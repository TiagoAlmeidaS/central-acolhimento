# Testing Strategy - Central de Acolhimento

## Overview

Testing strategy focuses on maintaining >80% code coverage while ensuring reliability and correctness of LLM integration, API endpoints, and database operations.

## Testing Pyramid

```
        ┌──────────────┐
        │   E2E Tests  │  (Future: 5-10 tests)
        │  (Optional)  │
        ├──────────────┤
        │  Integration │  (30-50 tests)
        │     Tests    │
        ├──────────────┤
        │  Unit Tests  │  (100+ tests)
        │              │
        └──────────────┘
```

### Coverage Target: >80%

- **Unit Tests**: 100+ tests, fast (<1s each)
- **Integration Tests**: 30-50 tests, medium speed (<5s each)
- **E2E Tests**: 5-10 tests, slow (>10s each) - optional

## Unit Tests

### Location: `tests/unit/`

### Scope
Test individual functions and methods in isolation.

### Example: Testing CRUD Service

```python
# tests/unit/test_crud_service.py
import pytest
from unittest.mock import Mock, patch
from app.services.crud_service import ContatoService
from app.models.contato import Contato

def test_create_contato_success():
    """Test successful contact creation."""
    # Arrange
    mock_db = Mock()
    service = ContatoService()
    
    # Act
    result = service.create_contato(
        db=mock_db,
        data={"nome": "Test", "telefone": "11-9999-8888"}
    )
    
    # Assert
    assert result.nome == "Test"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()

def test_create_contato_duplicate_phone():
    """Test contact creation with duplicate phone."""
    # Arrange
    mock_db = Mock()
    service = ContatoService()
    # Mock existing contact
    mock_db.query.return_value.filter.return_value.first.return_value = Contato(...)
    
    # Act & Assert
    with pytest.raises(ValueError, match="duplicate"):
        service.create_contato(mock_db, data={...})
```

### Mocking External Dependencies

```python
# Mock LLM client
@patch('app.services.llm_integration.LLMIntegration')
def test_extract_entities(mock_llm):
    """Test entity extraction with mocked LLM."""
    mock_llm.extract_entities.return_value = {
        "nome": "Maria Silva",
        "telefone": "11-9999-8888"
    }
    
    service = ContatoService()
    result = service.create_contato(...)
    
    assert result.nome == "Maria Silva"
```

### Running Unit Tests
```bash
pytest tests/unit/ -v --cov=app --cov-report=term-missing
```

## Integration Tests

### Location: `tests/integration/`

### Scope
Test API endpoints with real database (SQLite in-memory or test DB).

### Example: Testing API Endpoints

```python
# tests/integration/test_api_contatos.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)

@pytest.fixture
def db_session():
    """Create test database session."""
    # Use SQLite in-memory database
    yield SessionLocal()

def test_create_contato_integration(client, db_session):
    """Test creating contact via API."""
    response = client.post(
        "/api/v1/contatos",
        json={
            "nome": "Test User",
            "telefone": "11-9999-8888",
            "motivo": "test"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["nome"] == "Test User"
```

### Database Fixtures

```python
@pytest.fixture(autouse=True)
def setup_database():
    """Setup test database before each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
```

### Running Integration Tests
```bash
pytest tests/integration/ -v
```

## E2E Tests (Future)

### Location: `tests/e2e/`

### Scope
Test full system with real LLM service.

### Example: Full Flow Test

```python
# tests/e2e/test_e2e_flow.py
@pytest.mark.e2e
def test_full_contact_lifecycle(docker_compose):
    """Test full contact lifecycle with LLM."""
    # Start services
    # Create contact via LLM
    # Verify extraction
    # Export to Excel
    pass
```

### Running E2E Tests
```bash
# Requires LLM service running
pytest tests/e2e/ -v --e2e
```

## LLM Integration Testing

### Mocking LLM Responses

```python
# tests/fixtures/mock_llm.py
@pytest.fixture
def mock_llm_response():
    """Mock LLM extraction response."""
    return {
        "entities": {
            "nome": "Maria Silva",
            "telefone": "11-9999-8888",
            "motivo": "apoio emocional"
        }
    }
```

### Testing Prompt Engineering

```python
def test_prompt_template(mock_llm):
    """Test LLM prompt produces expected format."""
    prompt = build_prompt("Novo contato: João, tel 11-8888-7777")
    result = mock_llm.generate(prompt)
    
    assert "nome" in result
    assert "telefone" in result
    assert result["nome"] == "João"
```

## Database Testing

### Migrations Testing

```python
def test_migration_forward_and_backward():
    """Test migration can be applied and rolled back."""
    # Forward
    alembic.upgrade("head")
    
    # Backward
    alembic.downgrade("-1")
    
    # Forward again
    alembic.upgrade("head")
```

## Performance Testing

### Load Testing with Locust

```python
# tests/locustfile.py
from locust import HttpUser, task, between

class ContatoAPIUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def create_contato(self):
        self.client.post(
            "/api/v1/contatos",
            json={"nome": "Test", "telefone": "11-9999-8888"}
        )
    
    @task(3)
    def list_contatos(self):
        self.client.get("/api/v1/contatos")
```

### Running Load Tests
```bash
locust -f tests/locustfile.py --host http://localhost:8000
```

## Test Coverage

### Generating Coverage Report
```bash
pytest --cov=app --cov-report=html
# Open htmlcov/index.html
```

### Coverage Thresholds
- **Overall**: >80%
- **Critical paths**: >90% (LLM integration, CRUD operations)
- **Business logic**: >85%
- **Routers/API**: >75% (some edge cases acceptable)

## CI/CD Integration

### GitHub Actions
```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - run: pip install -r requirements.txt
    - run: pytest --cov=app --cov-report=xml
    - run: coverage report --fail-under=80
```

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Fast Tests**: Unit tests should run in <1 second
3. **Deterministic**: Tests should produce same results every time
4. **Clear Assertions**: Use descriptive assert messages
5. **Mock External**: Mock LLM, external APIs, file I/O
6. **Test Happy Path**: Test success scenarios first
7. **Test Error Cases**: Test failure scenarios (validation, timeouts)
8. **Cover Edge Cases**: Test boundary conditions, empty inputs, null values

## Test Organization

```
tests/
├── unit/
│   ├── test_models.py
│   ├── test_schemas.py
│   ├── test_crud.py
│   ├── test_services.py
│   └── test_mcp_client.py
├── integration/
│   ├── test_api_contatos.py
│   ├── test_api_health.py
│   └── test_api_export.py
├── e2e/            # Future
│   └── test_full_flow.py
├── fixtures/
│   ├── mock_llm.py
│   └── mock_db.py
└── locustfile.py
```

## Running Tests

### All Tests
```bash
pytest
```

### Specific Category
```bash
pytest tests/unit/
pytest tests/integration/
```

### With Coverage
```bash
pytest --cov=app --cov-report=html
```

### Watch Mode
```bash
pytest-watch
```

## Troubleshooting

### Issue: LLM Tests Fail
```bash
# Mock LLM instead of using real service
# Use fixtures/mock_llm.py
```

### Issue: Database Tests Conflict
```bash
# Use separate test database
DATABASE_URL=sqlite:///./test.db
```

### Issue: Slow Tests
```bash
# Run tests in parallel
pytest -n auto
```

## Resources
- [Pytest Documentation](https://docs.pytest.org/)
- [Testing FastAPI](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/14/tutorial/testing.html)
