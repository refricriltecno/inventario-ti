"""Script para importar dados reais de CSVs para o PostgreSQL"""
import csv
import os
from app import create_app
from app.models import db, Filial, Asset, Email
from datetime import datetime

def limpar_banco():
    """Remove dados genéricos criados antes"""
    from app.models import Software, AuditLog
    
    app = create_app()
    with app.app_context():
        print("🗑️  Limpando dados genéricos...")
        # Manter usuários e admin
        db.session.query(AuditLog).delete()
        db.session.query(Software).delete()
        db.session.query(Email).delete()
        db.session.query(Asset).delete()
        db.session.commit()
        print("✅ Dados antigos removidos")

def extrair_filial(descricao):
    """Extrai o nome da filial da descrição do patrimônio"""
    if not descricao:
        return "Sem Filial"
    
    filiais_map = {
        "Matriz": "Matriz",
        "São Paulo": "São Paulo",
        "Guarulhos": "São Paulo (Guarulhos)",
        "Osasco": "São Paulo (Osasco)",
        "Itaim": "São Paulo (Itaim)",
        "Joinville": "Joinville",
        "Blumenau": "Blumenau",
        "Floripa": "Floripa",
        "Florianópolis": "Floripa",
        "Londrina": "Londrina",
        "Teresina": "Teresina",
        "Porto Alegre": "Porto Alegre",
        "Belo Horizonte": "Belo Horizonte",
        "Itajaí": "Itajaí",
        "Vila Velha": "Vila Velha",
        "CD Içara": "CD Içara",
        "CD Paraíba": "CD Paraíba",
        "CD SÃO PAULO": "CD São Paulo",
        "CD São Paulo": "CD São Paulo",
        "CD Vila Velha": "CD Vila Velha",
        "Goiânia": "Goiânia",
        "14 - Goiânia": "Goiânia",
    }
    
    descricao_upper = descricao.upper()
    for key, value in filiais_map.items():
        if key.upper() in descricao_upper:
            return value
    
    # Pega a primeira parte antes do dash
    primeiro_item = descricao.split('-')[0].strip()
    return primeiro_item if primeiro_item else "Sem Filial"

def importar_patrimonios():
    """Importa patrimônios do CSV"""
    app = create_app()
    
    with app.app_context():
        print("\n💻 Importando Patrimônios...")
        
        # Criar filiais automaticamente
        filiais_criadas = {}
        
        with open('patrimonios.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            contador = 0
            erros = 0
            
            for row in reader:
                try:
                    pat = row.get('PAT', '').strip()
                    
                    if not pat or pat == 'PAT':
                        continue
                    
                    # Verificar se já existe
                    if Asset.query.filter_by(patrimonio=pat).first():
                        continue
                    
                    descricao = row.get('Em Uso', '').strip()
                    filial_nome = extrair_filial(descricao)
                    
                    # Criar filial se não existir
                    if filial_nome not in filiais_criadas:
                        filial = Filial.query.filter_by(nome=filial_nome).first()
                        if not filial:
                            filial = Filial(nome=filial_nome, ativo=True)
                            db.session.add(filial)
                            db.session.flush()
                        filiais_criadas[filial_nome] = filial
                    
                    asset = Asset(
                        patrimonio=pat,
                        tipo=row.get('Tipo', 'Desktop').strip() or 'Desktop',
                        marca=row.get('Modelo', '').split()[0] if row.get('Modelo') else 'Desconhecida',
                        modelo=row.get('Modelo', '').strip() or 'Modelo Desconhecido',
                        numero_serie=row.get('Hostname', '').strip() or f"SN-{pat}",
                        filial=filial_nome,
                        setor='Geral',
                        responsavel=descricao[:100] if descricao else 'Não informado',
                        status='Em Uso',
                        observacoes=row.get('Observação', '').strip(),
                        fornecedor='Dell' if 'Optiplex' in str(row.get('Modelo', '')) else 'Diversos'
                    )
                    
                    db.session.add(asset)
                    contador += 1
                    
                    if contador % 50 == 0:
                        print(f"  ✅ {contador} patrimônios importados")
                
                except Exception as e:
                    erros += 1
                    print(f"  ⚠️  Erro ao processar {pat}: {str(e)}")
            
            db.session.commit()
            
            print(f"\n📊 PATRIMÔNIOS IMPORTADOS")
            print(f"  Total: {contador}")
            print(f"  Filiais criadas: {len(filiais_criadas)}")
            print(f"  Erros: {erros}")

def importar_emails():
    """Importa emails do CSV"""
    app = create_app()
    
    with app.app_context():
        print("\n📧 Importando Emails...")
        
        with open('emails.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            contador = 0
            erros = 0
            
            for row in reader:
                try:
                    endereco = row.get('Conta', '').strip()
                    tipo = row.get('Tipo', 'Google').strip().lower()
                    senha = row.get('Senha', '').strip()
                    
                    if not endereco or endereco == 'Conta':
                        continue
                    
                    # Verificar se já existe
                    if Email.query.filter_by(endereco=endereco).first():
                        continue
                    
                    email = Email(
                        endereco=endereco,
                        tipo=tipo if tipo in ['google', 'microsoft', 'zimbra'] else 'google',
                        usuario=endereco.split('@')[0],
                        senha=senha if senha else '***PROTEGIDA***'
                    )
                    
                    db.session.add(email)
                    contador += 1
                    
                    if contador % 50 == 0:
                        print(f"  ✅ {contador} emails importados")
                
                except Exception as e:
                    erros += 1
                    print(f"  ⚠️  Erro ao processar {endereco}: {str(e)}")
            
            db.session.commit()
            
            print(f"\n📊 EMAILS IMPORTADOS")
            print(f"  Total: {contador}")
            print(f"  Erros: {erros}")

def exibir_resumo():
    """Exibe resumo dos dados"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*70)
        print("📊 RESUMO FINAL DO BANCO DE DADOS")
        print("="*70)
        print(f"✅ Filiais: {Filial.query.count()}")
        print(f"✅ Patrimônios: {Asset.query.count()}")
        print(f"✅ Emails: {Email.query.count()}")
        print("="*70)
        print("🎉 IMPORTAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*70)

if __name__ == '__main__':
    print("="*70)
    print("🔄 IMPORTANDO DADOS REAIS DO CSV PARA POSTGRESQL")
    print("="*70)
    
    limpar_banco()
    importar_patrimonios()
    importar_emails()
    exibir_resumo()
