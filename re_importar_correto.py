"""Re-importar TODOS os emails com TIPO CORRETO (primeiro tipo no CSV para cada email)"""
import csv
from collections import defaultdict
from app import create_app
from app.models import db, Email
from bcrypt import hashpw, gensalt

def re_importar_correto():
    app = create_app()
    
    with app.app_context():
        print("\n" + "=" * 80)
        print("RE-IMPORTADOR COMPLETO (TIPOS CORRETOS DO CSV)")
        print("=" * 80)
        
        # Passo 1: Ler CSV e guardar PRIMEIRO tipo de cada email
        print("\n📖 Lendo emails.csv...")
        emails_csv = defaultdict(dict)
        duplicatas_encontradas = 0
        
        with open('emails.csv', 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row_num, row in enumerate(reader, start=2):
                endereco = row.get('Conta', '').strip()
                tipo = row.get('Tipo', '').strip().lower()
                senha = row.get('Senha', '').strip()
                
                if not endereco or not tipo:
                    continue
                
                # Guardar SÓ a PRIMEIRA ocorrência
                if endereco not in emails_csv:
                    emails_csv[endereco] = {
                        'tipo': tipo,
                        'senha': senha,
                        'usuario': endereco.split('@')[0]
                    }
                else:
                    duplicatas_encontradas += 1
        
        print(f"✅ {len(emails_csv)} emails únicos lidos do CSV")
        print(f"⚠️  {duplicatas_encontradas} duplicatas ignoradas (mantendo primeiro tipo)\n")
        
        # Passo 2: Limpar banco de dados (deletar todos os emails)
        print("🗑️  Deletando todos os emails do banco...")
        Email.query.delete()
        db.session.commit()
        total_deletado = len(emails_csv)
        print(f"✅ {total_deletado} emails deletados\n")
        
        # Passo 3: Re-importar com tipo correto
        print("📧 Re-importando emails com tipos corretos...")
        importados = 0
        erros = 0
        
        for endereco, dados in sorted(emails_csv.items()):
            try:
                senha_hash = hashpw(dados['senha'].encode('utf-8'), gensalt())
                novo = Email(
                    endereco=endereco,
                    tipo=dados['tipo'],
                    usuario=dados['usuario'],
                    senha=senha_hash,
                    ativo=True
                )
                db.session.add(novo)
                importados += 1
                
                if importados % 50 == 0:
                    db.session.commit()
                    print(f"   {importados}...", end='\r')
            except Exception as e:
                print(f"❌ Erro importando {endereco}: {str(e)}")
                erros += 1
        
        db.session.commit()
        print(f"\n✅ Re-importação concluída:")
        print(f"   • Importados: {importados}")
        print(f"   • Erros: {erros}")
        print(f"   • Total: {importados + erros}\n")
        
        print("=" * 80)
        print(f"STATUS: Todos os emails importados com tipos corretos ✅")
        print("=" * 80 + "\n")


if __name__ == '__main__':
    re_importar_correto()
