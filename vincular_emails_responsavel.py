"""Script para vincular emails aos assets via nome do usuário responsável"""
from app import create_app
from app.models import db, Asset, Email

def vincular_emails_por_responsavel():
    """Vincula emails aos assets procurando pelo nome do responsável"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "=" * 70)
        print("VINCULADOR DE EMAILS POR RESPONSAVEL")
        print("=" * 70)
        
        contador_vinculado = 0
        contador_nao_encontrado = 0
        
        # Buscar emails sem vinculação
        emails_sem_vinculo = Email.query.filter(Email.asset_id == None).all()
        
        print(f"\nProcessando {len(emails_sem_vinculo)} emails sem vinculacao...\n")
        
        for email in emails_sem_vinculo:
            # Extrair primeira parte do email (antes do @)
            usuario = email.usuario.lower()
            
            # Estratégia 1: Procurar por correspondência com o responsável
            # Exemplo: tecnologia@... -> procurar responsável com "tecnologia"
            assets = Asset.query.all()
            encontrado = False
            
            for asset in assets:
                if asset.responsavel and usuario in asset.responsavel.lower():
                    email.asset_id = asset.id
                    db.session.add(email)
                    contador_vinculado += 1
                    print(f"[VINCULADO] {email.endereco} -> {asset.patrimonio} ({asset.responsavel})")
                    encontrado = True
                    break
            
            if not encontrado:
                # Estratégia 2: Procurar por emails conhecidos da filial/setor
                # Exemplo: se o email é financeiro@..., procurar assets do setor "Financeiro"
                setor_mapeado = mapeamento_setor_email(usuario)
                
                if setor_mapeado:
                    asset = Asset.query.filter_by(setor=setor_mapeado).first()
                    if asset:
                        email.asset_id = asset.id
                        db.session.add(email)
                        contador_vinculado += 1
                        print(f"[VINCULADO] {email.endereco} -> {asset.patrimonio} (Setor: {setor_mapeado})")
                        encontrado = True
                
                if not encontrado:
                    contador_nao_encontrado += 1
        
        # Commit
        db.session.commit()
        
        print("\n" + "=" * 70)
        print("VINCULACAO CONCLUIDA!")
        print("=" * 70)
        print(f"Emails vinculados: {contador_vinculado}")
        print(f"Emails nao vinculados: {contador_nao_encontrado}")
        print("=" * 70 + "\n")


def mapeamento_setor_email(usuario):
    """Mapeia nome de email para setor correspondente"""
    mapeamento = {
        'financeiro': 'Financeiro',
        'contabil': 'Contabil / Fiscal',
        'rh': 'RH',
        'compras': 'Compras',
        'logistica': 'Logística',
        'vendas': 'Vendas',
        'ti': 'TI',
        'tecnologia': 'TI',
        'administrativo': 'Administrativo',
    }
    
    for chave, valor in mapeamento.items():
        if chave in usuario:
            return valor
    
    return None


if __name__ == '__main__':
    vincular_emails_por_responsavel()
