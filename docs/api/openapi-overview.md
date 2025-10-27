# API Specification - Central de Acolhimento

## Overview
A API do Central de Acolhimento é uma REST API construída com FastAPI, expondo endpoints para CRUD de contatos com integração LLM via MCP.

## Base URL
- **Development**: `http://localhost:8000`
- **Production**: `https://api.central-acolhimento.com`

## Authentication
Autenticação via JWT tokens no header `Authorization: Bearer <token>`

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Content-Type
Todos os requests e responses usam `application/json`

## Endpoints Overview

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|----------------|
| POST | `/contatos` | Create contact (LLM or manual) | Yes |
| GET | `/contatos` | List all contacts | Yes |
| GET | `/contatos/{id}` | Get contact by ID | Yes |
| PUT | `/contatos/{id}` | Update contact | Yes |
| DELETE | `/contatos/{id}` | Delete contact | Yes (admin only) |
| GET | `/contatos/export/excel` | Export to Excel | Yes (admin only) |
| GET | `/health` | Health check | No |
| GET | `/ready` | Readiness probe | No |
| GET | `/metrics` | Prometheus metrics | No |

## Detailed Endpoint Specifications

### POST /contatos
Cria um novo contato, extraindo entidades via LLM ou permitindo entrada manual.

**Request Body (LLM extraction)**:
```json
{
  "texto_livre": "Novo contato: Maria Silva, telefone 11-9999-8888, motivo: apoio emocional"
}
```

**Request Body (Manual)**:
```json
{
  "nome": "Maria Silva",
  "telefone": "11-9999-8888",
  "email": "maria@example.com",
  "motivo": "apoio emocional"
}
```

**Response 201 Created**:
```json
{
  "id": 123,
  "nome": "Maria Silva",
  "telefone": "11-9999-8888",
  "email": "maria@example.com",
  "motivo": "apoio emocional",
  "data_cadastro": "2024-01-15T10:30:00Z",
  "status_mcp": "pendente",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Response 422 Unprocessable Entity**:
```json
{
  "error": {
    "code": "LLM_UNAVAILABLE",
    "message": "LLM service unavailable. Please provide explicit fields.",
    "fields_required": ["nome", "telefone", "motivo"]
  }
}
```

### GET /contatos
Lista todos os contatos com paginação e filtros opcionais.

**Query Parameters**:
- `skip` (int, default=0): Skip N records
- `limit` (int, default=100, max=1000): Limit results
- `motivo` (str, optional): Filter by motivo
- `status_mcp` (str, optional): Filter by MCP status
- `data_inicio` (date, optional): Filter by start date
- `data_fim` (date, optional): Filter by end date

**Example**:
```http
GET /contatos?skip=0&limit=20&motivo=apoio+emocional
```

**Response 200 OK**:
```json
{
  "total": 156,
  "skip": 0,
  "limit": 20,
  "data": [
    {
      "id": 1,
      "nome": "Maria Silva",
      "telefone": "11-9999-8888",
      ...
    },
    ...
  ]
}
```

### GET /contatos/{id}
Retorna um contato específico por ID.

**Response 200 OK**:
```json
{
  "id": 123,
  "nome": "Maria Silva",
  "telefone": "11-9999-8888",
  "email": "maria@example.com",
  "motivo": "apoio emocional",
  "data_cadastro": "2024-01-15T10:30:00Z",
  "status_mcp": "sincronizado",
  "mcp_synced_at": "2024-01-15T10:31:00Z",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:31:00Z"
}
```

**Response 404 Not Found**:
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Contact with ID 123 not found"
  }
}
```

### PUT /contatos/{id}
Atualiza um contato existente.

**Request Body**:
```json
{
  "nome": "Maria Silva da Silva",
  "telefone": "11-8888-7777",
  "motivo": "apoio emocional - atualizado"
}
```

**Response 200 OK**: Returns updated contact object

### DELETE /contatos/{id}
Remove um contato permanentemente (LGPD: right to deletion).

**Response 204 No Content** (successful deletion)

**Response 404 Not Found** (contact doesn't exist)

### GET /contatos/export/excel
Exporta todos os contatos para arquivo Excel.

**Query Parameters**:
- `format` (str, default="xlsx"): Output format (xlsx, csv, json)

**Response 200 OK**:
- Content-Type: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- Filename: `contatos_2024-01-15.xlsx`

## Schemas (Pydantic Models)

### ContatoCreate
```python
class ContatoCreate(BaseModel):
    texto_livre: Optional[str] = None  # For LLM extraction
    nome: Optional[str] = None         # Manual input (required if texto_livre not provided)
    telefone: Optional[str] = None    # Manual input (required if texto_livre not provided)
    email: Optional[str] = None       # Optional
    motivo: Optional[str] = None     # Manual input (required if texto_livre not provided)
```

### ContatoUpdate
```python
class ContatoUpdate(BaseModel):
    nome: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    motivo: Optional[str] = None
```

### ContatoOut
```python
class ContatoOut(BaseModel):
    id: int
    nome: str
    telefone: str
    email: Optional[str]
    motivo: str
    data_cadastro: datetime
    status_mcp: str
    mcp_synced_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
```

## Error Responses

All errors follow this format:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {}  // Optional additional context
  }
}
```

### Error Codes
- `VALIDATION_ERROR` (422): Invalid input data
- `NOT_FOUND` (404): Resource not found
- `UNAUTHORIZED` (401): Authentication required
- `FORBIDDEN` (403): Insufficient permissions
- `LLM_TIMEOUT` (504): LLM service timeout
- `LLM_UNAVAILABLE` (503): LLM service unavailable
- `DATABASE_ERROR` (500): Database operation failed
- `INTERNAL_ERROR` (500): Unexpected server error

## Swagger UI
Acesse `/docs` para Swagger UI interativo (FastAPI auto-generates):
```
http://localhost:8000/docs
```

## OpenAPI Specification
OpenAPI 3.1 specification disponível em `/openapi.json`:
```json
{
  "openapi": "3.1.0",
  "info": {
    "title": "Central de Acolhimento API",
    "version": "1.0.0"
  },
  "paths": {
    ...
  }
}
```

## Rate Limiting (Future)
- **Free tier**: 100 requests/hour
- **Premium**: 1000 requests/hour
- **Header**: `X-RateLimit-Remaining: 95`

## Pagination
Use `skip` and `limit` query parameters for pagination:
```http
GET /contatos?skip=0&limit=20    # First page
GET /contatos?skip=20&limit=20   # Second page
GET /contatos?skip=40&limit=20   # Third page
```

## Filtering
Filter by multiple fields:
```http
GET /contatos?motivo=apoio+emocional&status_mcp=sincronizado&data_inicio=2024-01-01
```

## Sorting (Future)
Sort by specific field:
```http
GET /contatos?sort_by=data_cadastro&sort_order=desc
```
