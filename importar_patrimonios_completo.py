"""Script para importar todos os patrimônios do CSV patrimonios.csv"""
import csv
import sys
import io
from datetime import datetime
from app import create_app
from app.models import db, Asset, Filial

# Configurar encoding para Windows
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def extrair_filial_da_descricao(descricao):
    """Extrai o nome da filial da descrição"""
    if not descricao:
        return "Sem Filial"
    
    # Mapeamento de filiais
    filiais_map = {
        "Matriz": "Matriz",
        "Sao Paulo": "Sao Paulo",
        "Guarulhos": "Sao Paulo (Guarulhos)",
        "Osasco": "Sao Paulo (Osasco)",
        "Itaim": "Sao Paulo (Itaim)",
        "Joinville": "Joinville",
        "Blumenau": "Blumenau",
        "Floripa": "Floripa",
        "Florianopolis": "Floripa",
        "Londrina": "Londrina",
        "Teresina": "Teresina",
        "Porto Alegre": "Porto Alegre",
        "Belo Horizonte": "Belo Horizonte",
        "Itajai": "Itajáí",
        "Vila Velha": "Vila Velha",
        "CD Icara": "CD Içara",
        "CD Paraiba": "CD Paraíba",
        "CD SAO PAULO": "CD São Paulo",
        "CD Sao Paulo": "CD São Paulo",
        "CD Vila Velha": "CD Vila Velha",
        "Goiania": "Goiânia",
    }
    
    descricao_upper = descricao.upper()
    
    # Procurar por correspondências exatas
    for key, value in filiais_map.items():
        if key.upper() in descricao_upper:
            return value
    
    # Se não encontrar, tentar pegar a primeira parte antes do hífen
    if '-' in descricao:
        primeira_parte = descricao.split('-')[0].strip()
        for key, value in filiais_map.items():
            if key.upper() in primeira_parte.upper():
                return value
    
    return "Sem Filial"


def extrair_setor_responsavel(descricao):
    """Extrai setor e responsável da descrição"""
    setor = "Sem Setor"
    responsavel = None
    
    if not descricao:
        return setor, responsavel
    
    # Padrão: "LOCAL - SETOR [#] - RESPONSAVEL"
    partes = [p.strip() for p in descricao.split('-')]
    
    if len(partes) >= 2:
        # Segunda parte é geralmente o setor
        setor_parte = partes[1]
        # Remove números entre colchetes
        setor = setor_parte.split('[')[0].strip()
    
    if len(partes) >= 3:
        # Terceira parte é o responsável
        responsavel = partes[2].strip()
        # Remove números entre colchetes se houver
        responsavel = responsavel.split('[')[0].strip()
    
    return setor if setor else "Sem Setor", responsavel


def importar_patrimonios():
    """Importa patrimônios do CSV para o banco de dados"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "=" * 70)
        print("IMPORTADOR DE PATRIMONIOS")
        print("=" * 70)
        
        contador_novo = 0
        contador_atualizado = 0
        contador_erro = 0
        contador_ignorado = 0
        
        try:
            with open('patrimonios.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for idx, row in enumerate(reader, start=2):
                    try:
                        pat = row.get('PAT', '').strip()
                        
                        # Validação
                        if not pat or pat == 'PAT':
                            contador_ignorado += 1
                            continue
                        
                        # Verificar se já existe
                        asset_existente = Asset.query.filter_by(patrimonio=pat).first()
                        
                        if asset_existente:
                            contador_atualizado += 1
                            continue
                        
                        # Extrair dados
                        descricao = row.get('Em Uso', '').strip()
                        filial_nome = extrair_filial_da_descricao(descricao)
                        setor, responsavel = extrair_setor_responsavel(descricao)
                        
                        # Garantir que a filial existe
                        filial = Filial.query.filter_by(nome=filial_nome).first()
                        if not filial:
                            # Se for novo tipo de filial, adicionar
                            tipo_filial = determinar_tipo_filial(filial_nome)
                            filial = Filial(
                                nome=filial_nome,
                                ativo=True
                            )
                            db.session.add(filial)
                            db.session.flush()
                        
                        # Criar novo asset
                        novo_asset = Asset(
                            patrimonio=pat,
                            tipo=row.get('Tipo', '').strip() or 'Desktop',
                            marca='Dell',  # Padrão
                            modelo=row.get('Modelo', '').strip() or 'Sem modelo',
                            numero_serie=row.get('PAT', pat),
                            filial=filial_nome,
                            setor=setor,
                            responsavel=responsavel or 'Sem responsável',
                            status='Ativo',
                            observacoes=f"Importado do CSV em {datetime.now().strftime('%d/%m/%Y %H:%M')}"
                        )
                        
                        db.session.add(novo_asset)
                        contador_novo += 1
                        
                        if idx % 50 == 0:
                            print(f"[{idx}] Processados {idx} registros...")
                        
                    except Exception as e:
                        print(f"ERRO Linha {idx}: {str(e)}")
                        contador_erro += 1
                        continue
                
                # Commit final
                db.session.commit()
                
                print("\n" + "=" * 70)
                print("IMPORTACAO COMPLETA!")
                print("=" * 70)
                print(f"Novos assets: {contador_novo}")
                print(f"Atualizados: {contador_atualizado}")
                print(f"Ignorados: {contador_ignorado}")
                print(f"Erros: {contador_erro}")
                print(f"Total no banco: {Asset.query.count()}")
                print("=" * 70 + "\n")
                
        except FileNotFoundError:
            print("ERRO: Arquivo patrimonios.csv nao encontrado!")
            return
        except Exception as e:
            db.session.rollback()
            print(f"ERRO geral: {str(e)}")
            return


def determinar_tipo_filial(nome_filial):
    """Determina o tipo da filial (Loja, CD, Administrativo)"""
    nome_upper = nome_filial.upper()
    
    if 'CD' in nome_upper or 'CENTRO' in nome_upper:
        return 'CD'
    elif 'MATRIZ' in nome_upper:
        return 'Administrativo'
    else:
        return 'Loja'


if __name__ == '__main__':
    importar_patrimonios()
