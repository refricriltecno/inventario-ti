import time
import requests
import json

print("Aguardando 5 segundos para servidor carregar...")
time.sleep(5)

print("Testando login...")
try:
    r = requests.post('http://127.0.0.1:5000/api/auth/login', 
                     json={'username': 'admin', 'password': 'admin123'},
                     timeout=10)
    print(f'Status: {r.status_code}')
    data = r.json()
    print(f'Response completa: {json.dumps(data, indent=2)}')
    
    if 'token' in data:
        token = data['token']
        print(f"\n✅ Token obtido com sucesso!")
    else:
        print(f"\n❌ Sem token na resposta")
except Exception as e:
    print(f"❌ Erro: {e}")
