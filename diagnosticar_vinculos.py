"""
Script para diagnosticar e corrigir vínculos entre Ativos, E-mails e Softwares no PostgreSQL
"""

from app import create_app
from app.models import db, Asset, Email, Software
from datetime import datetime

def diagnosticar():
    """Diagnostica problemas de integridade referencial"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*70)
        print("🔍 DIAGNÓSTICO DE INTEGRIDADE - Ativos, E-mails e Softwares")
        print("="*70 + "\n")
        
        # 1. Contar registros
        total_assets = Asset.query.count()
        total_emails = Email.query.count()
        total_softwares = Software.query.count()
        
        print(f"📊 CONTADORES:")
        print(f"   ✓ Assets (Ativos): {total_assets}")
        print(f"   ✓ Emails: {total_emails}")
        print(f"   ✓ Softwares: {total_softwares}\n")
        
        # 2. Verificar emails órfãos (asset_id nulo)
        print(f"📧 ANÁLISE DE E-MAILS:")
        emails_orfaos = Email.query.filter(Email.asset_id.is_(None)).all()
        if emails_orfaos:
            print(f"   ⚠️  {len(emails_orfaos)} e-mails SEM vínculo (asset_id = NULL):")
            for email in emails_orfaos[:5]:  # Mostra até 5
                print(f"       - {email.endereco} (ID: {email.id})")
            if len(emails_orfaos) > 5:
                print(f"       ... e mais {len(emails_orfaos) - 5}")
        else:
            print(f"   ✅ Todos os e-mails têm vínculo com um ativo")
        
        # 3. Verificar emails com asset_id inválido (não existente)
        emails_invalidos = []
        for email in Email.query.all():
            if email.asset_id and not Asset.query.get(email.asset_id):
                emails_invalidos.append(email)
        
        if emails_invalidos:
            print(f"   ❌ {len(emails_invalidos)} e-mails com asset_id INVÁLIDO (não existe):")
            for email in emails_invalidos[:5]:
                print(f"       - {email.endereco} (asset_id: {email.asset_id} - NÃO EXISTE)")
            if len(emails_invalidos) > 5:
                print(f"       ... e mais {len(emails_invalidos) - 5}")
        else:
            print(f"   ✅ Nenhum e-mail com asset_id inválido")
        
        # 4. Verificar softwares órfãos
        print(f"\n💾 ANÁLISE DE SOFTWARES:")
        softwares_orfaos = Software.query.filter(Software.asset_id.is_(None)).all()
        if softwares_orfaos:
            print(f"   ⚠️  {len(softwares_orfaos)} softwares SEM vínculo:")
            for soft in softwares_orfaos[:5]:
                print(f"       - {soft.nome} (ID: {soft.id})")
        else:
            print(f"   ✅ Todos os softwares têm vínculo")
        
        # 5. Verificar softwares com asset_id inválido
        softwares_invalidos = []
        for soft in Software.query.all():
            if soft.asset_id and not Asset.query.get(soft.asset_id):
                softwares_invalidos.append(soft)
        
        if softwares_invalidos:
            print(f"   ❌ {len(softwares_invalidos)} softwares com asset_id INVÁLIDO:")
            for soft in softwares_invalidos[:5]:
                print(f"       - {soft.nome} (asset_id: {soft.asset_id} - NÃO EXISTE)")
        else:
            print(f"   ✅ Nenhum software com asset_id inválido")
        
        # 6. Verificar assets com relacionamentos
        print(f"\n🔗 RELACIONAMENTOS:")
        assets_sem_emails = Asset.query.filter(~Asset.emails.any()).count()
        assets_sem_softwares = Asset.query.filter(~Asset.softwares.any()).count()
        
        print(f"   - {total_assets - assets_sem_emails} assets com e-mails")
        print(f"   - {assets_sem_emails} assets SEM e-mails")
        print(f"   - {total_assets - assets_sem_softwares} assets com softwares")
        print(f"   - {assets_sem_softwares} assets SEM softwares")
        
        # 7. Resumo
        print(f"\n📈 RESUMO:")
        total_problemas = len(emails_orfaos) + len(emails_invalidos) + len(softwares_orfaos) + len(softwares_invalidos)
        if total_problemas == 0:
            print("   ✅ EXCELENTE! Nenhum problema de integridade encontrado.")
        else:
            print(f"   ⚠️  {total_problemas} PROBLEMAS ENCONTRADOS")
            print("\n   Dica: Use o script 'corrigir_vinculos.py' para tentar corrigir automaticamente.")
        
        print("\n" + "="*70 + "\n")

if __name__ == '__main__':
    diagnosticar()
