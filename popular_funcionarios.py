import csv
from pymongo import MongoClient
from config import Config
from datetime import datetime

client = MongoClient(Config.MONGO_URI)
db = client.get_database()

def popular_funcionarios(csv_path):
    """Lê o CSV com nomes exatos das filiais e popula a coleção de funcionários"""
    
    funcionarios_inseridos = 0
    erro_count = 0
    
    print("--- INICIANDO UPLOAD DE FUNCIONÁRIOS (EXCEL ATUALIZADO) ---\n")
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=';')
            
            # Lê o cabeçalho (nomes exatos das filiais)
            headers = next(reader)
            headers = [h.strip().replace('\ufeff', '') for h in headers]  # Remove espaços e BOM
            print(f"Filiais encontradas ({len(headers)}): {headers}\n")
            
            # Processa cada linha de funcionários
            linha_num = 1
            for row in reader:
                linha_num += 1
                
                # Processa cada funcionário em cada coluna (filial)
                for col_idx, funcionario_nome in enumerate(row):
                    # Pula se estiver vazio
                    if not funcionario_nome or not funcionario_nome.strip():
                        continue
                    
                    funcionario_nome = funcionario_nome.strip()
                    filial_nome = headers[col_idx]  # Usa o nome exato do cabeçalho
                    
                    # Verifica se filial existe no banco
                    filial = db.filiais.find_one({'nome': filial_nome})
                    if not filial:
                        print(f"❌ Filial '{filial_nome}' não existe no banco (linha {linha_num})")
                        erro_count += 1
                        continue
                    
                    # Verifica se funcionário já existe
                    func_existe = db.funcionarios.find_one({
                        'nome': funcionario_nome,
                        'filial': filial_nome
                    })
                    
                    if not func_existe:
                        # Insere novo funcionário
                        db.funcionarios.insert_one({
                            'nome': funcionario_nome,
                            'filial': filial_nome,
                            'created_at': datetime.now(),
                            'updated_at': datetime.now()
                        })
                        funcionarios_inseridos += 1
                        print(f"[+] {funcionario_nome} -> {filial_nome}")
        
        print(f"\n--- CONCLUÍDO! ---")
        print(f"[OK] Funcionários inseridos: {funcionarios_inseridos}")
        print(f"[ERRO] Erros: {erro_count}")
        
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {csv_path}")
    except Exception as e:
        print(f"❌ Erro ao processar arquivo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    # Primeiro limpa funcionários antigos
    result = db.funcionarios.delete_many({})
    print(f'[*] {result.deleted_count} funcionários removidos\n')
    
    csv_file = r'c:\Users\User\Downloads\funcionarios.csv'
    popular_funcionarios(csv_file)
