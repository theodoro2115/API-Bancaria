"""
Módulo de modelos Pydantic para validação de dados
"""

from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field


class Token(BaseModel):
    """Modelo para resposta de token JWT"""
    access_token: str
    token_type: str
    expires_in: int


class UsuarioRegistro(BaseModel):
    """Modelo para registro de novo usuário"""
    username: str = Field(..., min_length=3, max_length=50, description="Nome de usuário")
    password: str = Field(..., min_length=6, description="Senha do usuário")
    email: Optional[str] = Field(None, description="Email do usuário")


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
    tipo: str
    valor: Decimal
    saldo_anterior: Decimal
    saldo_novo: Decimal
    data_hora: str
    descricao: Optional[str]


class OperacaoBancaria(BaseModel):
    """Modelo para requisição de operação bancária"""
    valor: Decimal = Field(..., gt=0, decimal_places=2, description="Valor da operação")
    descricao: Optional[str] = Field(None, description="Descrição da operação")


class Extrato(BaseModel):
    """Modelo para resposta de extrato"""
    usuario_id: int
    username: str
    saldo_atual: Decimal
    transacoes: List[Transacao]
