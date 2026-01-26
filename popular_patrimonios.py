import csv
import sys
import re
from pymongo import MongoClient
from config import Config
from datetime import datetime

client = MongoClient(Config.MONGO_URI)
db = client.get_database()

# Mapear nomes de colunas do CSV
COLUMN_MAPPING = {
    'PAT': 'patrimonio',
    'Em Uso': 'localizacao_responsavel',
    'Observação': 'observacao',
    'Senha Windows': 'senha_windows',
    'Anydesk': 'anydesk',
    '.bat utilizado': 'bat_utilizado',
    'Tipo': 'tipo',
    'Modelo': 'modelo',
    'SoftPhone': 'softphone',
    'Zimbra': 'email_zimbra',
    'Conta Google': 'email_google',
    'Email Secundário': 'email_secundario',
    'Conta Google 2': 'conta_google_2',
    'Hostname': 'hostname',
    'Senha BIOS': 'senha_bios',
    'BitLocker': 'bitlocker',
    'VPN': 'vpn_login',
    'Senha VPN': 'senha_vpn',
    'GIX Remoto\n10.1.1.134/135': 'gix_remoto',
    'Duapi\n10.1.1.122': 'duapi',
    'Domínio\n10.1.1.129': 'dominio',
    'Centro de Custo Filial': 'filial'
}

# Softwares
SOFTWARE_COLS = [
    ('PAT \nSoftware 1', 'Software 1'),
    ('PAT \nSoftware 2', 'Software 2'),
    ('PAT \nSoftware 3', 'Software 3')
]

def limpar_valor(valor):
    """Remove espaços em branco e converte vazio para None"""
    if not valor or valor.strip() == '':
        return None
    return valor.strip()

def extrair_responsavel(texto_misto):
    """
    Extrai o nome do responsável do campo mesclado
    Ex: 'Matriz - Garantia - GABRIEL FERREIRA' -> 'GABRIEL FERREIRA'
    """
    if not texto_misto or '-' not in str(texto_misto):
        return None
    
    partes = str(texto_misto).split(' - ')
    # O nome geralmente está na última parte e em maiúsculas
    if len(partes) >= 3:
        nome = partes[-1].strip()
        # Se parecer um nome (tem pelo menos 3 caracteres e não é um código)
        if len(nome) >= 3 and not nome.startswith('['):
            return nome
    elif len(partes) == 2:
        # Se tiver apenas 2 partes, a segunda pode ser o responsável
        nome = partes[-1].strip()
        if len(nome) >= 3 and not nome[0].isdigit():
            return nome
    
    return None

def extrair_setor(texto_misto):
    """
    Extrai o setor/função do campo mesclado
    Ex: 'Matriz - Garantia - GABRIEL FERREIRA' -> 'Garantia'
    """
    if not texto_misto or '-' not in str(texto_misto):
        return None
    
    partes = str(texto_misto).split(' - ')
    
    if len(partes) >= 3:
        # Setor está no meio (entre filial e nome)
        setor = partes[1].strip()
        # Remove números entre colchetes no final
        setor = re.sub(r'\s*\[\d+\].*$', '', setor)
        if setor and not setor.startswith('['):
            return setor
    elif len(partes) == 2:
        # Se tiver 2 partes, a primeira após filial é setor/local
        setor = partes[1].strip()
        setor = re.sub(r'\s*\[\d+\].*$', '', setor)
        if setor and not setor[0].isdigit():
            return setor
    
    return None

def extrair_ramal(softphone):
    """Extrai ramal do campo SoftPhone"""
    if not softphone:
        return None
    valor = str(softphone).strip()
    if valor and valor.isdigit():
        return valor
    return None

def processar_softwares(row):
    """Extrai softwares do CSV"""
    softwares = []
    for col_pat, col_nome in SOFTWARE_COLS:
        nome_soft = limpar_valor(row.get(col_nome, ''))
        if nome_soft:
            softwares.append({
                'nome': nome_soft,
                'licenca': '',
                'dt_instalacao': '',
                'dt_vencimento': ''
            })
    return softwares if softwares else []

def processar_linha(row):
    """Processa uma linha do CSV e retorna um dicionário formatado"""
    ativo = {}
    
    for csv_col, db_field in COLUMN_MAPPING.items():
        if csv_col in row:
            valor = limpar_valor(row[csv_col])
            
            # Tratamento especial para o campo mesclado
            if db_field == 'localizacao_responsavel':
                # Tenta extrair responsável e setor
                if valor:
                    resp = extrair_responsavel(valor)
                    setor = extrair_setor(valor)
                    if resp:
                        ativo['responsavel'] = resp
                    if setor:
                        ativo['setor'] = setor
            elif valor:
                ativo[db_field] = valor
    
    # Extrair Ramal do SoftPhone
    if 'softphone' in ativo:
        ramal = extrair_ramal(ativo.get('softphone', ''))
        if ramal:
            ativo['ramal'] = ramal
        del ativo['softphone']
        ativo['is_softphone'] = ramal is not None
    
    # Extrair softwares
    softwares = processar_softwares(row)
    if softwares:
        ativo['softwares'] = softwares
    
    # Adicionar metadados
    ativo['status'] = 'Ativo'
    ativo['created_at'] = datetime.now()
    ativo['updated_at'] = datetime.now()
    
    return ativo if ativo.get('patrimonio') else None

def popular_patrimonios():
    """Popula o banco de dados com os dados do CSV"""
    
    try:
        collection = db.workstations
        filiais_collection = db.filiais
        
        # Carregar todas as filiais do banco para normalização
        filiais_banco = list(filiais_collection.find())
        print(f"Filiais no banco: {len(filiais_banco)}")
        
        def normalizar_filial(filial_csv):
            """Tenta encontrar a filial completa no banco baseado no nome parcial"""
            if not filial_csv:
                return None
            
            filial_csv_upper = filial_csv.upper().strip()
            
            for f in filiais_banco:
                nome_banco = f.get('nome', '').strip()
                nome_banco_upper = nome_banco.upper()
                
                # Match exato
                if nome_banco_upper == filial_csv_upper:
                    return nome_banco
                
                # Match se a filial CSV está contida no nome do banco
                # Ex: "Osasco" em "21 - São Paulo (Osasco)"
                if filial_csv_upper in nome_banco_upper:
                    return nome_banco
                
                # Match se o código está no início
                # Ex: "21" em "21 - São Paulo (Osasco)"
                if nome_banco_upper.startswith(filial_csv_upper):
                    return nome_banco
            
            # Se não encontrar match, retorna o original
            return filial_csv
        
        # Verificar quantos já existem
        count_antes = collection.count_documents({})
        print(f"Patrimonios existentes antes: {count_antes}")
        
        total_inseridos = 0
        total_atualizados = 0
        total_erros = 0
        
        with open('patrimonios.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for idx, row in enumerate(reader, start=2):  # start=2 pois linha 1 é header
                try:
                    ativo = processar_linha(row)
                    
                    if not ativo:
                        total_erros += 1
                        continue
                    
                    # Normalizar filial para usar o nome completo do banco
                    if ativo.get('filial'):
                        filial_normalizada = normalizar_filial(ativo['filial'])
                        ativo['filial'] = filial_normalizada
                        print(f"[N] Filial normalizada: {ativo.get('filial')}")
                    
                    # Verificar se já existe
                    patrimonio = ativo.get('patrimonio')
                    doc_existente = collection.find_one({'patrimonio': patrimonio})
                    
                    if doc_existente:
                        # Se já existe, atualizar com novos dados (merge)
                        ativo_atualizado = {**doc_existente, **ativo}
                        ativo_atualizado.pop('_id', None)
                        collection.update_one(
                            {'patrimonio': patrimonio},
                            {'$set': ativo_atualizado}
                        )
                        print(f"[U] PAT {patrimonio} - {ativo.get('filial')}")
                        total_atualizados += 1
                        continue
                    
                    # Inserir novo
                    result = collection.insert_one(ativo)
                    print(f"[+] PAT {patrimonio} - {ativo.get('filial')}")
                    total_inseridos += 1
                    
                except Exception as e:
                    print(f"[!] Linha {idx}: {str(e)}")
                    total_erros += 1
                    continue
        
        # Resumo final
        count_depois = collection.count_documents({})
        print("\n" + "="*80)
        print("RESUMO DA IMPORTACAO")
        print("="*80)
        print(f"Patrimonios inseridos: {total_inseridos}")
        print(f"Patrimonios atualizados: {total_atualizados}")
        print(f"Erros processados: {total_erros}")
        print(f"Total antes: {count_antes}")
        print(f"Total depois: {count_depois}")
        print("="*80)
        
    except FileNotFoundError:
        print("Erro: Arquivo 'patrimonios.csv' não encontrado!")
        sys.exit(1)
    except Exception as e:
        print(f"Erro geral: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    print("Iniciando importação de patrimonios com extração de Responsável e Setor...")
    popular_patrimonios()
    print("Importação concluída!")

