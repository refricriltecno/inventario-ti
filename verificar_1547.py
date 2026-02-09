"""Verificar dados do patrimonio 1547"""
from app import create_app
from app.models import Asset, Email

app = create_app()

with app.app_context():
    asset = Asset.query.filter_by(patrimonio='001547').first()
    
    if asset:
        print(f"\nAsset encontrado:")
        print(f"  Patrimonio: {asset.patrimonio}")
        print(f"  Setor: {asset.setor}")
        print(f"  Responsavel: {asset.responsavel}")
        print(f"  AnyDesk: {asset.anydesk}")
        print(f"  ID: {asset.id}")
        
        # Verificar emails vinculados
        emails = Email.query.filter_by(asset_id=asset.id).all()
        print(f"\n  Emails vinculados ({len(emails)}):")
        for e in emails:
            print(f"    - {e.endereco} ({e.tipo})")
        
        # Verificar se há email "tecnologia" no banco
        tech_email = Email.query.filter_by(endereco='tecnologia@refricril.com.br').first()
        if tech_email:
            print(f"\nEmail tecnologia@refricril.com.br encontrado:")
            print(f"  ID: {tech_email.id}")
            print(f"  Tipo: {tech_email.tipo}")
            print(f"  Asset ID: {tech_email.asset_id}")
            print(f"  Usuario: {tech_email.usuario}")
    else:
        print("Asset 001547 NAO encontrado no banco")
