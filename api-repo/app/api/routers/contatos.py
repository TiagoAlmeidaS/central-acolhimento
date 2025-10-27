"""Contact CRUD endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.schemas.contato import ContatoCreate, ContatoUpdate, ContatoOut
from app.services.crud_service import ContatoService

router = APIRouter(prefix="/contatos", tags=["contatos"])


@router.post("/", response_model=ContatoOut, status_code=201)
async def create_contato(
    data: ContatoCreate,
    db: Session = Depends(get_db)
):
    """Create a new contact (via LLM extraction or manual input)."""
    try:
        service = ContatoService()
        return await service.create_contato(db, data)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.get("/", response_model=List[ContatoOut])
async def list_contatos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    motivo: Optional[str] = None,
    status_mcp: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all contacts with pagination and filters."""
    service = ContatoService()
    return service.list_contatos(db, skip, limit, motivo, status_mcp)


@router.get("/{id}", response_model=ContatoOut)
async def get_contato(id: int, db: Session = Depends(get_db)):
    """Get a specific contact by ID."""
    service = ContatoService()
    contato = service.get_contato(db, id)
    if not contato:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contato


@router.put("/{id}", response_model=ContatoOut)
async def update_contato(
    id: int,
    data: ContatoUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing contact."""
    service = ContatoService()
    try:
        contato = service.update_contato(db, id, data)
        if not contato:
            raise HTTPException(status_code=404, detail="Contact not found")
        return contato
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.delete("/{id}", status_code=204)
async def delete_contato(id: int, db: Session = Depends(get_db)):
    """Delete a contact."""
    service = ContatoService()
    success = service.delete_contato(db, id)
    if not success:
        raise HTTPException(status_code=404, detail="Contact not found")


@router.get("/export/excel")
async def export_to_excel(db: Session = Depends(get_db)):
    """Export contacts to Excel file."""
    service = ContatoService()
    excel_data = service.export_to_excel(db)
    
    return Response(
        content=excel_data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=contatos.xlsx"
        }
    )