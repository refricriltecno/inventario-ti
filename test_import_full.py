import time
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

print("=" * 60)
print("TESTE DE IMPORTAÇÃO DE PATRIMONIOS.CSV")
print("=" * 60)

# Step 1: Login
print("\n[1/3] Fazendo login...")
try:
    r = requests.post(f"{BASE_URL}/api/auth/login", 
                     json={'username': 'admin', 'password': 'admin123'},
                     timeout=10)
    
    if r.status_code != 200:
        print(f"❌ Erro no login: {r.text}")
        exit(1)
    
    token = r.json().get('access_token')
    if not token:
        print(f"❌ Token não obtido: {r.json()}")
        exit(1)
    
    print(f"✅ Login realizado! Token: {token[:30]}...")
    
except Exception as e:
    print(f"❌ Erro na requisição: {e}")
    exit(1)

# Step 2: Import
print("\n[2/3] Enviando patrimonios.csv...")
headers = {"Authorization": f"Bearer {token}"}

try:
    with open("patrimonios.csv", "rb") as f:
        files = {"file": f}
        
        r = requests.post(
            f"{BASE_URL}/api/import/assets",
            files=files,
            headers=headers,
            timeout=60
        )
    
    print(f"Status: {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        print(f"✅ SUCESSO!")
        print(f"   Ativos criados: {data.get('sucessos', 0)}")
        print(f"   Total de erros: {data.get('total_erros', 0)}")
        
        if data.get('erros'):
            print(f"\n   Primeiros erros:")
            for erro in data['erros'][:5]:
                print(f"   - {erro}")
    else:
        print(f"❌ Erro na importação")
        print(f"   Resposta: {r.text}")
        
except Exception as e:
    print(f"❌ Erro: {e}")
    exit(1)

# Step 3: Verify
print("\n[3/3] Verificando dados importados...")
try:
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{BASE_URL}/api/assets", headers=headers, timeout=10)
    
    if r.status_code == 200:
        assets = r.json()
        print(f"✅ Total de ativos no banco: {len(assets)}")
    else:
        print(f"❌ Erro ao buscar ativos: {r.status_code}")
        
except Exception as e:
    print(f"❌ Erro: {e}")

print("\n" + "=" * 60)
print("FIM DO TESTE")
print("=" * 60)
