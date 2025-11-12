# API Bancária Assíncrona com FastAPI

Uma API RESTful assíncrona para gerenciar operações bancárias (depósitos e saques) com autenticação JWT, desenvolvida com FastAPI.

## Características

- ✅ **Autenticação JWT**: Segurança com tokens JSON Web Tokens
- ✅ **Gerenciamento de Contas**: Registro e autenticação de usuários
- ✅ **Operações Bancárias**: Depósitos e saques com validação
- ✅ **Extrato Detalhado**: Histórico completo de transações
- ✅ **Banco de Dados SQLite**: Persistência de dados
- ✅ **Documentação OpenAPI**: Swagger UI e ReDoc integrados
- ✅ **Validação de Dados**: Pydantic para validação robusta
- ✅ **Tratamento de Erros**: Respostas HTTP apropriadas

## Requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)

## Instalação

### 1. Clonar ou baixar o projeto

```bash
cd banco_fastapi
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

## Executar a API

### Opção 1: Arquivo único (main.py)

```bash
python main.py
```

### Opção 2: Com uvicorn diretamente

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

A API estará disponível em `http://localhost:8000`

## Documentação Interativa

Após iniciar a API, acesse:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Endpoints

### Autenticação

#### Registrar novo usuário
```http
POST /registrar
Content-Type: application/json

{
  "username": "joao",
  "password": "senha123",
  "email": "joao@example.com"
}
```

**Resposta (201):**
```json
{
  "id": 1,
  "username": "joao",
  "email": "joao@example.com",
  "saldo": 0.00
}
```

#### Login e obter token
```http
POST /token
Content-Type: application/x-www-form-urlencoded

username=joao&password=senha123
```

**Resposta (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Operações Bancárias

#### Realizar depósito
```http
POST /deposito
Authorization: Bearer {token}
Content-Type: application/json

{
  "valor": 100.00,
  "descricao": "Depósito inicial"
}
```

**Resposta (200):**
```json
{
  "id": 1,
  "usuario_id": 1,
  "tipo": "deposito",
  "valor": 100.00,
  "saldo_anterior": 0.00,
  "saldo_novo": 100.00,
  "data_hora": "2024-01-15T10:30:00",
  "descricao": "Depósito inicial"
}
```

#### Realizar saque
```http
POST /saque
Authorization: Bearer {token}
Content-Type: application/json

{
  "valor": 50.00,
  "descricao": "Saque para compras"
}
```

**Resposta (200):**
```json
{
  "id": 2,
  "usuario_id": 1,
  "tipo": "saque",
  "valor": 50.00,
  "saldo_anterior": 100.00,
  "saldo_novo": 50.00,
  "data_hora": "2024-01-15T10:35:00",
  "descricao": "Saque para compras"
}
```

#### Obter extrato
```http
GET /extrato
Authorization: Bearer {token}
```

**Resposta (200):**
```json
{
  "usuario_id": 1,
  "username": "joao",
  "saldo_atual": 50.00,
  "transacoes": [
    {
      "id": 2,
      "usuario_id": 1,
      "tipo": "saque",
      "valor": 50.00,
      "saldo_anterior": 100.00,
      "saldo_novo": 50.00,
      "data_hora": "2024-01-15T10:35:00",
      "descricao": "Saque para compras"
    },
    {
      "id": 1,
      "usuario_id": 1,
      "tipo": "deposito",
      "valor": 100.00,
      "saldo_anterior": 0.00,
      "saldo_novo": 100.00,
      "data_hora": "2024-01-15T10:30:00",
      "descricao": "Depósito inicial"
    }
  ]
}
```

### Informações do Usuário

#### Obter perfil do usuário
```http
GET /me
Authorization: Bearer {token}
```

**Resposta (200):**
```json
{
  "id": 1,
  "username": "joao",
  "email": "joao@example.com",
  "saldo": 50.00
}
```

## Estrutura do Projeto

### Arquivo Único (main.py)
Implementação completa da API em um único arquivo Python.

### Estrutura Modular

```
banco_fastapi/
├── main.py              # Arquivo único com toda a implementação
├── database.py          # Gerenciamento do banco de dados
├── security.py          # Autenticação e segurança JWT
├── schemas.py           # Modelos Pydantic
├── requirements.txt     # Dependências do projeto
└── README.md           # Este arquivo
```

## Validações Implementadas

### Operações Bancárias
- ✅ Valor deve ser positivo
- ✅ Saque não pode exceder o saldo disponível
- ✅ Transações registram saldo anterior e novo

### Autenticação
- ✅ Username único
- ✅ Senha mínima de 6 caracteres
- ✅ Token JWT com expiração
- ✅ Endpoints protegidos requerem autenticação

### Dados
- ✅ Validação de tipos com Pydantic
- ✅ Valores decimais com precisão de 2 casas
- ✅ Email opcional mas validado

## Códigos de Status HTTP

| Código | Descrição |
|--------|-----------|
| 200 | Sucesso |
| 201 | Criado com sucesso |
| 400 | Requisição inválida |
| 401 | Não autenticado |
| 404 | Não encontrado |
| 500 | Erro interno do servidor |

## Segurança

### Recomendações para Produção

1. **Alterar SECRET_KEY**: Mude a chave secreta em `security.py` ou `main.py`
   ```python
   SECRET_KEY = "gere-uma-chave-aleatoria-segura-aqui"
   ```

2. **Usar HTTPS**: Configure SSL/TLS em produção

3. **Variáveis de Ambiente**: Use `.env` para configurações sensíveis
   ```bash
   SECRET_KEY=sua-chave-secreta
   DATABASE_URL=postgresql://user:password@host/db
   ```

4. **CORS**: Configure CORS apropriadamente
   ```python
   from fastapi.middleware.cors import CORSMiddleware
   
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://seu-dominio.com"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

5. **Rate Limiting**: Implemente rate limiting para proteger contra abuso

6. **Logging**: Configure logging apropriado para auditoria

## Exemplo de Uso com cURL

```bash
# 1. Registrar novo usuário
curl -X POST "http://localhost:8000/registrar" \
  -H "Content-Type: application/json" \
  -d '{"username":"joao","password":"senha123","email":"joao@example.com"}'

# 2. Fazer login
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=joao&password=senha123"

# 3. Fazer depósito (substitua TOKEN pelo token obtido)
curl -X POST "http://localhost:8000/deposito" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"valor":100.00,"descricao":"Depósito inicial"}'

# 4. Obter extrato
curl -X GET "http://localhost:8000/extrato" \
  -H "Authorization: Bearer TOKEN"
```

## Exemplo de Uso com Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Registrar usuário
response = requests.post(
    f"{BASE_URL}/registrar",
    json={"username": "joao", "password": "senha123", "email": "joao@example.com"}
)
print(response.json())

# Login
response = requests.post(
    f"{BASE_URL}/token",
    data={"username": "joao", "password": "senha123"}
)
token = response.json()["access_token"]

# Fazer depósito
headers = {"Authorization": f"Bearer {token}"}
response = requests.post(
    f"{BASE_URL}/deposito",
    json={"valor": 100.00, "descricao": "Depósito inicial"},
    headers=headers
)
print(response.json())

# Obter extrato
response = requests.get(f"{BASE_URL}/extrato", headers=headers)
print(response.json())
```

## Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'fastapi'"
**Solução**: Instale as dependências
```bash
pip install -r requirements.txt
```

### Erro: "Address already in use"
**Solução**: Mude a porta
```bash
python main.py --port 8001
```

### Erro: "database is locked"
**Solução**: Aguarde alguns segundos e tente novamente. Considere usar PostgreSQL em produção.

## Licença

Este projeto é fornecido como exemplo educacional.

## Autor

Desenvolvido como exemplo de API Bancária com FastAPI.

## Suporte

Para dúvidas ou problemas, consulte a documentação do FastAPI em https://fastapi.tiangolo.com/
