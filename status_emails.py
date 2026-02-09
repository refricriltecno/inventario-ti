"""Verificar status final de emails vinculados"""
from app import create_app
from app.models import db, Email

app = create_app()

with app.app_context():
    total = Email.query.count()
    vinculados = Email.query.filter(Email.asset_id.isnot(None)).count()
    nao_vinculados = Email.query.filter(Email.asset_id.is_(None)).count()
    
    print("\n" + "=" * 60)
    print("STATUS DE VINCULAÇÃO DE EMAILS")
    print("=" * 60)
    print(f"Total de emails: {total}")
    print(f"Vinculados: {vinculados} ({100*vinculados/total:.1f}%)")
    print(f"Não vinculados: {nao_vinculados} ({100*nao_vinculados/total:.1f}%)")
    print("=" * 60 + "\n")
    
    # Amostra de não vinculados
    sem_vinculo = Email.query.filter(Email.asset_id.is_(None)).limit(5).all()
    print("Amostra de emails sem vínculo:")
    for email in sem_vinculo:
        print(f"  ✗ {email.endereco} (tipo: {email.tipo.upper()})")
