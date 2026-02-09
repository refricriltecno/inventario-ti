"""Script para diagnosticar patrimônios faltando no banco de dados"""
import csv
from app import create_app
from app.models import Asset

def diagnosticar_patrimonios():
    """Verifica quais patrimônios do CSV não foram importados"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "=" * 70)
        print("DIAGNOSTICO DE PATRIMONIOS")
        print("=" * 70)
        
        # Ler patrimônios do CSV
        patrimonios_csv = set()
        
        try:
            with open('patrimonios.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    pat = row.get('PAT', '').strip()
                    if pat and pat != 'PAT':
                        patrimonios_csv.add(pat)
        except FileNotFoundError:
            print("ERRO: Arquivo patrimonios.csv nao encontrado!")
            return
        
        # Ler patrimônios do banco
        assets_banco = Asset.query.all()
        patrimonios_banco = {a.patrimonio for a in assets_banco if a.patrimonio}
        
        # Calcular diferenças
        faltam_importar = patrimonios_csv - patrimonios_banco
        extras_banco = patrimonios_banco - patrimonios_csv
        
        print(f"\nTotal de patrimonios no CSV: {len(patrimonios_csv)}")
        print(f"Total de patrimonios no BANCO: {len(patrimonios_banco)}")
        print(f"Patrimonios FALTANDO importar: {len(faltam_importar)}")
        print(f"Patrimonios EXTRAS no banco: {len(extras_banco)}")
        
        if faltam_importar:
            print("\n" + "-" * 70)
            print("PATRIMONIOS A IMPORTAR (primeiros 30):")
            print("-" * 70)
            for pat in sorted(list(faltam_importar))[:30]:
                print(f"  • {pat}")
            
            if len(faltam_importar) > 30:
                print(f"  ... e mais {len(faltam_importar) - 30} patrimonios")
        
        if extras_banco:
            print("\n" + "-" * 70)
            print("PATRIMONIOS EXTRAS NO BANCO (primeiros 30):")
            print("-" * 70)
            for pat in sorted(list(extras_banco))[:30]:
                print(f"  • {pat}")
            
            if len(extras_banco) > 30:
                print(f"  ... e mais {len(extras_banco) - 30} patrimonios")
        
        # Informações sobre IDs
        print("\n" + "-" * 70)
        print("INFORMACOES SOBRE IDs NO BANCO:")
        print("-" * 70)
        ids = [a.id for a in assets_banco]
        print(f"Quantidade de assets: {len(ids)}")
        print(f"ID minimo: {min(ids) if ids else 'N/A'}")
        print(f"ID maximo: {max(ids) if ids else 'N/A'}")
        print(f"IDs: {sorted(ids)[:20]}")
        if len(ids) > 20:
            print(f"     ... e mais {len(ids) - 20} registros")
        
        print("\n" + "=" * 70 + "\n")


if __name__ == '__main__':
    diagnosticar_patrimonios()
