# Prompt Engineering Guide - Llama3 8B

## Overview
Este guia documenta a estratégia de prompt engineering para extração de entidades usando Llama3:8b via Ollama.

## Entity Extraction Prompt Template

### Base Prompt
```python
ENTITY_EXTRACTION_PROMPT = """
Você é um assistente especializado em extrair informações estruturadas de texto livre.

Tarefa: Extraia as seguintes entidades do texto fornecido:
- nome: Nome completo da pessoa
- telefone: Número de telefone no formato brasileiro (XX) XXXXX-XXXX
- email: Email válido (opcional)
- motivo: Motivo do contato (apoio emocional, orientação jurídica, etc.)
- data: Data do contato se mencionada (formato YYYY-MM-DD)

Texto de entrada:
{text}

Instruções:
1. Extraia APENAS as entidades explicitamente mencionadas no texto
2. Se uma entidade não for mencionada, retorne null
3. Telefone deve estar no formato brasileiro: (XX) XXXXX-XXXX
4. Email deve ser válido (contendo @)
5. Retorne APENAS JSON válido, sem markdown, sem explicações

Formato de saída (JSON):
{
  "nome": "...",
  "telefone": "...",
  "email": "... ou null",
  "motivo": "...",
  "data": "... ou null"
}
"""
```

### Implementation
```python
# ollama/prompts.py
from jinja2 import Template

ENTITY_EXTRACTION_PROMPT = Template("""
Você é um assistente especializado em extrair informações estruturadas de texto livre.

Tarefa: Extraia as seguintes entidades do texto fornecido:
- nome: Nome completo da pessoa
- telefone: Número de telefone no formato brasileiro (XX) XXXXX-XXXX
- email: Email válido (opcional)
- motivo: Motivo do contato (apoio emocional, orientação jurídica, etc.)
- data: Data do contato se mencionada (formato YYYY-MM-DD)

Texto de entrada:
{{ text }}

Instruções:
1. Extraia APENAS as entidades explicitamente mencionadas no texto
2. Se uma entidade não for mencionada, retorne null
3. Telefone deve estar no formato brasileiro: (XX) XXXXX-XXXX
4. Email deve ser válido (contendo @)
5. Retorne APENAS JSON válido, sem markdown, sem explicações

Formato de saída (JSON):
{
  "nome": "...",
  "telefone": "...",
  "email": "... ou null",
  "motivo": "...",
  "data": "... ou null"
}
""")

def format_prompt(text: str) -> str:
    """Format prompt with input text"""
    return ENTITY_EXTRACTION_PROMPT.render(text=text)
```

## Examples

### Example 1: Complete Information
**Input**: "Novo contato: Maria Silva, telefone 11-9999-8888, email maria@example.com, motivo: apoio emocional, data 2024-01-15"

**Expected Output**:
```json
{
  "nome": "Maria Silva",
  "telefone": "11-9999-8888",
  "email": "maria@example.com",
  "motivo": "apoio emocional",
  "data": "2024-01-15"
}
```

### Example 2: Partial Information
**Input**: "Cadastrar: João, tel 11-8888-7777, orientação jurídica"

**Expected Output**:
```json
{
  "nome": "João",
  "telefone": "11-8888-7777",
  "email": null,
  "motivo": "orientação jurídica",
  "data": null
}
```

### Example 3: Missing Critical Fields
**Input**: "Marcar consulta para Maria"

**Expected Output**:
```json
{
  "nome": "Maria",
  "telefone": null,
  "email": null,
  "motivo": null,
  "data": null
}
```

**Validation**: Reject this extraction (critical fields missing)

## Prompt Patterns

### Pattern 1: Direct Explicit
```
Input: "Nome: João Silva, Telefone: 11-8888-7777"
Output: Extracts "João Silva" as nome, "11-8888-7777" as telefone
```

### Pattern 2: Informal
```
Input: "Oi, sou o João, meu tel é 11-8888-7777"
Output: Extracts "João" as nome, "11-8888-7777" as telefone
```

### Pattern 3: Variation (Telefone)
```
Input: "11 8888-7777" or "(11) 8888-7777" or "+55 11 8888-7777"
Expected Output: Normalize to "11-8888-7777"
```

### Pattern 4: Email Detection
```
Input: "Email: maria@example.com" or "maria [at] example [dot] com"
Output: Extracts "maria@example.com" as email
```

## Validation Post-Extraction

```python
import re
from typing import Optional

def validate_phone(phone: str) -> Optional[str]:
    """Validate and normalize Brazilian phone number"""
    # Remove non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Brazilian phone: 10 or 11 digits
    if len(digits) == 10 or len(digits) == 11:
        if len(digits) == 11:
            digits = digits[1:]  # Remove country code
        # Format: (XX) XXXXX-XXXX
        return f"{digits[0:2]}-{digits[2:7]}-{digits[7:]}"
    
    return None

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_extraction(entities: dict) -> bool:
    """Validate extracted entities"""
    # At minimum, nome and telefone are required
    if not entities.get("nome") or not entities.get("telefone"):
        return False
    
    # Validate phone format
    if not validate_phone(entities["telefone"]):
        return False
    
    # Validate email if present
    if entities.get("email") and not validate_email(entities["email"]):
        return False
    
    return True
```

## Prompt Engineering Best Practices

### 1. Be Explicit and Specific
```python
# BAD: "Extract information from text"
# GOOD: "Extract nome, telefone, email, motivo from text and return JSON"
```

### 2. Provide Examples
```python
prompt = f"""
Extract entities from: "Maria, tel 11-9999-8888, motivo: apoio"

Expected output:
{{"nome": "Maria", "telefone": "11-9999-8888", "motivo": "apoio"}}

Now extract from: {user_input}
"""
```

### 3. Specify Output Format
```python
# Always specify exact JSON format
prompt += """
Return ONLY valid JSON:
{
  "nome": "...",
  "telefone": "...",
  "email": "..." or null,
  "motivo": "...",
  "data": "..." or null
}
"""
```

### 4. Handle Edge Cases
```python
# Handle cases where information is missing
prompt += """
If entity is not mentioned, return null (not empty string or empty object).
If unsure, return null rather than guessing.
"""
```

## Confidence Scores (Future Enhancement)

```python
# Future: Request LLM to provide confidence scores
prompt += """
For each extracted entity, provide confidence score (0.0 to 1.0):
{
  "nome": "Maria",
  "nome_confidence": 0.95,
  "telefone": "11-9999-8888",
  "telefone_confidence": 0.90
}
"""
```

## Testing Prompts

### Test Dataset
```python
test_cases = [
    {
        "input": "Novo contato: Maria Silva, telefone 11-9999-8888, motivo: apoio emocional",
        "expected": {
            "nome": "Maria Silva",
            "telefone": "11-9999-8888",
            "email": None,
            "motivo": "apoio emocional",
            "data": None
        }
    },
    # ... more test cases
]

def test_prompt_accuracy():
    """Test prompt accuracy on test dataset"""
    correct = 0
    total = len(test_cases)
    
    for test_case in test_cases:
        result = await extract_entities(test_case["input"])
        if matches_expected(result, test_case["expected"]):
            correct += 1
    
    accuracy = correct / total
    assert accuracy > 0.90, f"Accuracy {accuracy} below threshold 0.90"
```

## Performance Optimization

### Prompt Caching
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_extraction(text: str) -> dict:
    """Cache LLM extractions for identical inputs"""
    return await extract_entities(text)
```

### Batch Processing (Future)
```python
async def batch_extract(texts: list[str]) -> list[dict]:
    """Extract entities from multiple texts in batch"""
    # Future: Send batch request to LLM
    results = []
    for text in texts:
        entities = await extract_entities(text)
        results.append(entities)
    return results
```

## References
- `llm/ollama/prompts.py` - Prompt templates
- `llm/extraction/llm_extractor.py` - Extraction logic
- `llm/extraction/validators.py` - Post-extraction validation
