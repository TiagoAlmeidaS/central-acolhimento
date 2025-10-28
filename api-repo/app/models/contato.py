"""Contato database model."""


from sqlalchemy import Column, DateTime, Integer, String, JSON
from sqlalchemy.sql import func

from app.core.database import Base


class Contato(Base):
    """Contato model for database persistence."""

    __tablename__ = "contatos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False, index=True)
    telefone = Column(String, nullable=False, index=True)
    email = Column(String, nullable=True, index=True)
    motivo = Column(String, nullable=False)
    data_cadastro = Column(DateTime(timezone=True), server_default=func.now())
    status_mcp = Column(String, default="pendente")  # pendente, sincronizado, erro
    extra_data = Column(JSON, nullable=True)  # Extra data extracted by LLM
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self) -> str:
        """String representation."""
        return f"<Contato id={self.id} nome={self.nome} telefone={self.telefone}>"
