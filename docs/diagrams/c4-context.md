# C4 Level 1: System Context Diagram

## Context Diagram

```mermaid
graph TB
    User[Atendente]
    API[Central de Acolhimento API]
    LLM[LLM Service]
    DB[(SQLite/PostgreSQL)]
    
    User -->|HTTPS/REST| API
    API -->|SQLAlchemy| DB
    API -.->|HTTP/MCP Protocol| LLM
    
    style User fill:#e1f5ff
    style API fill:#c3e6cb
    style LLM fill:#fff4e6
    style DB fill:#ffe6e6
```

## Diagram Description

### Actors
- **Atendente**: Usuário principal que cadastra contatos via API REST

### System
- **Central de Acolhimento API**: Sistema principal que expõe endpoints REST para CRUD de contatos

### External Systems
- **LLM Service**: Serviço externo (containerizado) que processa linguagem natural para extração de entidades
- **SQLite/PostgreSQL**: Banco de dados para persistência de contatos

### Relationships
- Atendente → API: Comunicação HTTPS/REST para cadastrar e consultar contatos
- API → DB: Operações CRUD via SQLAlchemy ORM
- API → LLM: Comunicação HTTP usando Model Context Protocol (MCP) para extração de entidades

## Notes
- LLM service é containerizado separadamente (via Docker)
- Comunicação API ↔ LLM é assíncrona via HTTP
- Database pode ser SQLite (dev) ou PostgreSQL (produção)
