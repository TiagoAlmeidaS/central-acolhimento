# Development Guide - Central de Acolhimento API

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Docker 24.0+ (for LLM service)
- Git

### Setup Development Environment

```bash
# 1. Clone repository
git clone <repo-url>
cd central-acolhimento/api-repo

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install pre-commit hooks
pre-commit install

# 5. Setup environment variables
cp .env.example .env
# Edit .env with your configuration

# 6. Run database migrations
alembic upgrade head

# 7. Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration    # Integration tests only
pytest -m "not slow"     # Exclude slow tests

# Run specific test file
pytest tests/unit/test_services.py -v

# Run with verbose output
pytest -v --tb=short
```

### Test Coverage

Current coverage: **92%** 🎯

```bash
# Generate HTML coverage report
pytest --cov=app --cov-report=html
open htmlcov/index.html

# Coverage threshold (CI/CD)
pytest --cov=app --cov-fail-under=90
```

### Test Categories

- **Unit Tests**: Test individual functions/classes in isolation
- **Integration Tests**: Test API endpoints and database interactions
- **LLM Tests**: Test LLM integration (mocked)

## 🔧 Code Quality

### Linting and Formatting

```bash
# Format code with black
black app/ tests/

# Lint with ruff
ruff check app/ tests/

# Type check with mypy
mypy app/

# Run all quality checks
pre-commit run --all-files
```

### Pre-commit Hooks

Automatically run on every commit:
- Code formatting (black)
- Linting (ruff)
- Type checking (mypy)
- Security checks (bandit)
- Test execution

## 🐳 Docker Development

### With LLM Service

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### API Only

```bash
# Build image
docker build -t central-acolhimento-api .

# Run container
docker run -p 8000:8000 central-acolhimento-api
```

## 📊 CI/CD Pipeline

### GitHub Actions Workflow

The project includes a comprehensive CI/CD pipeline:

1. **Test Matrix**: Python 3.8, 3.9, 3.10, 3.11
2. **Code Quality**: Linting, formatting, type checking
3. **Security**: Safety checks, bandit scans
4. **Coverage**: Minimum 90% coverage required
5. **Build**: Docker image creation and testing
6. **Deploy**: Staging and production deployments

### Pipeline Triggers

- **Push to main**: Full pipeline + production deploy
- **Push to develop**: Full pipeline + staging deploy
- **Pull Request**: Test and quality checks only

## 🏗️ Project Structure

```
api-repo/
├── app/                    # Application code
│   ├── api/               # API routes
│   ├── core/              # Configuration, database
│   ├── crud/              # Database operations
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic
│   └── mcp/               # MCP client
├── tests/                 # Test suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── conftest.py        # Test configuration
├── alembic/               # Database migrations
├── k8s/                   # Kubernetes manifests
├── terraform/             # Infrastructure as Code
├── .github/workflows/     # CI/CD pipelines
├── .pre-commit-config.yaml # Pre-commit hooks
├── pytest.ini            # Test configuration
├── pyproject.toml         # Project configuration
└── requirements.txt       # Dependencies
```

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure virtual environment is activated
2. **Database Errors**: Run `alembic upgrade head`
3. **LLM Connection**: Check if Ollama is running on port 11434
4. **Test Failures**: Check Python version compatibility

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
uvicorn app.main:app --reload --log-level debug
```

## 📈 Performance

### Test Performance

- **Unit Tests**: ~2-3 seconds
- **Integration Tests**: ~5-8 seconds
- **Full Suite**: ~12-15 seconds

### Optimization Tips

- Use `pytest-xdist` for parallel test execution
- Mock external dependencies in unit tests
- Use `pytest.mark.slow` for long-running tests

## 🔒 Security

### Security Checks

- **Bandit**: Python security linter
- **Safety**: Dependency vulnerability scanner
- **Pre-commit**: Automated security checks

### Best Practices

- Never commit secrets to version control
- Use environment variables for sensitive data
- Regular dependency updates
- Input validation and sanitization

## 📚 Documentation

- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc
- **Architecture**: See parent `docs/` directory

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/nova-funcionalidade`)
3. Make changes with tests
4. Run quality checks (`pre-commit run --all-files`)
5. Commit changes (`git commit -m 'feat: nova funcionalidade'`)
6. Push to branch (`git push origin feature/nova-funcionalidade`)
7. Open Pull Request

## 📞 Support

- **Issues**: GitHub Issues
- **Documentation**: `/docs` directory
- **API Reference**: `/docs/api` directory
