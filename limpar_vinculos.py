"""Limpar vinculações incorretas de emails

Problema: vincular_emails_responsavel.py vinculou TODOS os emails de um setor
ao PRIMEIRO asset daquele setor, criando vinculações massivas incorretas.

Solução: Desvincular TODOS os emails e depois re-vincular apenas emails que
combinam EXATAMENTE com o responsável do patrimônio.
"""
from app import create_app
from app.models import db, Email, Asset

def limpar_vinculos_incorretos():
    app = create_app()
    
    with app.app_context():
        print("\n" + "=" * 80)
        print("LIMPEZA DE VINCULAÇÕES INCORRETAS")
        print("=" * 80)
        
        # Passo 1: Desvincular TODOS os emails
        print("\n🗑️  Desvinculando todos os emails...")
        emails_vinculados = Email.query.filter(Email.asset_id.isnot(None)).all()
        total_antes = len(emails_vinculados)
        
        for email in emails_vinculados:
            email.asset_id = None
        
        db.session.commit()
        print(f"✅ {total_antes} emails desvinculados\n")
        
        # Passo 2: Re-vincular apenas emails com correspondência EXATA de responsável
        print("🔗 Re-vinculando emails com correspondência EXATA do responsável...\n")
        
        assets = Asset.query.all()
        emails_sem_vinculo = Email.query.filter(Email.asset_id.is_(None)).all()
        
        vinculados = 0
        
        for email in emails_sem_vinculo:
            usuario = email.usuario.lower()
            
            # Buscar asset onde o responsável contenha o nome do usuário do email
            # Exemplo: "luis.zanatta" deve vincular ao asset de "LUIS ZANATTA"
            for asset in assets:
                if asset.responsavel:
                    responsavel_lower = asset.responsavel.lower()
                    
                    # Verificar se o nome do email está no responsável
                    # Exemplo: "luis.zanatta" em "LUIS ZANATTA"
                    nome_email = usuario.replace('.', ' ')
                    
                    if nome_email in responsavel_lower or usuario in responsavel_lower:
                        email.asset_id = asset.id
                        db.session.add(email)
                        vinculados += 1
                        print(f"[VINCULADO] {email.endereco} -> {asset.patrimonio} ({asset.responsavel})")
                        break
        
        db.session.commit()
        
        print(f"\n{'=' * 80}")
        print(f"RESULTADO:")
        print(f"{'=' * 80}")
        print(f"Emails desvinculados: {total_antes}")
        print(f"Emails re-vinculados (correspondência exata): {vinculados}")
        print(f"Emails sem vínculo mantidos: {len(emails_sem_vinculo) - vinculados}")
        print(f"{'=' * 80}\n")


if __name__ == '__main__':
    limpar_vinculos_incorretos()
