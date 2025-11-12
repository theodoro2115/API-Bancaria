"""
Módulo de segurança e autenticação JWT
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from database import obter_usuario_por_username


# Configurações
SECRET_KEY = "sua-chave-secreta-super-segura-aqui-mude-em-producao"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Contexto de criptografia para senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class TokenData(BaseModel):
    """Dados extraídos do token JWT"""
    username: Optional[str] = None


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
    
    usuario = obter_usuario_por_username(token_data.username)
    
    if usuario is None:
        raise credential_exception
    
    return usuario
