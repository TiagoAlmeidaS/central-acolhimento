"""Contact CRUD endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.schemas.contato import ContatoCreate, ContatoUpdate, ContatoOut

router = APIRouter(prefix="/contatos", tags=["contatos"])


@router.post("/", response_model=ContatoOut, status_code=201)
async def create_contato(
    data: ContatoCreate,
    db: Session = Depends(get_db)
):
    """Create a new contact (via LLM extraction or manual input)."""
    # TODO: Implement LLM extraction logic
    # TODO: Implement CRUD service
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.get("/", response_model=List[ContatoOut])
async def list_contatos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """List all contacts with pagination."""
    # TODO: Implement list logic
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.get("/{id}", response_model=ContatoOut)
async def get_contato(id: int, db: Session = Depends(get_db)):
    """Get a specific contact by ID."""
    # TODO: Implement get logic
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.put("/{id}", response_model=ContatoOut)
async def update_contato(
    id: int,
    data: ContatoUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing contact."""
    # TODO: Implement update logic
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.delete("/{id}", status_code=204)
async def delete_contato(id: int, db: Session = Depends(get_db)):
    """Delete a contact."""
    # TODO: Implement delete logic
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.get("/export/excel")
async def export_to_excel(db: Session = Depends(get_db)):
    """Export contacts to Excel file."""
    # TODO: Implement export logic
    raise HTTPException(status_code=501, detail="Not implemented yet")
