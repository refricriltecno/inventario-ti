"""Verificar dados do email no CSV"""
import csv

with open('patrimonios.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row.get('PAT', '').strip() == '001547':
            print("Dados do PAT 001547 no CSV:")
            print(f"  Conta Google: {row.get('Conta Google', '')}")
            print(f"  Zimbra: {row.get('Zimbra', '')}")
            print(f"  Email Secundário: {row.get('Email Secundário', '')}")
            print(f"  Conta Google 2: {row.get('Conta Google 2', '')}")
            break
