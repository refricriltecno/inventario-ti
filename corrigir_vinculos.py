"""
Script para corrigir vínculos órfãos entre Ativos, E-mails e Softwares
"""

from app import create_app
from app.models import db, Asset, Email, Software
from datetime import datetime

def corrigir_vinculos():
    """Tenta corrigir automaticamente e-mails e softwares órfãos"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*70)
        print("🔧 CORREÇÃO DE VÍNCULOS - Ativos, E-mails e Softwares")
        print("="*70 + "\n")
        
        # 1. Limpar emails órfãos (sem asset_id)
        emails_orfaos = Email.query.filter(Email.asset_id.is_(None)).all()
        if emails_orfaos:
            print(f"⚠️  Encontrados {len(emails_orfaos)} e-mails órfãos (sem asset_id)")
            print("   Opções:")
            print("   1. Deletar e-mails órfãos")
            print("   2. Tentar vincular ao primeiro asset (não recomendado)")
            print("   3. Manter como estão (Requer vínculo manual)")
            opcao = input("\n   Escolha uma opção (1/2/3) [padrão: 3]: ").strip() or "3"
            
            if opcao == "1":
                for email in emails_orfaos:
                    db.session.delete(email)
                    print(f"   ❌ Deletado: {email.endereco}")
                db.session.commit()
                print(f"   ✅ {len(emails_orfaos)} e-mails órfãos deletados\n")
            elif opcao == "2":
                primeiro_asset = Asset.query.first()
                if primeiro_asset:
                    for email in emails_orfaos:
                        email.asset_id = primeiro_asset.id
                        print(f"   🔗 Vinculado: {email.endereco} → {primeiro_asset.patrimonio}")
                    db.session.commit()
                    print(f"   ✅ {len(emails_orfaos)} e-mails vinculados ao primeiro asset\n")
                else:
                    print("   ❌ Nenhum asset disponível para vincular\n")
            else:
                print("   ℹ️  Mantendo e-mails órfãos. Você precisará vincular manualmente.\n")
        else:
            print("✅ Nenhum e-mail órfão encontrado\n")
        
        # 2. Limpar softwares órfãos
        softwares_orfaos = Software.query.filter(Software.asset_id.is_(None)).all()
        if softwares_orfaos:
            print(f"⚠️  Encontrados {len(softwares_orfaos)} softwares órfãos")
            print("   Opções:")
            print("   1. Deletar softwares órfãos")
            print("   2. Tentar vincular ao primeiro asset (não recomendado)")
            print("   3. Manter como estão")
            opcao = input("\n   Escolha uma opção (1/2/3) [padrão: 3]: ").strip() or "3"
            
            if opcao == "1":
                for soft in softwares_orfaos:
                    db.session.delete(soft)
                    print(f"   ❌ Deletado: {soft.nome}")
                db.session.commit()
                print(f"   ✅ {len(softwares_orfaos)} softwares órfãos deletados\n")
            elif opcao == "2":
                primeiro_asset = Asset.query.first()
                if primeiro_asset:
                    for soft in softwares_orfaos:
                        soft.asset_id = primeiro_asset.id
                        print(f"   🔗 Vinculado: {soft.nome} → {primeiro_asset.patrimonio}")
                    db.session.commit()
                    print(f"   ✅ {len(softwares_orfaos)} softwares vinculados\n")
                else:
                    print("   ❌ Nenhum asset disponível\n")
            else:
                print("   ℹ️  Mantendo softwares órfãos.\n")
        else:
            print("✅ Nenhum software órfão encontrado\n")
        
        # 3. Detectar e-mails com asset_id inválido
        emails_invalidos = []
        for email in Email.query.all():
            if email.asset_id and not Asset.query.get(email.asset_id):
                emails_invalidos.append(email)
        
        if emails_invalidos:
            print(f"❌ Encontrados {len(emails_invalidos)} e-mails com asset_id INVÁLIDO")
            print("   Opções:")
            print("   1. Deletar e-mails com asset_id inválido")
            print("   2. Limpar asset_id (deixar órfão)")
            print("   3. Tentar vincular ao primeiro asset")
            opcao = input("\n   Escolha uma opção (1/2/3) [padrão: 1]: ").strip() or "1"
            
            if opcao == "1":
                for email in emails_invalidos:
                    db.session.delete(email)
                    print(f"   ❌ Deletado: {email.endereco}")
                db.session.commit()
                print(f"   ✅ {len(emails_invalidos)} e-mails com asset_id inválido deletados\n")
            elif opcao == "2":
                for email in emails_invalidos:
                    email.asset_id = None
                    print(f"   🔓 Desvinculado: {email.endereco}")
                db.session.commit()
                print(f"   ✅ {len(emails_invalidos)} e-mails desvinculados\n")
            elif opcao == "3":
                primeiro_asset = Asset.query.first()
                if primeiro_asset:
                    for email in emails_invalidos:
                        email.asset_id = primeiro_asset.id
                        print(f"   🔗 Re-vinculado: {email.endereco} → {primeiro_asset.patrimonio}")
                    db.session.commit()
                    print(f"   ✅ {len(emails_invalidos)} e-mails re-vinculados\n")
        else:
            print("✅ Nenhum e-mail com asset_id inválido encontrado\n")
        
        # 4. Detectar softwares com asset_id inválido
        softwares_invalidos = []
        for soft in Software.query.all():
            if soft.asset_id and not Asset.query.get(soft.asset_id):
                softwares_invalidos.append(soft)
        
        if softwares_invalidos:
            print(f"❌ Encontrados {len(softwares_invalidos)} softwares com asset_id INVÁLIDO")
            print("   Opções:")
            print("   1. Deletar softwares com asset_id inválido")
            print("   2. Limpar asset_id")
            print("   3. Vincular ao primeiro asset")
            opcao = input("\n   Escolha uma opção (1/2/3) [padrão: 1]: ").strip() or "1"
            
            if opcao == "1":
                for soft in softwares_invalidos:
                    db.session.delete(soft)
                    print(f"   ❌ Deletado: {soft.nome}")
                db.session.commit()
                print(f"   ✅ {len(softwares_invalidos)} softwares com asset_id inválido deletados\n")
            elif opcao == "2":
                for soft in softwares_invalidos:
                    soft.asset_id = None
                    print(f"   🔓 Desvinculado: {soft.nome}")
                db.session.commit()
                print(f"   ✅ {len(softwares_invalidos)} softwares desvinculados\n")
            elif opcao == "3":
                primeiro_asset = Asset.query.first()
                if primeiro_asset:
                    for soft in softwares_invalidos:
                        soft.asset_id = primeiro_asset.id
                        print(f"   🔗 Re-vinculado: {soft.nome} → {primeiro_asset.patrimonio}")
                    db.session.commit()
                    print(f"   ✅ {len(softwares_invalidos)} softwares re-vinculados\n")
        else:
            print("✅ Nenhum software com asset_id inválido encontrado\n")
        
        print("="*70)
        print("✅ Correção concluída!")
        print("="*70 + "\n")

if __name__ == '__main__':
    corrigir_vinculos()
