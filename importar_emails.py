"""Script para importar emails do arquivo CSV e vinculá-los aos assets"""
import csv
import os
import sys
from app import create_app
from app.models import db, Email, Asset
from bcrypt import hashpw, gensalt

# Configurar encoding para Windows
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def importar_emails_do_csv():
    """Importa emails do arquivo emails.csv e os vincula aos assets"""
    app = create_app()
    
    with app.app_context():
        print("\n📧 Iniciando importação de emails...")
        print("=" * 60)
        
        contador_importados = 0
        contador_atualizados = 0
        contador_erros = 0
        emails_por_tipo = {}
        
        try:
            with open('emails.csv', 'r', encoding='utf-8-sig') as f:  # utf-8-sig remove BOM
                reader = csv.DictReader(f, delimiter=';')
                
                # Verificar se tem cabeçalho
                if not reader.fieldnames:
                    print("Erro ao ler arquivo CSV")
                    return
                
                # Verificar se tem o campo Tipo
                if 'Tipo' not in reader.fieldnames:
                    print("Erro: Arquivo CSV nao tem o formato esperado (Tipo;Conta;Senha)")
                    print(f"Campos detectados: {reader.fieldnames}")
                    return
                
                for idx, row in enumerate(reader, start=2):  # Começa em 2 (linha 1 é cabeçalho)
                    try:
                        tipo = row.get('Tipo', '').strip().lower()
                        conta = row.get('Conta', '').strip()
                        senha = row.get('Senha', '').strip()
                        
                        # Validação básica
                        if not conta or not tipo:
                            print(f"AVISO Linha {idx}: Faltam dados obrigatorios (Tipo ou Conta). Pulando...")
                            contador_erros += 1
                            continue
                        
                        # Normalizar tipo
                        tipo_normalizado = normalizar_tipo(tipo)
                        
                        # Extrair usuário da conta (sem domínio)
                        usuario = conta.split('@')[0] if '@' in conta else conta
                        
                        # Verificar se email já existe
                        email_existente = Email.query.filter_by(endereco=conta).first()
                        
                        if email_existente:
                            # Atualizar
                            if senha:
                                email_existente.senha = hashpw(senha.encode('utf-8'), gensalt())
                            email_existente.tipo = tipo_normalizado
                            email_existente.usuario = usuario
                            db.session.add(email_existente)
                            contador_atualizados += 1
                            print(f"[ATUALIZADO] Linha {idx}: Email {conta}")
                        else:
                            # Criar novo email
                            novo_email = Email(
                                endereco=conta,
                                tipo=tipo_normalizado,
                                usuario=usuario,
                                senha=hashpw(senha.encode('utf-8'), gensalt()) if senha else None,
                                ativo=True
                            )
                            db.session.add(novo_email)
                            contador_importados += 1
                            print(f"[IMPORTADO] Linha {idx}: Email {conta} ({tipo_normalizado})")
                        
                        # Contabilizar por tipo
                        emails_por_tipo[tipo_normalizado] = emails_por_tipo.get(tipo_normalizado, 0) + 1
                        
                    except Exception as e:
                        print(f"ERRO Linha {idx}: {str(e)}")
                        contador_erros += 1
                        continue
                
                # Commit
                try:
                    db.session.commit()
                    print("\n" + "=" * 60)
                    print("IMPORTACAO CONCLUIDA COM SUCESSO!")
                    print("=" * 60)
                    print(f"Estatisticas:")
                    print(f"   Emails importados: {contador_importados}")
                    print(f"   Emails atualizados: {contador_atualizados}")
                    print(f"   Erros: {contador_erros}")
                    print(f"\nDistribuicao por tipo:")
                    for tipo, qtd in sorted(emails_por_tipo.items()):
                        print(f"   * {tipo.upper()}: {qtd} email(s)")
                    print("=" * 60 + "\n")
                except Exception as e:
                    db.session.rollback()
                    print(f"\nERRO ao confirmar importacao: {str(e)}\n")
                    
        except FileNotFoundError:
            print("ERRO: Arquivo 'emails.csv' nao encontrado!")
            return
        except Exception as e:
            print(f"ERRO geral: {str(e)}")
            return


def normalizar_tipo(tipo_str):
    """Normaliza o tipo de email para formato padrão"""
    tipo_map = {
        'google': 'google',
        'microsoft': 'microsoft',
        'zimbra': 'zimbra',
        'matriz': 'matriz',
        'canon': 'canon',
    }
    
    tipo_lower = tipo_str.lower().strip()
    return tipo_map.get(tipo_lower, tipo_lower)


def vincular_emails_aos_assets():
    """
    Vincula emails aos assets com base em correspondência de nomes
    Pode ser usado se houver padrão no nome do email que corresponda ao asset
    """
    app = create_app()
    
    with app.app_context():
        print("\nTentando vincular emails aos assets...")
        
        emails = Email.query.filter(Email.asset_id == None).all()
        
        for email in emails:
            # Tentar encontrar asset por correspondência de nome
            # Exemplo: se email é 'patrimonio123@company.com' e existe asset com patrimonio 'PAT-123'
            usuario = email.usuario.lower()
            
            # Procurar por padrões comuns
            assets_candidatos = Asset.query.filter(
                Asset.patrimonio.ilike(f'%{usuario}%')
            ).all()
            
            if len(assets_candidatos) == 1:
                email.asset_id = assets_candidatos[0].id
                db.session.add(email)
                print(f"[VINCULADO] {email.endereco} -> {assets_candidatos[0].patrimonio}")
        
        db.session.commit()
        print("Vinculo concluido!\n")


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("IMPORTADOR DE EMAILS")
    print("=" * 60)
    
    # Executar importação
    importar_emails_do_csv()
    
    # Opcional: vincular emails aos assets
    # Descomente a linha abaixo se quiser tentar vincular automaticamente
    # vincular_emails_aos_assets()
