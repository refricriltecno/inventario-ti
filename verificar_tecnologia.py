"""Verificar tipo de tecnologia@refricril.com.br após re-import"""
from app import create_app
from app.models import db, Email

app = create_app()

with app.app_context():
    email = Email.query.filter_by(endereco='tecnologia@refricril.com.br').first()
    
    if email:
        print(f"\n✅ Email encontrado:")
        print(f"   Endereço: {email.endereco}")
        print(f"   Tipo: {email.tipo.upper()}")
        print(f"   Asset ID: {email.asset_id}")
        print(f"   Ativo: {email.ativo}\n")
    else:
        print("\n❌ Email não encontrado\n")
