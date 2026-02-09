"""Corrigir para Google (primeiro tipo no CSV)"""
from app import create_app
from app.models import db, Email
from bcrypt import hashpw, gensalt

app = create_app()

with app.app_context():
    email = Email.query.filter_by(endereco='tecnologia@refricril.com.br').first()
    if email:
        print(f"❌ Deletando: {email.endereco} (tipo: {email.tipo})")
        db.session.delete(email)
        db.session.commit()
    
    senha_hash = hashpw('ROF2cr)*&reg505050'.encode('utf-8'), gensalt())
    novo = Email(
        endereco='tecnologia@refricril.com.br',
        tipo='google',
        usuario='tecnologia',
        senha=senha_hash,
        ativo=True
    )
    db.session.add(novo)
    db.session.commit()
    
    print(f"\n✅ Re-importado: {novo.endereco}")
    print(f"   Tipo: {novo.tipo.upper()}")
    print(f"   Usuario: {novo.usuario}\n")
