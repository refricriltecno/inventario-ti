from datetime import datetime
from app import mongo
from bson import ObjectId

def registrar_historico(asset_id, dados_antigos, dados_novos, usuario="Sistema"):
    """
    Compara o documento antigo com o novo e gera logs detalhados para o que mudou.
    Registra: criação, alterações de campos, adições e remoções de itens.
    """
    
    # Garantir que asset_id é ObjectId
    if isinstance(asset_id, str):
        asset_id = ObjectId(asset_id)
    
    # É uma criação nova
    if not dados_antigos:
        log_entrada = {
            "asset_id": asset_id,
            "data": datetime.now(),
            "acao": "CRIACAO",
            "usuario": usuario,
            "campos_alterados": list(dados_novos.keys()),
            "detalhes": f"Ativo {dados_novos.get('patrimonio', 'N/A')} cadastrado no sistema",
            "timestamp": datetime.now()
        }
        mongo.db.logs.insert_one(log_entrada)
        return

    ignorar = ['_id', 'updated_at', 'created_at']
    
    # Detectar campos alterados
    campos_alterados = []
    
    for chave, valor_novo in dados_novos.items():
        if chave in ignorar:
            continue
            
        valor_antigo = dados_antigos.get(chave)
        
        if valor_antigo != valor_novo:
            # Se for lista (softwares), detectar o que foi adicionado/removido
            if isinstance(valor_novo, list) and isinstance(valor_antigo, list):
                adicionados = [item for item in valor_novo if item not in valor_antigo]
                removidos = [item for item in valor_antigo if item not in valor_novo]
                
                if adicionados:
                    mongo.db.logs.insert_one({
                        "asset_id": asset_id,
                        "data": datetime.now(),
                        "acao": "ADICAO",
                        "campo": chave,
                        "itens_adicionados": adicionados,
                        "usuario": usuario,
                        "timestamp": datetime.now()
                    })
                    campos_alterados.append(f"{chave} (+)")
                
                if removidos:
                    mongo.db.logs.insert_one({
                        "asset_id": asset_id,
                        "data": datetime.now(),
                        "acao": "REMOCAO",
                        "campo": chave,
                        "itens_removidos": removidos,
                        "usuario": usuario,
                        "timestamp": datetime.now()
                    })
                    campos_alterados.append(f"{chave} (-)")
            else:
                # Alteração simples de campo
                mongo.db.logs.insert_one({
                    "asset_id": asset_id,
                    "data": datetime.now(),
                    "acao": "ALTERACAO",
                    "campo": chave,
                    "valor_anterior": str(valor_antigo) if valor_antigo else "vazio",
                    "valor_novo": str(valor_novo) if valor_novo else "vazio",
                    "usuario": usuario,
                    "timestamp": datetime.now()
                })
                campos_alterados.append(chave)
    
    # Registrar log geral de alteração
    if campos_alterados:
        mongo.db.logs.insert_one({
            "asset_id": asset_id,
            "data": datetime.now(),
            "acao": "ATUALIZACAO",
            "usuario": usuario,
            "campos_alterados": campos_alterados,
            "detalhes": f"Ativo {dados_novos.get('patrimonio', 'N/A')} atualizado",
            "timestamp": datetime.now()
        })

def obter_logs_ativo(asset_id):
    """Retorna todos os logs de um ativo"""
    if isinstance(asset_id, str):
        asset_id = ObjectId(asset_id)
    
    logs = list(mongo.db.logs.find(
        {'asset_id': asset_id}
    ).sort('data', -1))
    
    for log in logs:
        log['_id'] = str(log['_id'])
        log['asset_id'] = str(log['asset_id'])
        log['data'] = log['data'].isoformat()
        if 'timestamp' in log:
            log['timestamp'] = log['timestamp'].isoformat()
    
    return logs

def obter_todos_os_logs(filtro_usuario=None, limite=100):
    """Retorna todos os logs do sistema com opção de filtro"""
    query = {}
    if filtro_usuario:
        query['usuario'] = filtro_usuario
    
    logs = list(mongo.db.logs.find(query).sort('data', -1).limit(limite))
    
    for log in logs:
        log['_id'] = str(log['_id'])
        log['asset_id'] = str(log['asset_id'])
        log['data'] = log['data'].isoformat()
        if 'timestamp' in log:
            log['timestamp'] = log['timestamp'].isoformat()
    
    return logs