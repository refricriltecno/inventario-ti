"""Script para vincular emails aos assets/computadores"""
import sys
import io
from app import create_app
from app.models import db, Email, Asset

# Configurar encoding para Windows
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def vincular_emails_aos_assets():
    """
    Vincula emails aos assets com base em correspondência de nomes
    Estratégias:
    1. Se o email contém parte do número de patrimônio do asset
    2. Se o email contém o nome/descrição do usuário responsável
    """
    app = create_app()
    
    with app.app_context():
        print("\n" + "=" * 60)
        print("VINCULADOR DE EMAILS A ASSETS")
        print("=" * 60)
        print("\nTentando vincular emails aos assets...")
        
        emails_vinculados = 0
        emails_sem_vinculo = 0
        
        # Trazer todos os assets
        assets = Asset.query.all()
        
        if not assets:
            print("Nenhum asset encontrado no banco de dados.")
            return
        
        # Processar cada email
        emails = Email.query.filter(Email.asset_id == None).all()
        
        print(f"Total de emails sem vinculo: {len(emails)}\n")
        
        for email in emails:
            usuario = email.usuario.lower()
            endereco = email.endereco.lower()
            
            # Estratégia 1: Procurar por email no responsável do asset
            asset_encontrado = Asset.query.filter(
                Asset.responsavel.ilike(f'%{usuario}%')
            ).first()
            
            if asset_encontrado:
                email.asset_id = asset_encontrado.id
                db.session.add(email)
                emails_vinculados += 1
                print(f"[VINCULADO] {email.endereco}")
                print(f"           -> {asset_encontrado.patrimonio} ({asset_encontrado.responsavel})\n")
                continue
            
            # Estratégia 2: Procurar por padrão numérico no email que corresponda a patrimônio
            import re
            numeros = re.findall(r'\d+', usuario)
            
            if numeros:
                for num in numeros:
                    asset_encontrado = Asset.query.filter(
                        Asset.patrimonio.ilike(f'%{num}%')
                    ).first()
                    
                    if asset_encontrado:
                        email.asset_id = asset_encontrado.id
                        db.session.add(email)
                        emails_vinculados += 1
                        print(f"[VINCULADO] {email.endereco}")
                        print(f"           -> {asset_encontrado.patrimonio}\n")
                        break
        
        if emails_vinculados > 0:
            db.session.commit()
            print("=" * 60)
            print(f"Emails vinculados: {emails_vinculados}")
            print(f"Emails ainda sem vinculo: {len(emails) - emails_vinculados}")
            print("=" * 60 + "\n")
        else:
            print("\nNenhuma correspondência encontrada para vinculacao automatica.")
            print("\nVoce pode vincular manualmente atraves da API:\n")
            print("  PUT /api/emails/<id>")
            print("  { 'asset_id': <asset_id> }\n")


def vincular_email_manual(email_id, asset_id):
    """Vincula um email específico a um asset específico"""
    app = create_app()
    
    with app.app_context():
        email = Email.query.get(email_id)
        asset = Asset.query.get(asset_id)
        
        if not email or not asset:
            print("Email ou Asset nao encontrado.")
            return False
        
        email.asset_id = asset.id
        db.session.commit()
        
        print(f"Email {email.endereco} vinculado a {asset.patrimonio}")
        return True


if __name__ == '__main__':
    vincular_emails_aos_assets()
