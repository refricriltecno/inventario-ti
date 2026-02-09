"""Corrigir para o tipo correto do CSV (GOOGLE for tecnologia@refricril.com.br)"""
from app import create_app
from app.models import db, Email
from bcrypt import hashpw, gensalt

app = create_app()

with app.app_context():
    # Deletar o existente
    email = Email.query.filter_by(endereco='tecnologia@refricril.com.br').first()
    if email:
        print(f"❌ Deletando: {email.endereco} (tipo: {email.tipo})")
        db.session.delete(email)
        db.session.commit()
    
    # Re-importar com o tipo correto (GOOGLE - primeira linha)
    novo = Email(
        endereco='tecnologia@refricril.com.br',
        tipo='google',  # O primeiro tipo no CSV
        usuario='tecnologia',
        senha=hashpw('ROF2cr)*&reg505050'.encode('utf-8'), gensalt()),
        ativo=True
    )
    db.session.add(novo)
    db.session.commit()
    
    print(f"✅ Re-importado: {novo.endereco} (tipo: {novo.tipo.upper()})")
    print(f"   Usuario: {novo.usuario}")
    print(f"   ID: {novo.id}\n")
