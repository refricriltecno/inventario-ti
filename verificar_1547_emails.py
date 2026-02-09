"""Verificar emails vinculados ao PAT 001547"""
from app import create_app
from app.models import db, Email, Asset

app = create_app()

with app.app_context():
    # Buscar o asset 001547
    asset = Asset.query.filter_by(patrimonio='001547').first()
    
    if not asset:
        print("❌ Patrimônio 001547 não encontrado")
    else:
        print(f"\n{'=' * 80}")
        print(f"PATRIMÔNIO: {asset.patrimonio} (ID: {asset.id})")
        print(f"{'=' * 80}")
        print(f"Filial: {asset.filial}")
        print(f"Setor: {asset.setor}")
        print(f"Responsável: {asset.responsavel}")
        print(f"AnyDesk: {asset.anydesk}")
        
        # Buscar emails vinculados
        emails = Email.query.filter_by(asset_id=asset.id).all()
        
        print(f"\n📧 EMAILS VINCULADOS: {len(emails)}")
        print(f"{'=' * 80}\n")
        
        for i, email in enumerate(emails, 1):
            print(f"{i:2d}. {email.endereco}")
            print(f"    Tipo: {email.tipo.upper()}")
            print(f"    Usuario: {email.usuario}\n")
        
        print(f"{'=' * 80}\n")
