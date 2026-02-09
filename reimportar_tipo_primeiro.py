"""Re-importar emails usando o PRIMEIRO tipo do CSV"""
import csv
from collections import defaultdict
from app import create_app
from app.models import db, Email
from bcrypt import hashpw, gensalt

def reimportar_com_tipo_correto():
    """Re-importa emails usando o primeiro tipo que aparece no CSV"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "=" * 80)
        print("RE-IMPORTADOR DE EMAILS (PRIMEIRO TIPO DO CSV)")
        print("=" * 80)
        
        # Ler APENAS a primeira ocorrência de cada email
        emails_csv_primeiro = {}
        
        with open('emails.csv', 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                endereco = row.get('Conta', '').strip()
                tipo = row.get('Tipo', '').strip().lower()
                senha = row.get('Senha', '').strip()
                
                # Só importar a PRIMEIRA ocorrência
                if endereco and tipo and endereco not in emails_csv_primeiro:
                    emails_csv_primeiro[endereco] = {
                        'tipo': tipo,
                        'senha': senha
                    }
        
        # Processar
        contador = 0
        
        for endereco, dados in sorted(emails_csv_primeiro.items()):
            email = Email.query.filter_by(endereco=endereco).first()
            
            if email:
                tipo_novo = dados['tipo']
                tipo_antigo = email.tipo
                
                # Se o tipo é diferente, atualizar
                if tipo_novo != tipo_antigo:
                    email.tipo = tipo_novo
                    if dados['senha']:
                        email.senha = hashpw(dados['senha'].encode('utf-8'), gensalt())
                    db.session.add(email)
                    contador += 1
                    
                    print(f"[ATUALIZADO] {endereco}")
                    print(f"             {tipo_antigo.upper()} -> {tipo_novo.upper()}\n")
        
        # Commit
        db.session.commit()
        
        print("=" * 80)
        print(f"Emails atualizados: {contador}")
        print("=" * 80 + "\n")


if __name__ == '__main__':
    reimportar_com_tipo_correto()
