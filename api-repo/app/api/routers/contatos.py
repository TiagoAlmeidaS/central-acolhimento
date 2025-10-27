"""Contact CRUD endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.schemas.contato import ContatoCreate, ContatoUpdate, ContatoOut
from app.services.crud_service import ContatoService

router = APIRouter(prefix="/contatos", tags=["contatos"])


@router.post(
    "/",
    response_model=ContatoOut,
    status_code=201,
    summary="Cadastrar novo contato",
    description="""
Cadastra um novo contato. Suporta duas modalidades:

**1. Extração via LLM** (texto livre):
```json
{
  "texto_livre": "Novo contato: Maria Silva, telefone 11-9999-8888, motivo: apoio emocional"
}
```

**2. Cadastro manual** (campos explícitos):
```json
{
  "nome": "João Silva",
  "telefone": "11-8888-7777",
  "email": "joao@example.com",
  "motivo": "orientação jurídica"
}
```

**Nota**: Se LLM estiver indisponível, será exigido cadastro manual.
    """,
    responses={
        201: {"description": "Contato criado com sucesso"},
        422: {"description": "Validação falhou ou LLM indisponível"},
        500: {"description": "Erro interno do servidor"},
    },
)
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


@router.get(
    "/",
    response_model=List[ContatoOut],
    summary="Listar contatos",
    description="""
Lista todos os contatos com paginação e filtros opcionais.

**Parâmetros de query:**
- `skip`: Número de registros a pular (paginação)
- `limit`: Número máximo de registros a retornar (1-1000)
- `motivo`: Filtrar por motivo do contato (busca parcial)
- `status_mcp`: Filtrar por status de sincronização MCP

**Exemplos:**
- `/contatos?skip=0&limit=20` - Primeira página
- `/contatos?motivo=apoio+emocional` - Filtrar por motivo
- `/contatos?status_mcp=sincronizado` - Contatos já sincronizados
    """,
)
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