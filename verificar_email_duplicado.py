"""Verificar todas as entradas de um email no banco"""
from app import create_app
from app.models import Email

app = create_app()

with app.app_context():
    emails = Email.query.filter_by(endereco='tecnologia@refricril.com.br').all()
    
    print(f"\nEmails encontrados para 'tecnologia@refricril.com.br': {len(emails)}\n")
    
    for i, e in enumerate(emails, 1):
        print(f"{i}. ID: {e.id}")
        print(f"   Type: {e.tipo}")
        print(f"   Asset ID: {e.asset_id}")
        print(f"   Ativo: {e.ativo}")
        print()
