"""Script para inicializar o banco de dados PostgreSQL"""
from app import create_app
from app.models import db, Usuario, Filial
from app.auth import hash_password

def init_db():
    """Cria todas as tabelas no banco de dados"""
    app = create_app()
    
    with app.app_context():
        print("🔨 Criando tabelas no banco de dados...")
        db.create_all()
        print("✅ Tabelas criadas com sucesso!")
        
        # Verificar se já existe usuário admin
        admin = Usuario.query.filter_by(username='admin').first()
        
        if not admin:
            print("\n👤 Criando usuário administrador padrão...")
            admin = Usuario(
                username='admin',
                password=hash_password('admin123'),
                nome='Administrador',
                email='admin@inventario.com',
                filial='Matriz',
                permissoes=['admin', 'view', 'edit', 'delete'],
                ativo=True
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Usuário 'admin' criado com senha 'admin123'")
        else:
            print("\n⚠️  Usuário 'admin' já existe")
        
        # Criar filiais padrão se não existirem
        filiais_padrao = [
            {'nome': 'Matriz', 'cidade': 'São Paulo', 'estado': 'SP'},
            {'nome': 'Filial 1', 'cidade': 'Rio de Janeiro', 'estado': 'RJ'},
            {'nome': 'Filial 2', 'cidade': 'Belo Horizonte', 'estado': 'MG'},
        ]
        
        print("\n🏢 Verificando filiais...")
        for filial_data in filiais_padrao:
            filial = Filial.query.filter_by(nome=filial_data['nome']).first()
            if not filial:
                filial = Filial(**filial_data)
                db.session.add(filial)
                print(f"  ✅ Filial '{filial_data['nome']}' criada")
            else:
                print(f"  ⚠️  Filial '{filial_data['nome']}' já existe")
        
        db.session.commit()
        
        print("\n" + "="*50)
        print("🎉 Banco de dados inicializado com sucesso!")
        print("="*50)
        print("\n📝 Credenciais de acesso:")
        print("   Usuário: admin")
        print("   Senha: admin123")
        print("\n🌐 Servidor PostgreSQL:")
        print("   Host: 10.1.1.248")
        print("   Database: inventario-ti")
        print("   User: user_inventario")
        print("="*50)

if __name__ == '__main__':
    init_db()
