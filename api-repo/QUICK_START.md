# Quick Start - Central de Acolhimento API

## 🚀 Início Rápido

### Opção 1: Docker Compose (Recomendado)

```bash
# 1. Clone o repositório (se ainda não fez)
git clone <repo-url>
cd central-acolhimento/api-repo

# 2. Inicie todos os serviços
docker-compose up -d

# 3. Aguarde a inicialização (30-60s para LLM baixar modelo)
docker-compose logs -f llm

# 4. Acesse a API
# Swagger UI: http://localhost:8000/docs
# API: http://localhost:8000
```

### Opção 2: Setup Local (Desenvolvimento)

```bash
# 1. Crie virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Instale dependências
pip install -r requirements.txt

# 3. Inicie LLM separadamente
docker run -d -p 11434:11434 ollama/ollama
docker exec <container-id> ollama pull llama3:8b

# 4. Execute migrations
alembic upgrade head

# 5. Inicie a API
uvicorn app.main:app --reload
```

## 📖 Usando a API

### Swagger UI (Recomendado)

Acesse **http://localhost:8000/docs** para:
- Testar todos os endpoints
- Ver exemplos de requests/responses
- Executar chamadas interativas

### cURL Examples

#### 1. Cadastrar contato via LLM
```bash
curl -X POST http://localhost:8000/api/v1/contatos \
  -H "Content-Type: application/json" \
  -d '{
    "texto_livre": "Novo contato: Maria Silva, telefone 11-9999-8888, motivo: apoio emocional"
  }'
```

#### 2. Cadastrar contato manual
```bash
curl -X POST http://localhost:8000/api/v1/contatos \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "João Silva",
    "telefone": "11-8888-7777",
    "email": "joao@example.com",
    "motivo": "orientação jurídica"
  }'
```

#### 3. Listar todos os contatos
```bash
curl http://localhost:8000/api/v1/contatos
```

#### 4. Obter contato específico
```bash
curl http://localhost:8000/api/v1/contatos/1
```

#### 5. Atualizar contato
```bash
curl -X PUT http://localhost:8000/api/v1/contatos/1 \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Maria Silva Atualizada"
  }'
```

#### 6. Deletar contato
```bash
curl -X DELETE http://localhost:8000/api/v1/contatos/1
```

#### 7. Exportar para Excel
```bash
curl -O http://localhost:8000/api/v1/contatos/export/excel
```

## 🧪 Rodar Testes

```bash
# Todos os testes
pytest

# Apenas unit tests
pytest tests/unit/

# Apenas integration tests
pytest tests/integration/

# Com coverage
pytest --cov=app --cov-report=html

# Ver relatório
# Abra htmlcov/index.html no navegador
```

## 🐛 Troubleshooting

### LLM não está respondendo
```bash
# Verificar se Ollama está rodando
curl http://localhost:11434/api/tags

# Ver logs
docker-compose logs llm

# Reiniciar serviço
docker-compose restart llm
```

### Erro de conexão com banco
```bash
# Verificar database file
ls -lh database.db

# Recriar database
rm database.db
alembic upgrade head
```

### API retorna 500
```bash
# Ver logs
docker-compose logs api

# Verificar dependências
pip list
```

## 📊 Monitoramento

### Health Check
```bash
curl http://localhost:8000/health
```

### Ready Check
```bash
curl http://localhost:8000/ready
```

### Métricas Prometheus (quando configurado)
```bash
curl http://localhost:8000/metrics
```

## 🎯 Próximos Passos

1. ✅ Teste a API via Swagger UI
2. ✅ Cadastre alguns contatos de exemplo
3. ✅ Teste extração LLM vs cadastro manual
4. ✅ Exporte dados para Excel
5. ⏭️ Configure ambiente de produção (Kubernetes)
6. ⏭️ Implemente autenticação JWT
7. ⏭️ Adicione logging estruturado
8. ⏭️ Configure CI/CD pipeline

## 📚 Documentação Completa

- **Arc42 Architecture**: `docs/arc42/`
- **API Specs**: `docs/api/`
- **Getting Started**: `docs/guides/getting-started.md`
- **Development Workflow**: `docs/guides/development-workflow.md`
- **Testing Strategy**: `docs/guides/testing-strategy.md`
