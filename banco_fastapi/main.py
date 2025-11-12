"""
API Bancária Assíncrona com FastAPI
Gerencia operações bancárias de depósitos e saques com autenticação JWT
"""

from datetime import datetime, timedelta
from typing import Optional, List
from decimal import Decimal
import sqlite3
import json
from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from jose import JWTError, jwt
import uvicorn


# ============================================================================
# CONFIGURAÇÕES
# ============================================================================

SECRET_KEY = "sua-chave-secreta-super-segura-aqui-mude-em-producao"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
DATABASE_URL = "banco.db"

# Contexto de criptografia para senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# ============================================================================
# MODELOS PYDANTIC
# ============================================================================

class Token(BaseModel):
    """Modelo para resposta de token JWT"""
    access_token: str
    token_type: str
    expires_in: int


class TokenData(BaseModel):
    """Dados extraídos do token JWT"""
    username: Optional[str] = None


class UsuarioRegistro(BaseModel):
    """Modelo para registro de novo usuário"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    email: Optional[str] = None


class UsuarioResposta(BaseModel):
    """Modelo para resposta de usuário"""
    id: int
    username: str
    email: Optional[str]
    saldo: Decimal


class Transacao(BaseModel):
    """Modelo para transação bancária"""
    id: int
    usuario_id: int
    tipo: str  # "deposito" ou "saque"
    valor: Decimal
    saldo_anterior: Decimal
    saldo_novo: Decimal
    data_hora: str
    descricao: Optional[str]


class OperacaoBancaria(BaseModel):
    """Modelo para requisição de operação bancária"""
    valor: Decimal = Field(..., gt=0, decimal_places=2)
    descricao: Optional[str] = None


class Extrato(BaseModel):
    """Modelo para resposta de extrato"""
    usuario_id: int
    username: str
    saldo_atual: Decimal
    transacoes: List[Transacao]


# ============================================================================
# BANCO DE DADOS
# ============================================================================

def inicializar_banco():
    """Inicializa o banco de dados com as tabelas necessárias"""
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Tabela de usuários
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            saldo DECIMAL(10, 2) DEFAULT 0.00,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabela de transações
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transacoes (
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
    """)
    
    conn.commit()
    conn.close()


def obter_conexao_db():
    """Obtém uma conexão com o banco de dados"""
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================================
# AUTENTICAÇÃO E SEGURANÇA
# ============================================================================

def verificar_senha(senha_plana: str, hash_senha: str) -> bool:
    """Verifica se a senha corresponde ao hash"""
    return pwd_context.verify(senha_plana, hash_senha)


def obter_hash_senha(senha: str) -> str:
    """Gera o hash de uma senha"""
    return pwd_context.hash(senha)


def criar_token_acesso(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Cria um token JWT"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def obter_usuario_atual(token: str = Depends(oauth2_scheme)) -> dict:
    """Obtém o usuário atual a partir do token JWT"""
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            raise credential_exception
        
        token_data = TokenData(username=username)
    except JWTError:
        raise credential_exception
    
    conn = obter_conexao_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE username = ?", (token_data.username,))
    usuario = cursor.fetchone()
    conn.close()
    
    if usuario is None:
        raise credential_exception
    
    return dict(usuario)


# ============================================================================
# OPERAÇÕES DO BANCO DE DADOS
# ============================================================================

def criar_usuario(username: str, password: str, email: Optional[str] = None) -> Optional[dict]:
    """Cria um novo usuário"""
    try:
        conn = obter_conexao_db()
        cursor = conn.cursor()
        
        hash_senha = obter_hash_senha(password)
        cursor.execute(
            "INSERT INTO usuarios (username, password_hash, email, saldo) VALUES (?, ?, ?, ?)",
            (username, hash_senha, email, 0.00)
        )
        
        conn.commit()
        usuario_id = cursor.lastrowid
        conn.close()
        
        return {"id": usuario_id, "username": username, "email": email, "saldo": 0.00}
    except sqlite3.IntegrityError:
        return None


def obter_usuario_por_username(username: str) -> Optional[dict]:
    """Obtém um usuário pelo username"""
    conn = obter_conexao_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE username = ?", (username,))
    usuario = cursor.fetchone()
    conn.close()
    
    return dict(usuario) if usuario else None


def registrar_transacao(usuario_id: int, tipo: str, valor: Decimal, 
                       saldo_anterior: Decimal, descricao: Optional[str] = None) -> dict:
    """Registra uma transação e atualiza o saldo do usuário"""
    conn = obter_conexao_db()
    cursor = conn.cursor()
    
    # Calcula o novo saldo
    if tipo == "deposito":
        saldo_novo = saldo_anterior + valor
    elif tipo == "saque":
        saldo_novo = saldo_anterior - valor
    else:
        raise ValueError("Tipo de transação inválido")
    
    # Registra a transação
    cursor.execute(
        """INSERT INTO transacoes 
           (usuario_id, tipo, valor, saldo_anterior, saldo_novo, descricao) 
           VALUES (?, ?, ?, ?, ?, ?)""",
        (usuario_id, tipo, valor, saldo_anterior, saldo_novo, descricao)
    )
    
    # Atualiza o saldo do usuário
    cursor.execute(
        "UPDATE usuarios SET saldo = ? WHERE id = ?",
        (saldo_novo, usuario_id)
    )
    
    conn.commit()
    transacao_id = cursor.lastrowid
    conn.close()
    
    return {
        "id": transacao_id,
        "usuario_id": usuario_id,
        "tipo": tipo,
        "valor": valor,
        "saldo_anterior": saldo_anterior,
        "saldo_novo": saldo_novo,
        "descricao": descricao
    }


def obter_transacoes_usuario(usuario_id: int, limite: int = 100) -> List[dict]:
    """Obtém todas as transações de um usuário"""
    conn = obter_conexao_db()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT * FROM transacoes 
           WHERE usuario_id = ? 
           ORDER BY data_hora DESC 
           LIMIT ?""",
        (usuario_id, limite)
    )
    transacoes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return transacoes


# ============================================================================
# APLICAÇÃO FASTAPI
# ============================================================================

app = FastAPI(
    title="API Bancária Assíncrona",
    description="API RESTful para gerenciar operações bancárias com autenticação JWT",
    version="1.0.0"
)

# Inicializa o banco de dados
inicializar_banco()


# ============================================================================
# ENDPOINTS DE AUTENTICAÇÃO
# ============================================================================

@app.post("/token", response_model=Token, tags=["Autenticação"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint de login que retorna um token JWT
    
    - **username**: Nome de usuário
    - **password**: Senha do usuário
    """
    usuario = obter_usuario_por_username(form_data.username)
    
    if not usuario or not verificar_senha(form_data.password, usuario["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = criar_token_acesso(
        data={"sub": usuario["username"]},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@app.post("/registrar", response_model=UsuarioResposta, tags=["Autenticação"])
async def registrar(usuario_data: UsuarioRegistro):
    """
    Endpoint para registrar um novo usuário
    
    - **username**: Nome de usuário (3-50 caracteres)
    - **password**: Senha (mínimo 6 caracteres)
    - **email**: Email do usuário (opcional)
    """
    usuario_existente = obter_usuario_por_username(usuario_data.username)
    
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username já existe"
        )
    
    novo_usuario = criar_usuario(
        username=usuario_data.username,
        password=usuario_data.password,
        email=usuario_data.email
    )
    
    if not novo_usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao criar usuário"
        )
    
    return novo_usuario


# ============================================================================
# ENDPOINTS DE OPERAÇÕES BANCÁRIAS
# ============================================================================

@app.post("/deposito", response_model=Transacao, tags=["Operações Bancárias"])
async def fazer_deposito(
    operacao: OperacaoBancaria,
    usuario_atual: dict = Depends(obter_usuario_atual)
):
    """
    Endpoint para realizar um depósito
    
    - **valor**: Valor do depósito (deve ser positivo)
    - **descricao**: Descrição opcional da transação
    """
    if operacao.valor <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O valor do depósito deve ser positivo"
        )
    
    transacao = registrar_transacao(
        usuario_id=usuario_atual["id"],
        tipo="deposito",
        valor=operacao.valor,
        saldo_anterior=Decimal(str(usuario_atual["saldo"])),
        descricao=operacao.descricao
    )
    
    return transacao


@app.post("/saque", response_model=Transacao, tags=["Operações Bancárias"])
async def fazer_saque(
    operacao: OperacaoBancaria,
    usuario_atual: dict = Depends(obter_usuario_atual)
):
    """
    Endpoint para realizar um saque
    
    - **valor**: Valor do saque (deve ser positivo)
    - **descricao**: Descrição opcional da transação
    """
    saldo_atual = Decimal(str(usuario_atual["saldo"]))
    
    if operacao.valor <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O valor do saque deve ser positivo"
        )
    
    if operacao.valor > saldo_atual:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Saldo insuficiente. Saldo atual: {saldo_atual}"
        )
    
    transacao = registrar_transacao(
        usuario_id=usuario_atual["id"],
        tipo="saque",
        valor=operacao.valor,
        saldo_anterior=saldo_atual,
        descricao=operacao.descricao
    )
    
    return transacao


@app.get("/extrato", response_model=Extrato, tags=["Operações Bancárias"])
async def obter_extrato(usuario_atual: dict = Depends(obter_usuario_atual)):
    """
    Endpoint para obter o extrato da conta
    
    Retorna o saldo atual e todas as transações do usuário
    """
    transacoes = obter_transacoes_usuario(usuario_atual["id"])
    
    return {
        "usuario_id": usuario_atual["id"],
        "username": usuario_atual["username"],
        "saldo_atual": Decimal(str(usuario_atual["saldo"])),
        "transacoes": transacoes
    }


# ============================================================================
# ENDPOINTS DE INFORMAÇÕES
# ============================================================================

@app.get("/me", response_model=UsuarioResposta, tags=["Usuário"])
async def obter_perfil(usuario_atual: dict = Depends(obter_usuario_atual)):
    """
    Endpoint para obter as informações do usuário atual
    """
    return {
        "id": usuario_atual["id"],
        "username": usuario_atual["username"],
        "email": usuario_atual["email"],
        "saldo": Decimal(str(usuario_atual["saldo"]))
    }


@app.get("/", tags=["Info"])
async def root():
    """
    Endpoint raiz da API
    """
    return {
        "mensagem": "API Bancária Assíncrona com FastAPI",
        "versao": "1.0.0",
        "documentacao": "/docs",
        "documentacao_alternativa": "/redoc"
    }


# ============================================================================
# EXECUÇÃO
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
