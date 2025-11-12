"""
Script de testes para a API Bancária
Demonstra como usar todos os endpoints
"""

import requests
import json
from typing import Optional

BASE_URL = "http://localhost:8000"


class ClienteBancario:
    """Cliente para testar a API Bancária"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.usuario = None
    
    def registrar(self, username: str, password: str, email: Optional[str] = None):
        """Registra um novo usuário"""
        print(f"\n📝 Registrando usuário: {username}")
        response = requests.post(
            f"{self.base_url}/registrar",
            json={"username": username, "password": password, "email": email}
        )
        
        if response.status_code == 200:
            self.usuario = response.json()
            print(f"✅ Usuário registrado com sucesso!")
            print(f"   ID: {self.usuario['id']}")
            print(f"   Username: {self.usuario['username']}")
            print(f"   Email: {self.usuario['email']}")
            print(f"   Saldo: R$ {self.usuario['saldo']:.2f}")
            return self.usuario
        else:
            print(f"❌ Erro ao registrar: {response.json()}")
            return None
    
    def login(self, username: str, password: str):
        """Faz login e obtém o token JWT"""
        print(f"\n🔐 Fazendo login: {username}")
        response = requests.post(
            f"{self.base_url}/token",
            data={"username": username, "password": password}
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data["access_token"]
            print(f"✅ Login realizado com sucesso!")
            print(f"   Token: {self.token[:50]}...")
            print(f"   Tipo: {data['token_type']}")
            print(f"   Expira em: {data['expires_in']} segundos")
            return self.token
        else:
            print(f"❌ Erro ao fazer login: {response.json()}")
            return None
    
    def obter_perfil(self):
        """Obtém o perfil do usuário atual"""
        print(f"\n👤 Obtendo perfil do usuário")
        response = requests.get(
            f"{self.base_url}/me",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        
        if response.status_code == 200:
            usuario = response.json()
            self.usuario = usuario
            print(f"✅ Perfil obtido com sucesso!")
            print(f"   ID: {usuario['id']}")
            print(f"   Username: {usuario['username']}")
            print(f"   Email: {usuario['email']}")
            print(f"   Saldo: R$ {usuario['saldo']:.2f}")
            return usuario
        else:
            print(f"❌ Erro ao obter perfil: {response.json()}")
            return None
    
    def depositar(self, valor: float, descricao: Optional[str] = None):
        """Realiza um depósito"""
        print(f"\n💰 Realizando depósito de R$ {valor:.2f}")
        response = requests.post(
            f"{self.base_url}/deposito",
            json={"valor": valor, "descricao": descricao},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        
        if response.status_code == 200:
            transacao = response.json()
            print(f"✅ Depósito realizado com sucesso!")
            print(f"   ID da transação: {transacao['id']}")
            print(f"   Valor: R$ {transacao['valor']:.2f}")
            print(f"   Saldo anterior: R$ {transacao['saldo_anterior']:.2f}")
            print(f"   Saldo novo: R$ {transacao['saldo_novo']:.2f}")
            print(f"   Data/Hora: {transacao['data_hora']}")
            if transacao['descricao']:
                print(f"   Descrição: {transacao['descricao']}")
            return transacao
        else:
            print(f"❌ Erro ao depositar: {response.json()}")
            return None
    
    def sacar(self, valor: float, descricao: Optional[str] = None):
        """Realiza um saque"""
        print(f"\n💸 Realizando saque de R$ {valor:.2f}")
        response = requests.post(
            f"{self.base_url}/saque",
            json={"valor": valor, "descricao": descricao},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        
        if response.status_code == 200:
            transacao = response.json()
            print(f"✅ Saque realizado com sucesso!")
            print(f"   ID da transação: {transacao['id']}")
            print(f"   Valor: R$ {transacao['valor']:.2f}")
            print(f"   Saldo anterior: R$ {transacao['saldo_anterior']:.2f}")
            print(f"   Saldo novo: R$ {transacao['saldo_novo']:.2f}")
            print(f"   Data/Hora: {transacao['data_hora']}")
            if transacao['descricao']:
                print(f"   Descrição: {transacao['descricao']}")
            return transacao
        else:
            print(f"❌ Erro ao sacar: {response.json()}")
            return None
    
    def obter_extrato(self):
        """Obtém o extrato da conta"""
        print(f"\n📋 Obtendo extrato da conta")
        response = requests.get(
            f"{self.base_url}/extrato",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        
        if response.status_code == 200:
            extrato = response.json()
            print(f"✅ Extrato obtido com sucesso!")
            print(f"   Usuário: {extrato['username']}")
            print(f"   Saldo atual: R$ {extrato['saldo_atual']:.2f}")
            print(f"   Total de transações: {len(extrato['transacoes'])}")
            print(f"\n   Histórico de transações:")
            for i, transacao in enumerate(extrato['transacoes'], 1):
                tipo = "📥 Depósito" if transacao['tipo'] == 'deposito' else "📤 Saque"
                print(f"   {i}. {tipo} - R$ {transacao['valor']:.2f} - {transacao['data_hora']}")
                if transacao['descricao']:
                    print(f"      Descrição: {transacao['descricao']}")
            return extrato
        else:
            print(f"❌ Erro ao obter extrato: {response.json()}")
            return None


def testar_api():
    """Executa uma sequência de testes na API"""
    print("=" * 60)
    print("TESTE DA API BANCÁRIA COM FASTAPI")
    print("=" * 60)
    
    cliente = ClienteBancario()
    
    # 1. Registrar novo usuário
    cliente.registrar(
        username="joao_silva",
        password="senha123",
        email="joao@example.com"
    )
    
    # 2. Fazer login
    cliente.login("joao_silva", "senha123")
    
    # 3. Obter perfil
    cliente.obter_perfil()
    
    # 4. Fazer depósito
    cliente.depositar(1000.00, "Salário mensal")
    
    # 5. Fazer outro depósito
    cliente.depositar(500.00, "Bônus")
    
    # 6. Fazer saque
    cliente.sacar(200.00, "Compras no supermercado")
    
    # 7. Fazer outro saque
    cliente.sacar(150.00, "Pagamento de conta")
    
    # 8. Obter extrato
    cliente.obter_extrato()
    
    # 9. Tentar saque com saldo insuficiente
    print("\n⚠️  Testando validação de saldo insuficiente:")
    cliente.sacar(2000.00, "Tentativa com saldo insuficiente")
    
    # 10. Obter perfil final
    cliente.obter_perfil()
    
    print("\n" + "=" * 60)
    print("TESTES CONCLUÍDOS COM SUCESSO!")
    print("=" * 60)


if __name__ == "__main__":
    testar_api()
