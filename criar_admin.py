from pymongo import MongoClient
from config import Config
import bcrypt
from datetime import datetime

# Conectar direto ao MongoDB
client = MongoClient(Config.MONGO_URI)
db = client.get_database()

print("--- CRIANDO PRIMEIRO USUÁRIO ADMIN ---\n")

# Criar índices para melhor performance
db.logs.create_index([('asset_id', 1), ('data', -1)])
db.logs.create_index([('usuario', 1)])
db.logs.create_index([('acao', 1)])
print("[+] Índices de logs criados")

# Criar usuário admin
username = 'admin'
password = 'admin123'
nome = 'Administrador'
filial = '00 - Administrativo'

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

if not db.usuarios.find_one({'username': username}):
    user = {
        'username': username,
        'senha': hash_password(password),
        'nome': nome,
        'filial': filial,
        'permissoes': ['admin', 'view', 'edit', 'delete'],
        'created_at': datetime.now(),
        'updated_at': datetime.now(),
        'ativo': True
    }
    result = db.usuarios.insert_one(user)
    print(f"[+] Usuário '{username}' criado com sucesso!")
    print(f"    Credenciais: {username} / {password}")
    print(f"    Permissões: admin, view, edit, delete")
else:
    print(f"[-] Usuário '{username}' já existe")

print("\n--- CONCLUÍDO! ---")
