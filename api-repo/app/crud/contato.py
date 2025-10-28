"""Contact CRUD operations."""

from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.contato import Contato


class ContatoRepository:
    """Repository pattern for contact database operations."""

    @staticmethod
    def create(db: Session, contato_data: dict) -> Contato:
        """Create a new contact."""
        db_contato = Contato(**contato_data)
        db.add(db_contato)
        db.commit()
        db.refresh(db_contato)
        return db_contato

    @staticmethod
    def get(db: Session, contato_id: int) -> Optional[Contato]:
        """Get contact by ID."""
        return db.query(Contato).filter(Contato.id == contato_id).first()

    @staticmethod
    def get_by_telefone(db: Session, telefone: str) -> Optional[Contato]:
        """Get contact by phone number."""
        return db.query(Contato).filter(Contato.telefone == telefone).first()

    @staticmethod
    def list_all(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        motivo: Optional[str] = None,
        status_mcp: Optional[str] = None,
    ) -> List[Contato]:
        """List all contacts with optional filters."""
        query = db.query(Contato)

        if motivo:
            query = query.filter(Contato.motivo.contains(motivo))
        if status_mcp:
            query = query.filter(Contato.status_mcp == status_mcp)

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, contato_id: int, contato_data: dict) -> Optional[Contato]:
        """Update an existing contact."""
        db_contato = db.query(Contato).filter(Contato.id == contato_id).first()
        if not db_contato:
            return None

        for field, value in contato_data.items():
            if value is not None:
                setattr(db_contato, field, value)

        db.commit()
        db.refresh(db_contato)
        return db_contato

    @staticmethod
    def delete(db: Session, contato_id: int) -> bool:
        """Delete a contact."""
        db_contato = db.query(Contato).filter(Contato.id == contato_id).first()
        if not db_contato:
            return False

        db.delete(db_contato)
        db.commit()
        return True

    @staticmethod
    def count(db: Session) -> int:
        """Count total contacts."""
        return db.query(Contato).count()
