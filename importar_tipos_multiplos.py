"""Atualizar emails para incluir todos os tipos disponíveis"""
import csv
from collections import defaultdict
from app import create_app
from app.models import db, Email

def importar_todos_tipos_email():
    """Importa todos os tipos de email disponíveis no CSV"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "=" * 80)
        print("IMPORTADOR DE TIPOS DE EMAIL MULTIPLOS")
        print("=" * 80)
        
        # Ler todos os emails do CSV com seus tipos
        emails_csv = defaultdict(list)
        
        with open('emails.csv', 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                endereco = row.get('Conta', '').strip()
                tipo = row.get('Tipo', '').strip().lower()
                senha = row.get('Senha', '').strip()
                
                if endereco and tipo:
                    emails_csv[endereco].append({
                        'tipo': tipo,
                        'senha': senha
                    })
        
        # Processar cada email
        contador_atualizado = 0
        
        for endereco, tipos_lista in sorted(emails_csv.items()):
            if len(tipos_lista) > 1:
                # Email com múltiplos tipos
                email = Email.query.filter_by(endereco=endereco).first()
                
                if email:
                    # Criar string com todos os tipos
                    tipos_disponiveis = ', '.join(sorted(set(t['tipo'].upper() for t in tipos_lista)))
                    
                    # Atualizar observações para incluir todos os tipos
                    obs_atual = email.observacoes or ""
                    
                    # Adicionar tipos disponíveis
                    if "Tipos disponíveis" not in obs_atual:
                        nova_obs = f"{obs_atual}\nTipos disponíveis: {tipos_disponiveis}".strip()
                        email.observacoes = nova_obs
                        db.session.add(email)
                        contador_atualizado += 1
                        
                        print(f"[ATUALIZADO] {endereco}")
                        print(f"             Tipo atual: {email.tipo.upper()}")
                        print(f"             Tipos disponíveis: {tipos_disponiveis}\n")
        
        # Commit
        db.session.commit()
        
        print("=" * 80)
        print(f"Emails atualizados: {contador_atualizado}")
        print("=" * 80)
        print(f"\n💡 Os tipos foram armazenados nas observações dos emails.")
        print(f"   Para usar outro tipo, edite o email e copie a senha do CSV.\n")


if __name__ == '__main__':
    importar_todos_tipos_email()
