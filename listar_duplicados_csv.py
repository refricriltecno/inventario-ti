"""Identificar emails duplicados no CSV e mostrar quais tipos faltam importar"""
import csv
from collections import defaultdict

# Ler emails.csv
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

# Encontrar emails duplicados
print("\n" + "=" * 80)
print("EMAILS DUPLICADOS NO CSV")
print("=" * 80)

duplicados = {k: v for k, v in emails_csv.items() if len(v) > 1}

if not duplicados:
    print("\nNenhum email duplicado encontrado.")
else:
    print(f"\nTotal de emails com múltiplas entradas: {len(duplicados)}\n")
    
    for email, tipos in sorted(duplicados.items()):
        print(f"📧 {email}")
        for i, info in enumerate(tipos, 1):
            print(f"   {i}. {info['tipo'].upper()}")
        print()

# Verificar especificamente tecnologia@refricril.com.br
print("\n" + "=" * 80)
print("VERIFICAR: tecnologia@refricril.com.br")
print("=" * 80)

tech_email = emails_csv.get('tecnologia@refricril.com.br', [])
if tech_email:
    print(f"\nEncontrado {len(tech_email)} entradas:")
    for i, info in enumerate(tech_email, 1):
        print(f"  {i}. Tipo: {info['tipo'].upper()}")
    
    # Mostrar qual deveria estar no banco
    tipos_disponiveis = [info['tipo'] for info in tech_email]
    print(f"\nTipos disponíveis no CSV: {', '.join(t.upper() for t in tipos_disponiveis)}")
else:
    print("\nEmail não encontrado no CSV")

print("\n" + "=" * 80 + "\n")
