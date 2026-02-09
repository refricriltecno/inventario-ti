"""Script para importar AnyDesk do CSV para os assets"""
import csv
from app import create_app
from app.models import db, Asset

def importar_anydesk():
    """Importa AnyDesk do CSV patrimonios.csv para os assets"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "=" * 70)
        print("IMPORTADOR DE ANYDESK")
        print("=" * 70)
        
        contador_atualizado = 0
        contador_nao_encontrado = 0
        
        try:
            with open('patrimonios.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for idx, row in enumerate(reader, start=2):
                    try:
                        pat = row.get('PAT', '').strip()
                        anydesk = row.get('Anydesk', '').strip()
                        
                        if not pat or pat == 'PAT':
                            continue
                        
                        # Procurar asset no banco
                        asset = Asset.query.filter_by(patrimonio=pat).first()
                        
                        if not asset:
                            contador_nao_encontrado += 1
                            continue
                        
                        # Atualizar AnyDesk se houver valor
                        if anydesk and anydesk != asset.anydesk:
                            asset.anydesk = anydesk
                            db.session.add(asset)
                            contador_atualizado += 1
                            print(f"[ATUALIZADO] PAT {pat}: AnyDesk = {anydesk}")
                    
                    except Exception as e:
                        print(f"ERRO Linha {idx}: {str(e)}")
                        continue
                
                # Commit
                db.session.commit()
                
                print("\n" + "=" * 70)
                print("ATUALIZACAO CONCLUIDA!")
                print("=" * 70)
                print(f"AnyDesk atualizados: {contador_atualizado}")
                print(f"Assets nao encontrados: {contador_nao_encontrado}")
                print("=" * 70 + "\n")
                
        except FileNotFoundError:
            print("ERRO: Arquivo patrimonios.csv nao encontrado!")
            return
        except Exception as e:
            db.session.rollback()
            print(f"ERRO geral: {str(e)}")
            return


if __name__ == '__main__':
    importar_anydesk()
