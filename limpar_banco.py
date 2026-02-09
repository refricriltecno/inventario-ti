"""Script para limpar completamente o banco de dados e recriar as tabelas"""
from app import create_app
from app.models import db

def limpar_banco():
    """Limpa todas as tabelas e recria a estrutura do banco"""
    app = create_app()
    
    with app.app_context():
        print("🗑️  Removendo todas as tabelas do banco de dados...")
        db.drop_all()
        print("✅ Todas as tabelas foram removidas!")
        
        print("\n🔨 Recriando a estrutura do banco de dados...")
        db.create_all()
        print("✅ Tabelas recriadas com sucesso!")
        
        print("\n" + "="*50)
        print("✨ Banco de dados foi zerado com sucesso!")
        print("="*50)
        print("\nPróximo passo: execute 'python init_db.py' para:")
        print("  - Criar usuário admin padrão")
        print("  - Criar filiais padrão")

if __name__ == '__main__':
    limpar_banco()
