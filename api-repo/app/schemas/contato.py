"""Pydantic schemas for Contato."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ContatoBase(BaseModel):
    """Base schema for Contato."""

    nome: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    motivo: Optional[str] = None


class ContatoCreate(ContatoBase):
    """Schema for creating a new contact."""

    texto_livre: Optional[str] = Field(None, description="Free text for LLM extraction")

    class Config:
        from_attributes = True


class ContatoUpdate(ContatoBase):
    """Schema for updating an existing contact."""

    pass


class ContatoOut(ContatoBase):
    """Schema for contact output."""

    id: int
    nome: str
    telefone: str
    email: Optional[str] = None
    motivo: str
    data_cadastro: datetime
    status_mcp: str
    mcp_synced_at: Optional[datetime] = None
    extra_data: Optional[dict] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
