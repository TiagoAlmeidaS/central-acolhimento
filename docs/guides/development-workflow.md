# Development Workflow - Central de Acolhimento

## Git Workflow

### Branch Strategy
```bash
main              # Production-ready code
├── develop       # Integration branch
└── feature/*     # Feature branches
```

### Naming Conventions
- **Feature branches**: `feature/nome-da-funcionalidade`
- **Bugfix branches**: `fix/nome-do-bug`
- **Hotfix branches**: `hotfix/descricao-urgente`

### Commit Messages (Conventional Commits)
```bash
feat: add MCP client integration
fix: resolve LLM timeout issue
docs: update API documentation
refactor: reorganize service layer
test: add integration tests for CRUD
chore: update dependencies
```

### Pull Request Process
1. Create feature branch from `develop`
2. Make changes and commit with conventional commits
3. Push branch and create PR targeting `develop`
4. Code review required (at least 1 approval)
5. CI/CD pipeline must pass (tests, linting, type-checking)
6. Squash merge to `develop`

## Code Quality

### Pre-commit Hooks
```bash
# Install hooks
pip install pre-commit
pre-commit install

# Run manually
pre-commit run --all-files
```

### Linting & Formatting
```bash
# Format with Black
black app/ tests/

# Lint with Ruff
ruff check app/ tests/
ruff format app/ tests/

# Type check with mypy
mypy app/
```

### Running Tests
```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# With coverage
pytest tests/ -v --cov=app --cov-report=html

# Specific test file
pytest tests/unit/test_crud.py -v
```

## Development Environment

### Local Setup
```bash
# 1. Clone repository
git clone <repo-url>
cd central-acolhimento

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment variables
cp .env.example .env
# Edit .env with local configuration

# 5. Run migrations
alembic upgrade head

# 6. Start development server
uvicorn app.main:app --reload
```

### Docker Compose Development
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api
docker-compose logs -f llm

# Stop services
docker-compose down
```

## Code Review Checklist

### Before Submitting PR
- [ ] Code follows PEP 8 and Black formatting
- [ ] Type hints added to all function signatures
- [ ] Docstrings added (Google style)
- [ ] Tests written and passing (coverage >80%)
- [ ] Linting passes (ruff, mypy)
- [ ] Documentation updated
- [ ] No secrets/credentials committed
- [ ] Migration files included (if DB changes)

### Reviewer Checklist
- [ ] Code is readable and maintainable
- [ ] Business logic is correct
- [ ] Error handling is appropriate
- [ ] Security considerations addressed
- [ ] Performance is acceptable
- [ ] Tests are comprehensive
- [ ] Documentation is updated

## Debugging

### FastAPI Debugging
```bash
# Run with debug mode
uvicorn app.main:app --reload --log-level debug

# Enable debug toolbar (optional)
# Add to app/main.py: from starlette.middleware import Middleware
```

### Database Debugging
```bash
# Check SQLAlchemy queries
# Set SQLALCHEMY_ECHO=True in config
export SQLALCHEMY_ECHO=true

# Alembic debugging
alembic history
alembic current
alembic downgrade -1  # Rollback last migration
```

### LLM Debugging
```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Test LLM directly
curl http://localhost:11434/api/generate -d '{"model": "llama3", "prompt": "Test"}'
```

## Hot Reload Development

### FastAPI Auto-reload
```bash
# Start with auto-reload (watches for file changes)
uvicorn app.main:app --reload
```

### Docker Compose Hot Reload
```yaml
# In docker-compose.yml
services:
  api:
    volumes:
      - ./app:/app  # Mount local code into container
```

## Environment Variables

### Development (.env.local)
```env
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=DEBUG
DATABASE_URL=sqlite:///./database.db
LLM_URL=http://localhost:11434
```

### Staging (.env.staging)
```env
ENVIRONMENT=staging
DEBUG=False
LOG_LEVEL=INFO
DATABASE_URL=postgresql://user:pass@host:5432/dbname
LLM_URL=http://llm-service:11434
SECRET_KEY=staging-secret-key
```

## Testing Strategy

### Unit Tests
- Test individual functions/methods in isolation
- Use mocks for external dependencies (LLM, DB)
- Fast execution (<1s per test)

### Integration Tests
- Test API endpoints with real database (SQLite in-memory)
- Test MCP client with mocked LLM responses
- Slower execution (>1s per test)

### E2E Tests (Future)
- Test full flow: API → LLM → DB
- Run against actual Ollama service
- Very slow execution (>10s per test)

## Performance Monitoring

### Locust Load Testing
```bash
# Install
pip install locust

# Run
locust -f tests/locustfile.py --host http://localhost:8000
# Open browser to http://localhost:8089
```

### Profiling
```python
# Add to app/main.py for profiling
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()
# ... run app ...
profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats()
```

## Troubleshooting

### Common Issues

**Issue**: Module not found
```bash
# Solution: Ensure PYTHONPATH is set
export PYTHONPATH=$PWD
# Or activate virtual environment
source venv/bin/activate
```

**Issue**: Database locked
```bash
# Solution: Close other connections or use PostgreSQL
# SQLite doesn't support concurrent writes
```

**Issue**: LLM service unavailable
```bash
# Check Ollama is running
docker ps | grep ollama

# Restart LLM service
docker-compose restart llm
```

## Resources
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
