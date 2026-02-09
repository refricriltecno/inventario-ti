"""Script para importar dados reais com vinculação de emails e Anydesk"""
import csv
import os
from app import create_app
from app.models import db, Filial, Asset, Email

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
    
    primeiro_item = descricao.split('-')[0].strip()
    return primeiro_item if primeiro_item else "Sem Filial"

def importar_patrimonios_com_vinculo():
    """Importa patrimônios com Anydesk e cria vínculo com emails"""
    app = create_app()
    
    with app.app_context():
        print("\n💻 Importando Patrimônios com Anydesk e Emails...")
        
        filiais_criadas = {}
        contador = 0
        erros = 0
        
        with open('patrimonios.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                try:
                    pat = row.get('PAT', '').strip()
                    
                    if not pat or pat == 'PAT':
                        continue
                    
                    # Verificar se já existe
                    asset = Asset.query.filter_by(patrimonio=pat).first()
                    if asset:
                        # Atualizar com novas informações
                        pass
                    else:
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
                            fornecedor='Dell' if 'Optiplex' in str(row.get('Modelo', '')) else 'Diversos',
                            anydesk=row.get('Anydesk', '').strip()
                        )
                        
                        db.session.add(asset)
                        db.session.flush()
                    
                    # Vincular emails ao asset
                    emails_campos = [
                        ('Zimbra', 'zimbra'),
                        ('Conta Google', 'google'),
                        ('Email Secundário', 'google'),
                        ('Conta Google 2', 'google'),
                    ]
                    
                    for campo, tipo in emails_campos:
                        email_addr = row.get(campo, '').strip()
                        
                        if email_addr and '@' in email_addr:
                            # Verificar se email já existe
                            email = Email.query.filter_by(endereco=email_addr).first()
                            if not email:
                                email = Email(
                                    endereco=email_addr,
                                    tipo=tipo,
                                    usuario=email_addr.split('@')[0],
                                    asset_id=asset.id
                                )
                                db.session.add(email)
                            else:
                                # Se email existe mas não está vinculado a este asset, vincular
                                if email.asset_id is None:
                                    email.asset_id = asset.id
                    
                    contador += 1
                    
                    if contador % 50 == 0:
                        db.session.commit()
                        print(f"  ✅ {contador} patrimônios processados")
                
                except Exception as e:
                    erros += 1
                    print(f"  ⚠️  Erro ao processar {pat}: {str(e)}")
            
            db.session.commit()
            
            print(f"\n📊 PATRIMÔNIOS COM ANYDESK E EMAILS")
            print(f"  Total: {contador}")
            print(f"  Filiais: {len(filiais_criadas)}")
            print(f"  Erros: {erros}")

def exibir_resumo():
    """Exibe resumo dos dados"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*70)
        print("📊 RESUMO FINAL DO BANCO DE DADOS")
        print("="*70)
        
        filiais = Filial.query.count()
        assets = Asset.query.count()
        emails = Email.query.count()
        emails_vinculados = Email.query.filter(Email.asset_id.isnot(None)).count()
        assets_com_anydesk = Asset.query.filter(Asset.anydesk.isnot(None)).count()
        
        print(f"✅ Filiais: {filiais}")
        print(f"✅ Patrimônios: {assets}")
        print(f"✅ Patrimônios com Anydesk: {assets_com_anydesk}")
        print(f"✅ Emails: {emails}")
        print(f"✅ Emails Vinculados: {emails_vinculados}")
        print("="*70)
        print("🎉 IMPORTAÇÃO COM VÍNCULO CONCLUÍDA!")
        print("="*70)

if __name__ == '__main__':
    print("="*70)
    print("🔄 IMPORTANDO DADOS COM ANYDESK E VINCULAÇÃO DE EMAILS")
    print("="*70)
    
    importar_patrimonios_com_vinculo()
    exibir_resumo()
