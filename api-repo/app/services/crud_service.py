"""Business logic for CRUD operations."""

from typing import Optional
from sqlalchemy.orm import Session

from app.schemas.contato import ContatoCreate, ContatoUpdate, ContatoOut
from app.crud.contato import ContatoRepository
from app.services.llm_integration import LLMIntegration
from app.core.config import settings


class ContatoService:
    """Service layer for contact operations with LLM integration."""

    def __init__(self):
        self.repository = ContatoRepository()
        self.llm = LLMIntegration()

    async def create_contato(
        self,
        db: Session,
        data: ContatoCreate
    ) -> ContatoOut:
        """Create a new contact, optionally extracting entities via LLM."""
        # Check for duplicate phone
        existing = self.repository.get_by_telefone(db, data.telefone or "")
        if existing:
            raise ValueError("Contact with this phone number already exists")

        # If texto_livre provided, extract entities via LLM
        if data.texto_livre and not data.nome:
            try:
                entities = await self.llm.extract_entities(data.texto_livre)
                contato_data = {
                    "nome": entities.get("nome"),
                    "telefone": entities.get("telefone"),
                    "email": entities.get("email"),
                    "motivo": entities.get("motivo"),
                    "metadata": entities,
                    "status_mcp": "pendente",
                }
            except Exception as e:
                # LLM unavailable, require manual input
                raise ValueError(
                    f"LLM extraction failed: {str(e)}. "
                    "Please provide explicit fields (nome, telefone, motivo)."
                )
        else:
            # Manual input with explicit fields
            if not all([data.nome, data.telefone, data.motivo]):
                raise ValueError("Nome, telefone and motivo are required")
            
            contato_data = {
                "nome": data.nome,
                "telefone": data.telefone,
                "email": data.email,
                "motivo": data.motivo,
            }

        # Create contact
        contato = self.repository.create(db, contato_data)
        return ContatoOut.model_validate(contato)

    def get_contato(self, db: Session, contato_id: int) -> Optional[ContatoOut]:
        """Get contact by ID."""
        contato = self.repository.get(db, contato_id)
        if not contato:
            return None
        return ContatoOut.model_validate(contato)

    def list_contatos(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        motivo: Optional[str] = None,
        status_mcp: Optional[str] = None
    ) -> list[ContatoOut]:
        """List all contacts with pagination and filters."""
        contatos = self.repository.list_all(db, skip, limit, motivo, status_mcp)
        return [ContatoOut.model_validate(c) for c in contatos]

    def update_contato(
        self,
        db: Session,
        contato_id: int,
        data: ContatoUpdate
    ) -> Optional[ContatoOut]:
        """Update an existing contact."""
        contato_data = data.model_dump(exclude_unset=True)
        
        # Check for duplicate phone if telefone is being updated
        if "telefone" in contato_data:
            existing = self.repository.get_by_telefone(db, contato_data["telefone"])
            if existing and existing.id != contato_id:
                raise ValueError("Contact with this phone number already exists")

        contato = self.repository.update(db, contato_id, contato_data)
        if not contato:
            return None
        return ContatoOut.model_validate(contato)

    def delete_contato(self, db: Session, contato_id: int) -> bool:
        """Delete a contact."""
        return self.repository.delete(db, contato_id)

    def export_to_excel(self, db: Session) -> bytes:
        """Export all contacts to Excel file."""
        import pandas as pd
        from io import BytesIO

        contatos = self.repository.list_all(db, limit=settings.EXPORT_MAX_RECORDS)
        
        # Convert to DataFrame
        data = {
            "ID": [c.id for c in contatos],
            "Nome": [c.nome for c in contatos],
            "Telefone": [c.telefone for c in contatos],
            "Email": [c.email or "" for c in contatos],
            "Motivo": [c.motivo for c in contatos],
            "Data Cadastro": [c.data_cadastro for c in contatos],
            "Status MCP": [c.status_mcp for c in contatos],
        }
        
        df = pd.DataFrame(data)
        
        # Export to Excel in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Contatos', index=False)
        
        output.seek(0)
        return output.getvalue()
