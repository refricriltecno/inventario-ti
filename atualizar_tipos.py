from pymongo import MongoClient
from config import Config

client = MongoClient(Config.MONGO_URI)
db = client.get_database()

# Atualizar 00 - Administrativo para tipo Administrativo
db.filiais.update_one({'nome': '00 - Administrativo'}, {'$set': {'tipo': 'Administrativo'}})
print('[+] 00 - Administrativo atualizado para tipo: Administrativo')

# Atualizar 01 - Matriz para tipo Loja
db.filiais.update_one({'nome': '01 - Matriz'}, {'$set': {'tipo': 'Loja'}})
print('[+] 01 - Matriz atualizado para tipo: Loja')

print('--- CONCLUÍDO! ---')
