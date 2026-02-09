"""Script para popular o banco de dados com dados de exemplo"""
from app import create_app
from app.models import db, Asset, Celular, Software, Email, Usuario
from datetime import datetime, date, timedelta
from app.auth import hash_password
import random

def popular_dados():
    """Popula o banco com dados de exemplo"""
    app = create_app()
    
    with app.app_context():
        print("📊 Populando banco de dados com dados de exemplo...\n")
        
        # Criar usuários adicionais
        print("👥 Criando usuários...")
        usuarios = [
            {'username': 'joao.silva', 'nome': 'João Silva', 'filial': 'Matriz', 'email': 'joao@empresa.com'},
            {'username': 'maria.santos', 'nome': 'Maria Santos', 'filial': 'Filial 1', 'email': 'maria@empresa.com'},
            {'username': 'carlos.lima', 'nome': 'Carlos Lima', 'filial': 'Filial 2', 'email': 'carlos@empresa.com'},
        ]
        
        for user_data in usuarios:
            if not Usuario.query.filter_by(username=user_data['username']).first():
                user = Usuario(
                    username=user_data['username'],
                    password=hash_password('senha123'),
                    nome=user_data['nome'],
                    filial=user_data['filial'],
                    email=user_data['email'],
                    permissoes=['view', 'edit'],
                    ativo=True
                )
                db.session.add(user)
                print(f"  ✅ Usuário {user_data['username']} criado")
        
        db.session.commit()
        
        # Criar assets (computadores)
        print("\n💻 Criando computadores...")
        marcas = ['Dell', 'HP', 'Lenovo', 'Asus']
        processadores = ['Intel Core i5-11400', 'Intel Core i7-12700', 'AMD Ryzen 5 5600', 'AMD Ryzen 7 5800']
        filiais = ['Matriz', 'Filial 1', 'Filial 2']
        setores = ['TI', 'Financeiro', 'RH', 'Vendas', 'Operações']
        
        for i in range(1, 21):
            patrimonio = f"COMP-{i:04d}"
            if not Asset.query.filter_by(patrimonio=patrimonio).first():
                asset = Asset(
                    patrimonio=patrimonio,
                    tipo='Computador',
                    marca=random.choice(marcas),
                    modelo=f'OptiPlex 3000',
                    numero_serie=f'SN{i:06d}',
                    filial=random.choice(filiais),
                    setor=random.choice(setores),
                    responsavel=random.choice(['João Silva', 'Maria Santos', 'Carlos Lima']),
                    status='Ativo',
                    especificacoes={
                        'processador': random.choice(processadores),
                        'ram': random.choice(['8GB', '16GB', '32GB']),
                        'hd': random.choice(['256GB SSD', '512GB SSD', '1TB SSD']),
                        'so': 'Windows 11 Pro'
                    },
                    dt_compra=date.today() - timedelta(days=random.randint(30, 365)),
                    dt_garantia=date.today() + timedelta(days=random.randint(365, 1095)),
                    valor=random.randint(2500, 5000)
                )
                db.session.add(asset)
                print(f"  ✅ Computador {patrimonio} criado")
        
        db.session.commit()
        
        # Criar celulares
        print("\n📱 Criando celulares...")
        modelos_cel = ['iPhone 13 Pro', 'iPhone 14', 'Samsung Galaxy S23', 'Xiaomi Mi 11', 'Motorola Edge 40']
        operadoras = ['Vivo', 'Claro', 'TIM', 'Oi']
        
        for i in range(1, 16):
            patrimonio = f"CEL-{i:03d}"
            if not Celular.query.filter_by(patrimonio=patrimonio).first():
                celular = Celular(
                    patrimonio=patrimonio,
                    filial=random.choice(filiais),
                    modelo=random.choice(modelos_cel),
                    imei=f"{random.randint(100000000000000, 999999999999999)}",
                    numero=f"(11) 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                    operadora=random.choice(operadoras),
                    responsavel=random.choice(['João Silva', 'Maria Santos', 'Carlos Lima', 'Pedro Alves']),
                    status='Ativo',
                    dt_compra=date.today() - timedelta(days=random.randint(30, 730)),
                    valor=random.randint(1500, 6000)
                )
                db.session.add(celular)
                print(f"  ✅ Celular {patrimonio} criado")
        
        db.session.commit()
        
        # Criar softwares
        print("\n💿 Criando softwares...")
        softwares_lista = [
            {'nome': 'Microsoft Office 365', 'versao': '2024', 'tipo_licenca': 'Corporativa'},
            {'nome': 'Adobe Creative Cloud', 'versao': '2024', 'tipo_licenca': 'Corporativa'},
            {'nome': 'AutoCAD', 'versao': '2024', 'tipo_licenca': 'Corporativa'},
            {'nome': 'Windows 11 Pro', 'versao': '23H2', 'tipo_licenca': 'OEM'},
            {'nome': 'Antivírus Kaspersky', 'versao': '2024', 'tipo_licenca': 'Corporativa'},
        ]
        
        assets = Asset.query.limit(10).all()
        for asset in assets:
            # Cada computador recebe 2-3 softwares
            num_softwares = random.randint(2, 3)
            softwares_selecionados = random.sample(softwares_lista, num_softwares)
            
            for soft_data in softwares_selecionados:
                dt_instalacao = date.today() - timedelta(days=random.randint(30, 365))
                dt_vencimento = date.today() + timedelta(days=random.randint(-30, 730))
                
                software = Software(
                    nome=soft_data['nome'],
                    versao=soft_data['versao'],
                    asset_id=asset.id,
                    tipo_licenca=soft_data['tipo_licenca'],
                    chave_licenca=f"XXXXX-XXXXX-XXXXX-{random.randint(10000, 99999)}",
                    dt_instalacao=dt_instalacao,
                    dt_vencimento=dt_vencimento,
                    custo_anual=random.choice([0, 499, 999, 1499, 2999]),
                    renovacao_automatica=random.choice([True, False]),
                    ativo=True
                )
                db.session.add(software)
        
        db.session.commit()
        print(f"  ✅ Softwares criados e vinculados aos computadores")
        
        # Criar emails
        print("\n📧 Criando emails...")
        dominios = ['@empresa.com', '@empresa.com.br']
        tipos = ['google', 'zimbra']
        
        nomes = ['joao.silva', 'maria.santos', 'carlos.lima', 'ana.souza', 'pedro.alves', 
                 'julia.costa', 'marcos.oliveira', 'fernanda.martins']
        
        assets_com_email = Asset.query.limit(8).all()
        for i, asset in enumerate(assets_com_email):
            if i < len(nomes):
                endereco = nomes[i] + random.choice(dominios)
                if not Email.query.filter_by(endereco=endereco).first():
                    email = Email(
                        endereco=endereco,
                        tipo=random.choice(tipos),
                        asset_id=asset.id,
                        usuario=nomes[i],
                        senha='SenhaSegura@123',  # Em produção usar criptografia
                        recuperacao=f"{nomes[i]}.pessoal@gmail.com",
                        ativo=True
                    )
                    db.session.add(email)
                    print(f"  ✅ Email {endereco} criado")
        
        db.session.commit()
        
        print("\n" + "="*50)
        print("🎉 Banco de dados populado com sucesso!")
        print("="*50)
        print("\n📊 Estatísticas:")
        print(f"   👥 Usuários: {Usuario.query.count()}")
        print(f"   💻 Computadores: {Asset.query.count()}")
        print(f"   📱 Celulares: {Celular.query.count()}")
        print(f"   💿 Softwares: {Software.query.count()}")
        print(f"   📧 Emails: {Email.query.count()}")
        print("="*50)

if __name__ == '__main__':
    popular_dados()
