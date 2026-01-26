from pymongo import MongoClient
from app.routes.assets import bp_assets # Apenas para garantir contexto se precisasse, mas vamos direto pelo Mongo
from config import Config

# Conexão direta usando sua Configuração
client = MongoClient(Config.MONGO_URI)
db = client.get_database() # Pega o banco padrão da URI

# Sua lista exata
unidades_raw = [
    "00 - Administrativo",
    "01 - Matriz",
    "08 - Porto Alegre",
    "09 - Floripa",
    "06 - Blumenau",
    "12 - Itajaí",
    "03 - Joinville",
    "05 - Londrina",
    "17 - CD São Paulo",
    "22 - São Paulo (Itaim)",
    "21 - São Paulo (Osasco)",
    "20 - São Paulo (Guarulhos)",
    "10 - São Paulo",
    "02 - CD Vila Velha",
    "24 - CD Goiânia",
    "15 - Teresina",
    "18 - Belo Horizonte",
    "11 - Vila Velha",
    "07 - CD Içara",
    "13 - CD Paraíba",
    "27 - Brasília"
]

def definir_tipo(nome):
    nome_upper = nome.upper()
    
    # Regra 1: Se tem "CD" no nome -> Tipo CD
    if "CD " in nome_upper:
        return "CD"
    
    # Regra 2: Se é Administrativo -> Tipo Administrativo
    if "ADMINISTRATIVO" in nome_upper:
        return "Administrativo"
    
    # Regra 3: Se é Matriz -> Tipo Loja
    if "MATRIZ" in nome_upper:
        return "Loja"
    
    # Regra 4: O resto é tudo Loja (Cidades)
    return "Loja"

print("--- INICIANDO CADASTRO AUTOMÁTICO ---")

collection = db.filiais

for unidade in unidades_raw:
    tipo_calculado = definir_tipo(unidade)
    
    # Verifica se já existe para não duplicar
    if collection.find_one({"nome": unidade}):
        print(f"[-] {unidade} já existe. Pulando.")
    else:
        collection.insert_one({
            "nome": unidade,
            "tipo": tipo_calculado
        })
        print(f"[+] {unidade} cadastrada como: {tipo_calculado}")

print("--- CONCLUÍDO! ---")
print("Reinicie o Frontend (F5) para ver as novas unidades.")