"""Script para popular as filiais no banco de dados"""
from app import create_app
from app.models import db, Filial

def popular_filiais():
    """Insere todas as filiais no banco de dados"""
    app = create_app()
    
    filiais = [
        {'codigo': '00', 'nome': 'Administrativo', 'estado': 'SP'},
        {'codigo': '1', 'nome': 'Matriz', 'estado': 'SP'},
        {'codigo': '2', 'nome': 'CD ES', 'estado': 'ES'},
        {'codigo': '3', 'nome': 'Joinville', 'estado': 'SC'},
        {'codigo': '5', 'nome': 'Londrina', 'estado': 'PR'},
        {'codigo': '6', 'nome': 'Blumenau', 'estado': 'SC'},
        {'codigo': '7', 'nome': 'CD SC', 'estado': 'SC'},
        {'codigo': '8', 'nome': 'POA', 'estado': 'RS'},
        {'codigo': '9', 'nome': 'Floripa', 'estado': 'SC'},
        {'codigo': '10', 'nome': 'São Paulo', 'estado': 'SP'},
        {'codigo': '11', 'nome': 'Loja Vila Velha', 'estado': 'ES'},
        {'codigo': '12', 'nome': 'Itajaí', 'estado': 'SC'},
        {'codigo': '13', 'nome': 'CD PB', 'estado': 'PB'},
        {'codigo': '14', 'nome': 'Goiânia', 'estado': 'GO'},
        {'codigo': '15', 'nome': 'Teresina', 'estado': 'PI'},
        {'codigo': '17', 'nome': 'CD SP', 'estado': 'SP'},
        {'codigo': '18', 'nome': 'Belo Horizonte', 'estado': 'MG'},
        {'codigo': '19', 'nome': 'Salvador', 'estado': 'BA'},
        {'codigo': '20', 'nome': 'Guarulhos', 'estado': 'SP'},
        {'codigo': '21', 'nome': 'Osasco', 'estado': 'SP'},
        {'codigo': '22', 'nome': 'Itaim', 'estado': 'SP'},
        {'codigo': '24', 'nome': 'CD Goiania', 'estado': 'GO'},
        {'codigo': '27', 'nome': 'Brasilia', 'estado': 'DF'},
        {'codigo': '28', 'nome': 'Uberlandia', 'estado': 'MG'},
        {'codigo': '29', 'nome': 'Cuiaba', 'estado': 'MT'},
    ]
    
    with app.app_context():
        print("🏢 Adicionando filiais ao banco de dados...\n")
        
        for filial_data in filiais:
            filial = Filial.query.filter_by(nome=filial_data['nome']).first()
            
            if not filial:
                filial = Filial(
                    nome=filial_data['nome'],
                    estado=filial_data['estado'],
                    ativo=True
                )
                db.session.add(filial)
                print(f"  ✅ {filial_data['codigo']:>2} - {filial_data['nome']:<25} ({filial_data['estado']})")
            else:
                print(f"  ⚠️  {filial_data['codigo']:>2} - {filial_data['nome']:<25} (já existe)")
        
        db.session.commit()
        
        total = Filial.query.count()
        print(f"\n{'='*60}")
        print(f"✨ Total de filiais no sistema: {total}")
        print(f"{'='*60}")

if __name__ == '__main__':
    popular_filiais()
