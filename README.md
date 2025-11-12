API Bancária Assíncrona com FastAPI
-----------------------------------
Uma API RESTful para gerenciar operações bancárias (depósitos e saques) com autenticação JWT, desenvolvida com FastAPI e SQLite.

O que é este projeto?

Este projeto implementa uma API bancária simples que permite aos usuários criar contas, fazer login, realizar depósitos e saques, e visualizar o histórico de transações. A API utiliza autenticação JWT para proteger os endpoints e garante que apenas usuários autenticados possam acessar suas contas.

Principais funcionalidades

•
Registro e autenticação de usuários: Crie uma conta com username e senha, faça login para obter um token JWT

•
Depósitos: Adicione dinheiro à sua conta com descrição opcional

•
Saques: Retire dinheiro da sua conta com validação de saldo

•
Extrato: Visualize todas as suas transações com data, hora e saldo

•
Validações: A API valida valores negativos, saldo insuficiente e garante a integridade dos dados

•
Documentação automática: Acesse a documentação interativa da API no Swagger UI ou ReDoc

Como instalar

1.
Clone o repositório:

Bash


git clone https://github.com/seu-usuario/banco_fastapi.git
cd banco_fastapi


1.
Instale as dependências:

Bash


pip install -r requirements.txt


1.
Execute a API:

Bash


python main.py


A API estará disponível em http://localhost:8000

Como usar

1. Registrar um novo usuário

Bash


curl -X POST "http://localhost:8000/registrar" \
  -H "Content-Type: application/json" \
  -d '{"username":"joao","password":"senha123","email":"joao@example.com"}'


2. Fazer login

Bash


curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=joao&password=senha123"


Você receberá um token JWT que deve ser usado nos próximos passos.

3. Fazer um depósito

Bash


curl -X POST "http://localhost:8000/deposito" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"valor":100.00,"descricao":"Depósito inicial"}'


4. Fazer um saque

Bash


curl -X POST "http://localhost:8000/saque" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"valor":50.00,"descricao":"Saque para compras"}'


5. Visualizar extrato

Bash


curl -X GET "http://localhost:8000/extrato" \
  -H "Authorization: Bearer SEU_TOKEN"


Documentação interativa

Após iniciar a API, você pode acessar a documentação interativa em:

•
Swagger UI: http://localhost:8000/docs

•
ReDoc: http://localhost:8000/redoc

Lá você pode testar todos os endpoints diretamente no navegador.

Estrutura do projeto

•
main.py - Implementação completa da API em um único arquivo

•
database.py - Funções para gerenciar o banco de dados SQLite

•
security.py - Funções de autenticação e geração de tokens JWT

•
schemas.py - Modelos Pydantic para validação de dados

•
test_api.py - Script com exemplos de como usar a API

•
requirements.txt - Dependências do projeto

•
Dockerfile - Para executar a API em um container Docker

•
docker-compose.yml - Para orquestrar a aplicação com Docker

Endpoints disponíveis

Autenticação

•
POST /registrar - Registrar novo usuário

•
POST /token - Fazer login e obter token JWT

Operações bancárias

•
POST /deposito - Realizar um depósito

•
POST /saque - Realizar um saque

•
GET /extrato - Obter extrato da conta

Informações do usuário

•
GET /me - Obter informações do usuário autenticado

•
GET / - Informações gerais da API

Tecnologias utilizadas

•
FastAPI - Framework web moderno e rápido para Python

•
Uvicorn - Servidor ASGI para rodar a API

•
Pydantic - Validação de dados e documentação automática

•
SQLite - Banco de dados leve para persistência

•
Python-jose - Implementação de JWT

•
Passlib - Hash seguro de senhas com bcrypt

Segurança

A API utiliza:

•
JWT (JSON Web Tokens ) para autenticação

•
Bcrypt para hash de senhas

•
Validação de dados com Pydantic

•
Proteção de endpoints que requerem autenticação

Importante: Em produção, altere a SECRET_KEY no arquivo security.py ou main.py para uma chave segura e aleatória.

Exemplos de resposta

Registrar usuário (sucesso)

JSON


{
  "id": 1,
  "username": "joao",
  "email": "joao@example.com",
  "saldo": 0.00
}


Login (sucesso)

JSON


{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}


Depósito (sucesso)

JSON


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


Extrato (sucesso)

JSON


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
    }
  ]
}


Como testar

Execute o script de testes para ver a API em ação:

Bash


python test_api.py


Este script vai:

1.
Registrar um novo usuário

2.
Fazer login

3.
Realizar depósitos

4.
Realizar saques

5.
Visualizar o extrato

6.
Testar validações (saldo insuficiente)

Executar com Docker

Se você tem Docker instalado, pode executar a API assim:

Bash


docker-compose up


A API estará disponível em http://localhost:8000

Tratamento de erros

A API retorna códigos HTTP apropriados:

•
200 - Sucesso

•
400 - Requisição inválida (valor negativo, saldo insuficiente, etc )

•
401 - Não autenticado (token inválido ou expirado)

•
404 - Recurso não encontrado

•
500 - Erro interno do servidor

Contribuindo

Sinta-se livre para fazer fork, abrir issues e enviar pull requests. Toda contribuição é bem-vinda!

Licença

Este projeto é fornecido como exemplo educacional. Use livremente.

Autor

Desenvolvido como exemplo de API Bancária com FastAPI.

Suporte

Para dúvidas sobre FastAPI, consulte a documentação oficial em https://fastapi.tiangolo.com/

