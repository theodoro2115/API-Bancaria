# Documentação Técnica - API Bancária com FastAPI

## 1. Visão Geral

A **API Bancária Assíncrona** é uma aplicação RESTful desenvolvida com FastAPI que gerencia operações bancárias básicas (depósitos e saques) com autenticação JWT e persistência de dados em SQLite.

### Objetivos Alcançados

✅ **Cadastro de Transações**: Registro de depósitos e saques com rastreamento de saldo  
✅ **Exibição de Extrato**: Endpoint que mostra todas as transações de uma conta  
✅ **Autenticação JWT**: Proteção de endpoints com tokens JSON Web Tokens  
✅ **Validação de Operações**: Validação de valores negativos e saldo insuficiente  
✅ **Documentação OpenAPI**: Swagger UI e ReDoc integrados automaticamente  

## 2. Arquitetura da Aplicação

### 2.1 Estrutura de Arquivos

```
banco_fastapi/
├── main.py                    # Implementação completa em um arquivo
├── database.py               # Gerenciamento do banco de dados
├── security.py               # Autenticação e segurança JWT
├── schemas.py                # Modelos Pydantic para validação
├── requirements.txt          # Dependências do projeto
├── test_api.py              # Script de testes e exemplos
├── README.md                # Documentação de uso
├── DOCUMENTACAO_TECNICA.md  # Este arquivo
├── .env.example             # Exemplo de variáveis de ambiente
├── .gitignore               # Arquivos a ignorar no Git
├── Dockerfile               # Containerização da aplicação
└── docker-compose.yml       # Orquestração com Docker
```

### 2.2 Camadas da Aplicação

#### Camada de Apresentação (FastAPI)
- Endpoints RESTful
- Validação automática com Pydantic
- Documentação OpenAPI automática
- Tratamento de erros HTTP

#### Camada de Autenticação (JWT)
- Geração de tokens
- Validação de credenciais
- Proteção de endpoints

#### Camada de Negócio
- Lógica de depósitos e saques
- Validações de operações
- Cálculo de saldos

#### Camada de Persistência (SQLite)
- Armazenamento de usuários
- Histórico de transações
- Integridade referencial

## 3. Modelos de Dados

### 3.1 Tabela: usuarios

```sql
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email TEXT,
    saldo DECIMAL(10, 2) DEFAULT 0.00,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**Campos:**
- `id`: Identificador único do usuário
- `username`: Nome de usuário (único)
- `password_hash`: Hash bcrypt da senha
- `email`: Email do usuário (opcional)
- `saldo`: Saldo atual da conta
- `data_criacao`: Data de criação da conta

### 3.2 Tabela: transacoes

```sql
CREATE TABLE transacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    tipo TEXT NOT NULL,
    valor DECIMAL(10, 2) NOT NULL,
    saldo_anterior DECIMAL(10, 2) NOT NULL,
    saldo_novo DECIMAL(10, 2) NOT NULL,
    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    descricao TEXT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
)
```

**Campos:**
- `id`: Identificador único da transação
- `usuario_id`: ID do usuário (chave estrangeira)
- `tipo`: "deposito" ou "saque"
- `valor`: Valor da transação
- `saldo_anterior`: Saldo antes da transação
- `saldo_novo`: Saldo após a transação
- `data_hora`: Data e hora da transação
- `descricao`: Descrição opcional

## 4. Modelos Pydantic

### 4.1 Token
```python
{
    "access_token": "string",
    "token_type": "bearer",
    "expires_in": 1800
}
```

### 4.2 UsuarioRegistro
```python
{
    "username": "string (3-50 chars)",
    "password": "string (min 6 chars)",
    "email": "string (optional)"
}
```

### 4.3 UsuarioResposta
```python
{
    "id": 1,
    "username": "joao",
    "email": "joao@example.com",
    "saldo": 100.50
}
```

### 4.4 OperacaoBancaria
```python
{
    "valor": 100.50,
    "descricao": "string (optional)"
}
```

### 4.5 Transacao
```python
{
    "id": 1,
    "usuario_id": 1,
    "tipo": "deposito",
    "valor": 100.50,
    "saldo_anterior": 0.00,
    "saldo_novo": 100.50,
    "data_hora": "2024-01-15T10:30:00",
    "descricao": "Depósito inicial"
}
```

### 4.6 Extrato
```python
{
    "usuario_id": 1,
    "username": "joao",
    "saldo_atual": 100.50,
    "transacoes": [
        { "id": 1, "tipo": "deposito", ... }
    ]
}
```

## 5. Endpoints da API

### 5.1 Autenticação

#### POST /registrar
**Descrição**: Registra um novo usuário  
**Autenticação**: Não requerida  
**Body**:
```json
{
    "username": "joao",
    "password": "senha123",
    "email": "joao@example.com"
}
```
**Resposta (200)**:
```json
{
    "id": 1,
    "username": "joao",
    "email": "joao@example.com",
    "saldo": 0.00
}
```

#### POST /token
**Descrição**: Realiza login e retorna token JWT  
**Autenticação**: Não requerida  
**Body** (form-data):
```
username=joao&password=senha123
```
**Resposta (200)**:
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 1800
}
```

### 5.2 Operações Bancárias

#### POST /deposito
**Descrição**: Realiza um depósito  
**Autenticação**: Requerida (Bearer token)  
**Body**:
```json
{
    "valor": 100.00,
    "descricao": "Depósito inicial"
}
```
**Resposta (200)**:
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

#### POST /saque
**Descrição**: Realiza um saque  
**Autenticação**: Requerida (Bearer token)  
**Body**:
```json
{
    "valor": 50.00,
    "descricao": "Saque para compras"
}
```
**Resposta (200)**:
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

#### GET /extrato
**Descrição**: Obtém o extrato da conta  
**Autenticação**: Requerida (Bearer token)  
**Resposta (200)**:
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

### 5.3 Informações do Usuário

#### GET /me
**Descrição**: Obtém informações do usuário atual  
**Autenticação**: Requerida (Bearer token)  
**Resposta (200)**:
```json
{
    "id": 1,
    "username": "joao",
    "email": "joao@example.com",
    "saldo": 50.00
}
```

#### GET /
**Descrição**: Informações da API  
**Autenticação**: Não requerida  
**Resposta (200)**:
```json
{
    "mensagem": "API Bancária Assíncrona com FastAPI",
    "versao": "1.0.0",
    "documentacao": "/docs",
    "documentacao_alternativa": "/redoc"
}
```

## 6. Fluxo de Autenticação

### 6.1 Geração de Token

```
1. Usuário envia credenciais (username + password) para /token
2. API valida as credenciais contra o banco de dados
3. Se válidas:
   - Cria um payload JWT com o username
   - Adiciona timestamp de expiração (30 minutos por padrão)
   - Assina o token com a SECRET_KEY usando algoritmo HS256
   - Retorna o token ao cliente
4. Se inválidas:
   - Retorna erro 401 Unauthorized
```

### 6.2 Validação de Token

```
1. Cliente envia requisição com header: Authorization: Bearer {token}
2. API extrai o token do header
3. Valida a assinatura usando SECRET_KEY
4. Verifica se o token não expirou
5. Extrai o username do payload
6. Busca o usuário no banco de dados
7. Se tudo válido:
   - Executa a operação solicitada
8. Se inválido:
   - Retorna erro 401 Unauthorized
```

## 7. Validações Implementadas

### 7.1 Validações de Entrada

| Campo | Validação | Erro |
|-------|-----------|------|
| username | 3-50 caracteres, único | 400 Bad Request |
| password | Mínimo 6 caracteres | 400 Bad Request |
| email | Formato de email (opcional) | 400 Bad Request |
| valor | Maior que 0, 2 casas decimais | 400 Bad Request |

### 7.2 Validações de Negócio

| Operação | Validação | Erro |
|----------|-----------|------|
| Depósito | Valor > 0 | 400 Bad Request |
| Saque | Valor > 0 e ≤ saldo | 400 Bad Request |
| Login | Username existe e senha correta | 401 Unauthorized |
| Endpoint protegido | Token válido e não expirado | 401 Unauthorized |

## 8. Tratamento de Erros

### 8.1 Códigos de Status HTTP

| Código | Descrição | Exemplo |
|--------|-----------|---------|
| 200 | OK - Requisição bem-sucedida | Depósito realizado |
| 201 | Created - Recurso criado | Usuário registrado |
| 400 | Bad Request - Dados inválidos | Valor negativo |
| 401 | Unauthorized - Não autenticado | Token inválido |
| 404 | Not Found - Recurso não encontrado | Usuário não existe |
| 500 | Internal Server Error | Erro no servidor |

### 8.2 Formato de Erro

```json
{
    "detail": "Descrição do erro"
}
```

## 9. Segurança

### 9.1 Criptografia de Senha

- **Algoritmo**: bcrypt
- **Rounds**: Padrão do passlib (12)
- **Armazenamento**: Hash da senha (nunca a senha em texto plano)

### 9.2 Token JWT

- **Algoritmo**: HS256 (HMAC com SHA-256)
- **Expiração**: 30 minutos (configurável)
- **Assinatura**: SECRET_KEY (deve ser alterada em produção)

### 9.3 Recomendações para Produção

1. **Alterar SECRET_KEY**: Use uma chave aleatória e segura
2. **HTTPS**: Configure SSL/TLS
3. **CORS**: Configure origens permitidas
4. **Rate Limiting**: Implemente limitação de requisições
5. **Logging**: Configure logging para auditoria
6. **Variáveis de Ambiente**: Use .env para configurações sensíveis
7. **Banco de Dados**: Considere PostgreSQL em vez de SQLite

## 10. Dependências

| Pacote | Versão | Propósito |
|--------|--------|----------|
| fastapi | 0.104.1 | Framework web |
| uvicorn | 0.24.0 | Servidor ASGI |
| pydantic | 2.5.0 | Validação de dados |
| python-jose | 3.3.0 | JWT |
| passlib | 1.7.4 | Hash de senhas |
| python-multipart | 0.0.6 | Parsing de formulários |
| sqlalchemy | 2.0.23 | ORM (opcional) |

## 11. Exemplos de Uso

### 11.1 Com cURL

```bash
# Registrar
curl -X POST "http://localhost:8000/registrar" \
  -H "Content-Type: application/json" \
  -d '{"username":"joao","password":"senha123"}'

# Login
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=joao&password=senha123"

# Depositar
curl -X POST "http://localhost:8000/deposito" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"valor":100.00}'

# Extrato
curl -X GET "http://localhost:8000/extrato" \
  -H "Authorization: Bearer TOKEN"
```

### 11.2 Com Python

```python
import requests

# Registrar
resp = requests.post("http://localhost:8000/registrar",
    json={"username":"joao","password":"senha123"})
print(resp.json())

# Login
resp = requests.post("http://localhost:8000/token",
    data={"username":"joao","password":"senha123"})
token = resp.json()["access_token"]

# Depositar
headers = {"Authorization": f"Bearer {token}"}
resp = requests.post("http://localhost:8000/deposito",
    json={"valor":100.00}, headers=headers)
print(resp.json())

# Extrato
resp = requests.get("http://localhost:8000/extrato", headers=headers)
print(resp.json())
```

## 12. Executando a Aplicação

### 12.1 Instalação de Dependências

```bash
pip install -r requirements.txt
```

### 12.2 Executar Servidor

```bash
# Opção 1: Arquivo único
python main.py

# Opção 2: Com uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Opção 3: Com Docker
docker-compose up
```

### 12.3 Acessar Documentação

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 13. Testes

Execute o script de testes:

```bash
python test_api.py
```

Este script demonstra:
- Registro de usuário
- Login e obtenção de token
- Obtenção de perfil
- Depósitos múltiplos
- Saques múltiplos
- Obtenção de extrato
- Validação de saldo insuficiente

## 14. Considerações de Performance

### 14.1 Otimizações Implementadas

- ✅ Uso de índices no banco de dados (username é UNIQUE)
- ✅ Queries otimizadas com ORDER BY DESC para extrato
- ✅ Limite de transações retornadas (padrão: 100)
- ✅ Conexões SQLite reutilizáveis

### 14.2 Melhorias Futuras

- Implementar connection pooling
- Adicionar cache Redis
- Usar PostgreSQL para melhor concorrência
- Implementar paginação no extrato
- Adicionar índices adicionais

## 15. Conclusão

A API Bancária implementa todos os requisitos especificados:

✅ **Cadastro de Transações**: Depósitos e saques registrados com histórico  
✅ **Exibição de Extrato**: Endpoint GET /extrato com todas as transações  
✅ **Autenticação JWT**: Proteção de endpoints com tokens seguros  
✅ **Validação**: Valores negativos e saldo insuficiente validados  
✅ **Documentação**: OpenAPI automática com Swagger e ReDoc  

A aplicação está pronta para uso e pode ser facilmente expandida com novas funcionalidades.
