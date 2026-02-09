"""Script para popular o banco com dados mais completos"""
from app import create_app
from app.models import db, Usuario, Filial, Asset, Celular, Software, Email
from app.auth import hash_password
from datetime import datetime, timedelta
import random

def popular_dados_completos():
    app = create_app()
    
    with app.app_context():
        print("="*60)
        print("🚀 POPULANDO BANCO DE DADOS COM DADOS COMPLETOS")
        print("="*60)
        
        # ========== FILIAIS ==========
        print("\n🏢 Criando Filiais...")
        filiais_data = [
            {'nome': 'Matriz', 'endereco': 'Rua Principal, 100', 'cidade': 'São Paulo', 'estado': 'SP', 'telefone': '(11) 3000-0000'},
            {'nome': 'Filial Centro', 'endereco': 'Av. Paulista, 1000', 'cidade': 'São Paulo', 'estado': 'SP', 'telefone': '(11) 3000-0001'},
            {'nome': 'Filial Rio', 'endereco': 'Av. Rio Branco, 500', 'cidade': 'Rio de Janeiro', 'estado': 'RJ', 'telefone': '(21) 3000-0002'},
            {'nome': 'Filial Belo Horizonte', 'endereco': 'Av. Getúlio Vargas, 1500', 'cidade': 'Belo Horizonte', 'estado': 'MG', 'telefone': '(31) 3000-0003'},
            {'nome': 'Filial Brasília', 'endereco': 'SHIS QI 15, Bloco A', 'cidade': 'Brasília', 'estado': 'DF', 'telefone': '(61) 3000-0004'},
        ]
        
        filiais_criadas = {}
        for filial_data in filiais_data:
            filial = Filial.query.filter_by(nome=filial_data['nome']).first()
            if not filial:
                filial = Filial(**filial_data, ativo=True)
                db.session.add(filial)
                print(f"  ✅ {filial_data['nome']}")
            filiais_criadas[filial_data['nome']] = filial
        
        db.session.commit()
        
        # ========== USUÁRIOS ==========
        print("\n👥 Criando Usuários...")
        usuarios_data = [
            {'username': 'joao.silva', 'nome': 'João Silva', 'filial': 'Matriz', 'email': 'joao.silva@empresa.com', 'permissoes': ['view', 'edit']},
            {'username': 'maria.santos', 'nome': 'Maria Santos', 'filial': 'Filial Centro', 'email': 'maria.santos@empresa.com', 'permissoes': ['view']},
            {'username': 'carlos.lima', 'nome': 'Carlos Lima', 'filial': 'Filial Rio', 'email': 'carlos.lima@empresa.com', 'permissoes': ['view', 'edit']},
            {'username': 'ana.costa', 'nome': 'Ana Costa', 'filial': 'Filial Belo Horizonte', 'email': 'ana.costa@empresa.com', 'permissoes': ['view']},
            {'username': 'pedro.oliveira', 'nome': 'Pedro Oliveira', 'filial': 'Filial Brasília', 'email': 'pedro.oliveira@empresa.com', 'permissoes': ['view', 'edit', 'delete']},
            {'username': 'fabiana.dias', 'nome': 'Fabiana Dias', 'filial': 'Matriz', 'email': 'fabiana.dias@empresa.com', 'permissoes': ['admin']},
        ]
        
        for user_data in usuarios_data:
            if not Usuario.query.filter_by(username=user_data['username']).first():
                user = Usuario(
                    username=user_data['username'],
                    password=hash_password('senha123'),
                    nome=user_data['nome'],
                    filial=user_data['filial'],
                    email=user_data['email'],
                    permissoes=user_data['permissoes'],
                    ativo=True
                )
                db.session.add(user)
                print(f"  ✅ {user_data['nome']}")
        
        db.session.commit()
        
        # ========== COMPUTADORES/ASSETS ==========
        print("\n💻 Criando Computadores...")
        marcas = ['Dell', 'HP', 'Lenovo', 'Asus', 'Apple']
        modelos = {
            'Dell': ['OptiPlex 3090', 'Latitude 5530', 'XPS 13'],
            'HP': ['EliteDesk 800', 'ProBook 450', 'Pavilion 15'],
            'Lenovo': ['ThinkCentre M90', 'ThinkPad L15', 'IdeaPad 5'],
            'Asus': ['VivoPC M-series', 'ExpertBook', 'VivoBook'],
            'Apple': ['MacBook Pro 16', 'iMac 27', 'Mac Mini']
        }
        setores = ['TI', 'Financeiro', 'RH', 'Vendas', 'Operações', 'Marketing', 'Administrativo']
        
        filiais_list = list(filiais_criadas.values())
        contador = 1
        
        for i in range(50):
            patrimonio = f"COMP-{i+1:05d}"
            if not Asset.query.filter_by(patrimonio=patrimonio).first():
                marca = random.choice(marcas)
                modelo = random.choice(modelos[marca])
                filial = random.choice(filiais_list)
                
                asset = Asset(
                    patrimonio=patrimonio,
                    tipo='Notebook' if i % 3 == 0 else 'Desktop',
                    marca=marca,
                    modelo=modelo,
                    numero_serie=f"SN{random.randint(100000, 999999)}",
                    filial=filial.nome,
                    setor=random.choice(setores),
                    responsavel=random.choice([u['nome'] for u in usuarios_data]),
                    status='Em Uso' if random.random() > 0.2 else 'Manutenção',
                    especificacoes={
                        'processador': random.choice(['Intel Core i5', 'Intel Core i7', 'AMD Ryzen 5', 'AMD Ryzen 7']),
                        'memoria_ram': f"{random.choice([8, 16, 32])} GB",
                        'armazenamento': f"{random.choice([256, 512, 1024])} GB SSD",
                        'sistema_operacional': 'Windows 10' if random.random() > 0.3 else 'Windows 11'
                    },
                    dt_compra=(datetime.now() - timedelta(days=random.randint(30, 1095))).date(),
                    valor=round(random.uniform(2000, 8000), 2),
                    fornecedor=random.choice(['Dell Brasil', 'HP Brasil', 'Lenovo Brasil', 'Asus Brasil', 'Apple Brasil'])
                )
                db.session.add(asset)
                if contador % 10 == 0:
                    print(f"  ✅ {contador} computadores criados")
                contador += 1
        
        db.session.commit()
        
        # ========== CELULARES ==========
        print("\n📱 Criando Celulares...")
        marcas_cel = ['iPhone', 'Samsung', 'Motorola', 'LG', 'Xiaomi']
        operadoras = ['Vivo', 'Claro', 'Oi', 'Tim', 'Algar']
        
        contador = 1
        for i in range(40):
            patrimonio = f"CEL-{i+1:04d}"
            if not Celular.query.filter_by(patrimonio=patrimonio).first():
                filial = random.choice(filiais_list)
                
                celular = Celular(
                    patrimonio=patrimonio,
                    filial=filial.nome,
                    modelo=f"{random.choice(marcas_cel)} {random.choice(['12', '13', '14', 'S21', 'S22', 'G100', 'Note'])}",
                    imei=f"{random.randint(100000000000000, 999999999999999)}",
                    numero=f"(11) 9{random.randint(90000000, 99999999)}",
                    operadora=random.choice(operadoras),
                    responsavel=random.choice([u['nome'] for u in usuarios_data]),
                    status='Em Uso' if random.random() > 0.1 else 'Inativo'
                )
                db.session.add(celular)
                if contador % 10 == 0:
                    print(f"  ✅ {contador} celulares criados")
                contador += 1
        
        db.session.commit()
        
        # ========== SOFTWARES ==========
        print("\n💿 Criando Softwares...")
        softwares_data = [
            {'nome': 'Microsoft Office 365', 'versao': '2024', 'tipo_licenca': 'Assinatura', 'custo_anual': 99.90},
            {'nome': 'Adobe Creative Cloud', 'versao': '2024', 'tipo_licenca': 'Assinatura', 'custo_anual': 299.90},
            {'nome': 'Windows 10 Pro', 'versao': '22H2', 'tipo_licenca': 'Perpetua', 'custo_anual': 0},
            {'nome': 'Windows 11 Pro', 'versao': '23H2', 'tipo_licenca': 'Perpetua', 'custo_anual': 0},
            {'nome': 'Kaspersky Endpoint Security', 'versao': '13', 'tipo_licenca': 'Assinatura', 'custo_anual': 150.00},
            {'nome': 'TeamViewer', 'versao': '15', 'tipo_licenca': 'Assinatura', 'custo_anual': 49.99},
            {'nome': 'VS Code', 'versao': '1.85', 'tipo_licenca': 'Gratuito', 'custo_anual': 0},
            {'nome': 'AutoCAD', 'versao': '2024', 'tipo_licenca': 'Assinatura', 'custo_anual': 600.00},
            {'nome': 'Slack', 'versao': 'Pro', 'tipo_licenca': 'Assinatura', 'custo_anual': 12.50},
            {'nome': 'Zoom', 'versao': 'Pro', 'tipo_licenca': 'Assinatura', 'custo_anual': 15.99},
        ]
        
        assets = Asset.query.all()
        contador = 1
        
        for software_data in softwares_data:
            for _ in range(5):  # 5 instalações de cada software
                asset = random.choice(assets)
                software = Software(
                    nome=software_data['nome'],
                    versao=software_data['versao'],
                    asset_id=asset.id,
                    tipo_licenca=software_data['tipo_licenca'],
                    chave_licenca=f"KEY-{random.randint(1000000000, 9999999999)}",
                    dt_instalacao=(datetime.now() - timedelta(days=random.randint(30, 730))).date(),
                    dt_vencimento=(datetime.now() + timedelta(days=random.randint(30, 365))).date(),
                    custo_anual=software_data['custo_anual'],
                    renovacao_automatica=random.choice([True, False])
                )
                db.session.add(software)
                if contador % 20 == 0:
                    print(f"  ✅ {contador} softwares criados")
                contador += 1
        
        db.session.commit()
        
        # ========== EMAILS ==========
        print("\n📧 Criando Emails...")
        dominios = ['empresa.com', 'empresa.com.br', 'group.empresa.com']
        tipos_email = ['google', 'zimbra', 'outlook']
        
        contador = 1
        for i in range(50):
            nomes = ['joao', 'maria', 'carlos', 'ana', 'pedro', 'fabiana', 'lucas', 'julia', 'gabriel', 'isabella']
            sobrenomes = ['silva', 'santos', 'lima', 'costa', 'oliveira', 'dias', 'pereira', 'ferreira', 'gomes', 'martins']
            
            endereco = f"{random.choice(nomes)}.{random.choice(sobrenomes)}@{random.choice(dominios)}"
            
            if not Email.query.filter_by(endereco=endereco).first():
                assets_disponiveis = Asset.query.all()
                asset = random.choice(assets_disponiveis) if assets_disponiveis else None
                
                email = Email(
                    endereco=endereco,
                    tipo=random.choice(tipos_email),
                    asset_id=asset.id if asset else None,
                    usuario=endereco.split('@')[0],
                    senha='***SENHA_PROTEGIDA***',
                    recuperacao=f"{random.choice(nomes)}{random.randint(10, 99)}@gmail.com"
                )
                db.session.add(email)
                if contador % 15 == 0:
                    print(f"  ✅ {contador} emails criados")
                contador += 1
        
        db.session.commit()
        
        # ========== RESUMO ==========
        print("\n" + "="*60)
        print("📊 RESUMO DOS DADOS CRIADOS")
        print("="*60)
        print(f"✅ Filiais: {Filial.query.count()}")
        print(f"✅ Usuários: {Usuario.query.count()}")
        print(f"✅ Computadores: {Asset.query.count()}")
        print(f"✅ Celulares: {Celular.query.count()}")
        print(f"✅ Softwares: {Software.query.count()}")
        print(f"✅ Emails: {Email.query.count()}")
        print("="*60)
        print("🎉 BANCO DE DADOS POPULADO COM SUCESSO!")
        print("="*60)

if __name__ == '__main__':
    popular_dados_completos()
