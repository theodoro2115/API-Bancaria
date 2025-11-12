"""
Módulo de configuração e gerenciamento do banco de dados SQLite
"""

import sqlite3
from typing import Optional, List, Dict
from decimal import Decimal
from datetime import datetime


DATABASE_URL = "banco.db"


def obter_conexao_db():
    """Obtém uma conexão com o banco de dados"""
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    return conn


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


def criar_usuario(username: str, password_hash: str, email: Optional[str] = None) -> Optional[Dict]:
    """Cria um novo usuário no banco de dados"""
    try:
        conn = obter_conexao_db()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO usuarios (username, password_hash, email, saldo) VALUES (?, ?, ?, ?)",
            (username, password_hash, email, 0.00)
        )
        
        conn.commit()
        usuario_id = cursor.lastrowid
        conn.close()
        
        return {"id": usuario_id, "username": username, "email": email, "saldo": 0.00}
    except sqlite3.IntegrityError:
        return None


def obter_usuario_por_username(username: str) -> Optional[Dict]:
    """Obtém um usuário pelo username"""
    conn = obter_conexao_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE username = ?", (username,))
    usuario = cursor.fetchone()
    conn.close()
    
    return dict(usuario) if usuario else None


def obter_usuario_por_id(usuario_id: int) -> Optional[Dict]:
    """Obtém um usuário pelo ID"""
    conn = obter_conexao_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,))
    usuario = cursor.fetchone()
    conn.close()
    
    return dict(usuario) if usuario else None


def registrar_transacao(usuario_id: int, tipo: str, valor: Decimal, 
                       saldo_anterior: Decimal, descricao: Optional[str] = None) -> Dict:
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


def obter_transacoes_usuario(usuario_id: int, limite: int = 100) -> List[Dict]:
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
