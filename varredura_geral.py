"""Script para fazer varredura geral de todos os patrimônios"""
import csv
from app import create_app
from app.models import Asset, Email

def varredura_completa():
    """Faz varredura completa de todos os patrimônios"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "=" * 100)
        print("VARREDURA COMPLETA DE PATRIMONIOS")
        print("=" * 100)
        
        # Ler dados do CSV
        dados_csv = {}
        with open('patrimonios.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                pat = row.get('PAT', '').strip()
                if pat and pat != 'PAT':
                    dados_csv[pat] = row
        
        print(f"\nTotal de patrimônios no CSV: {len(dados_csv)}")
        
        # Analisar cada patrimônio
        assets = Asset.query.all()
        print(f"Total de patrimônios no BANCO: {len(assets)}")
        
        # Estatísticas
        stats = {
            'com_anydesk': 0,
            'sem_anydesk': 0,
            'com_email': 0,
            'sem_email': 0,
            'com_responsavel': 0,
            'com_observacoes': 0,
        }
        
        problemas = []
        
        print("\n" + "-" * 100)
        print("ANALISE DETALHADA:")
        print("-" * 100)
        
        for asset in assets:
            csv_data = dados_csv.get(asset.patrimonio)
            problemas_asset = []
            
            # Verificar AnyDesk
            if not asset.anydesk:
                stats['sem_anydesk'] += 1
                csv_anydesk = csv_data.get('Anydesk', '').strip() if csv_data else None
                if csv_anydesk:
                    problemas_asset.append(f"AnyDesk faltando (CSV tem: {csv_anydesk})")
            else:
                stats['com_anydesk'] += 1
            
            # Verificar Emails
            emails_vinculados = Email.query.filter_by(asset_id=asset.id).count()
            
            if emails_vinculados == 0:
                stats['sem_email'] += 1
                # Ver se há email no CSV
                csv_email = csv_data.get('Conta Google', '').strip() if csv_data else None
                if csv_email:
                    problemas_asset.append(f"Sem email vinculado (CSV tem: {csv_email})")
            else:
                stats['com_email'] += 1
            
            # Verificar Responsável
            if asset.responsavel and asset.responsavel != 'Sem responsável':
                stats['com_responsavel'] += 1
            
            # Verificar Observações
            if asset.observacoes:
                stats['com_observacoes'] += 1
            
            # Se há problemas, registrar
            if problemas_asset:
                problemas.append({
                    'patrimonio': asset.patrimonio,
                    'id': asset.id,
                    'setor': asset.setor,
                    'responsavel': asset.responsavel,
                    'problemas': problemas_asset,
                    'emails': emails_vinculados,
                    'anydesk': asset.anydesk
                })
        
        # Mostrar problemas
        if problemas:
            print(f"\n⚠️  PATRIMÔNIOS COM PROBLEMAS: {len(problemas)}\n")
            
            # Agrupar por tipo de problema
            por_anydesk = [p for p in problemas if 'AnyDesk' in str(p['problemas'])]
            por_email = [p for p in problemas if 'email' in str(p['problemas']).lower()]
            
            print(f"Sem AnyDesk: {len(por_anydesk)}")
            print(f"Sem Email: {len(por_email)}")
            
            print("\n" + "-" * 100)
            print("AMOSTRA DOS PRIMEIROS 20 PROBLEMAS:")
            print("-" * 100)
            
            for i, p in enumerate(problemas[:20], 1):
                print(f"\n{i}. PAT: {p['patrimonio']} (ID: {p['id']})")
                print(f"   Setor: {p['setor']}")
                print(f"   Responsável: {p['responsavel']}")
                print(f"   AnyDesk: {p['anydesk'] or 'FALTANDO'}")
                print(f"   Emails: {p['emails']}")
                for prob in p['problemas']:
                    print(f"   ⚠️  {prob}")
        
        # Mostrar estatísticas
        print("\n" + "=" * 100)
        print("ESTATISTICAS GERAIS:")
        print("=" * 100)
        print(f"\nAnyDesk:")
        print(f"  ✅ Com AnyDesk: {stats['com_anydesk']} ({100*stats['com_anydesk']/len(assets):.1f}%)")
        print(f"  ❌ Sem AnyDesk: {stats['sem_anydesk']} ({100*stats['sem_anydesk']/len(assets):.1f}%)")
        
        print(f"\nEmails:")
        print(f"  ✅ Com email vinculado: {stats['com_email']} ({100*stats['com_email']/len(assets):.1f}%)")
        print(f"  ❌ Sem email: {stats['sem_email']} ({100*stats['sem_email']/len(assets):.1f}%)")
        
        print(f"\nOutros dados:")
        print(f"  ✅ Com responsável: {stats['com_responsavel']} ({100*stats['com_responsavel']/len(assets):.1f}%)")
        print(f"  ✅ Com observações: {stats['com_observacoes']} ({100*stats['com_observacoes']/len(assets):.1f}%)")
        
        print("\n" + "=" * 100 + "\n")


def verificar_campos_csv_nao_importados():
    """Verifica quais campos do CSV não foram importados para o banco"""
    print("\n" + "=" * 100)
    print("CAMPOS DO CSV NÃO IMPORTADOS")
    print("=" * 100)
    
    print("\nCampos do CSV que existem mas NÃO foram importados para os Assets:")
    campos_nao_importados = [
        'Observação (coluna geral)',
        'Senha Windows',
        'Hostname',
        'Tipo de máquina (Desktop/Notebook)',
        'Modelo',
        'SoftPhone (número)',
        'Zimbra (email)',
        'Conta Google',
        'Email Secundário',
        'Conta Google 2',
        'Hostname (coluna)',
        'Senha BIOS',
        'BitLocker',
        'VPN',
        'Senha VPN',
        'GIX Remoto',
        'Duapi',
        'Domínio',
        'Software 1, 2, 3 (com versões)',
        'Centro de Custo Filial'
    ]
    
    print("\nCampos que PODERIAM ser importados:")
    for i, campo in enumerate(campos_nao_importados, 1):
        print(f"  {i:2d}. {campo}")
    
    print("\n💡 Recomendação: Criar migração do banco para adicionar esses campos")
    print("   ou importá-los no campo 'especificacoes' (JSON).")
    print("\n" + "=" * 100 + "\n")


if __name__ == '__main__':
    varredura_completa()
    verificar_campos_csv_nao_importados()
