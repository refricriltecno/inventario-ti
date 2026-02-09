#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script para testar a importação de patrimonios.csv"""

import requests
import json
import time
from config import Config

BASE_URL = "http://127.0.0.1:5000"

def get_token():
    """Login para obter JWT token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    
    if response.status_code != 200:
        print(f"❌ Erro ao fazer login: {response.text}")
        return None
    
    data = response.json()
    return data.get("access_token")

def test_import_assets(token):
    """Testa importação de ativos"""
    print("\n📋 Testando importação de patrimonios.csv...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # Abre o arquivo CSV
    try:
        with open("patrimonios.csv", "rb") as f:
            files = {"file": f}
            
            try:
                response = requests.post(
                    f"{BASE_URL}/api/import/assets",
                    files=files,
                    headers=headers,
                    timeout=30
                )
                
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"\n✅ Sucesso!")
                    print(f"   Ativos criados: {data.get('sucessos', 0)}")
                    print(f"   Erros: {data.get('total_erros', 0)}")
                    if data.get('erros'):
                        print(f"\n   Primeiros erros:")
                        for erro in data['erros'][:5]:
                            print(f"   - {erro}")
                else:
                    print(f"\n❌ Erro na importação!")
                    print(f"Response: {response.text}")
                    
            except requests.exceptions.ConnectionError as e:
                print(f"❌ Erro de conexão: {e}")
            except requests.exceptions.Timeout:
                print(f"❌ Timeout na requisição")
            except Exception as e:
                print(f"❌ Erro: {e}")
    except FileNotFoundError:
        print("❌ Arquivo patrimonios.csv não encontrado!")

if __name__ == "__main__":
    print("🔐 Obtendo token...")
    token = get_token()
    
    if token:
        print(f"✅ Token obtido: {token[:30]}...")
        test_import_assets(token)
    else:
        print("❌ Não foi possível obter token")
