from datetime import datetime
from app.models import db, AuditLog


def registrar_exclusao(asset_id, dados_antigos, usuario="Sistema", entidade="Asset"):
    """Registra remoção definitiva preservando snapshot para auditoria."""
    try:
        entidade_id = str(int(asset_id))
    except (TypeError, ValueError):
        entidade_id = None

    log = AuditLog(
        usuario_nome=usuario,
        acao="EXCLUSAO",
        entidade=entidade,
        entidade_id=entidade_id,
        descricao=f"Ativo {dados_antigos.get('patrimonio', 'N/A')} excluido definitivamente" if dados_antigos else "Registro excluido definitivamente",
        dados_antes=dados_antigos,
        dados_depois=None,
        timestamp=datetime.now()
    )
    db.session.add(log)
    db.session.commit()

def registrar_historico(asset_id, dados_antigos, dados_novos, usuario="Sistema", entidade="Asset"):
    """
    Compara o documento antigo com o novo e gera logs detalhados para o que mudou.
    Registra: criação, alterações de campos, adições e remoções de itens.
    """

    try:
        entidade_id = str(int(asset_id))
    except (TypeError, ValueError):
        entidade_id = None

    logs = []

    # É uma criação nova
    if not dados_antigos:
        logs.append(AuditLog(
            usuario_nome=usuario,
            acao="CRIACAO",
            entidade=entidade,
            entidade_id=entidade_id,
            descricao=f"Ativo {dados_novos.get('patrimonio', 'N/A')} cadastrado no sistema",
            dados_antes=None,
            dados_depois=dados_novos,
            timestamp=datetime.now()
        ))
        db.session.add_all(logs)
        db.session.commit()
        return

    ignorar = ['_id', 'updated_at', 'created_at', 'criado_em', 'atualizado_em']

    # Detectar campos alterados
    campos_alterados = []

    for chave, valor_novo in dados_novos.items():
        if chave in ignorar:
            continue

        valor_antigo = dados_antigos.get(chave)

        if valor_antigo != valor_novo:
            # Se for lista, detectar o que foi adicionado/removido
            if isinstance(valor_novo, list) and isinstance(valor_antigo, list):
                adicionados = [item for item in valor_novo if item not in valor_antigo]
                removidos = [item for item in valor_antigo if item not in valor_novo]

                if adicionados:
                    logs.append(AuditLog(
                        usuario_nome=usuario,
                        acao="ADICAO",
                        entidade=entidade,
                        entidade_id=entidade_id,
                        descricao=f"Itens adicionados em {chave}",
                        dados_antes=None,
                        dados_depois={"campo": chave, "itens_adicionados": adicionados},
                        timestamp=datetime.now()
                    ))
                    campos_alterados.append(f"{chave} (+)")

                if removidos:
                    logs.append(AuditLog(
                        usuario_nome=usuario,
                        acao="REMOCAO",
                        entidade=entidade,
                        entidade_id=entidade_id,
                        descricao=f"Itens removidos em {chave}",
                        dados_antes={"campo": chave, "itens_removidos": removidos},
                        dados_depois=None,
                        timestamp=datetime.now()
                    ))
                    campos_alterados.append(f"{chave} (-)")
            else:
                logs.append(AuditLog(
                    usuario_nome=usuario,
                    acao="ALTERACAO",
                    entidade=entidade,
                    entidade_id=entidade_id,
                    descricao=f"Campo {chave} alterado",
                    dados_antes={chave: valor_antigo},
                    dados_depois={chave: valor_novo},
                    timestamp=datetime.now()
                ))
                campos_alterados.append(chave)

    # Registrar log geral de alteração
    if campos_alterados:
        logs.append(AuditLog(
            usuario_nome=usuario,
            acao="ATUALIZACAO",
            entidade=entidade,
            entidade_id=entidade_id,
            descricao=f"Ativo {dados_novos.get('patrimonio', 'N/A')} atualizado",
            dados_antes={"campos_alterados": campos_alterados},
            dados_depois=dados_novos,
            timestamp=datetime.now()
        ))

    if logs:
        db.session.add_all(logs)
        db.session.commit()

def obter_logs_ativo(asset_id):
    """Retorna todos os logs de um ativo"""
    try:
        entidade_id = str(int(asset_id))
    except (TypeError, ValueError):
        entidade_id = None

    logs = AuditLog.query.filter_by(entidade_id=entidade_id).order_by(AuditLog.timestamp.desc()).all()
    return [log.to_dict() for log in logs]

def obter_todos_os_logs(filtro_usuario=None, limite=100):
    """Retorna todos os logs do sistema com opção de filtro"""
    query = AuditLog.query
    if filtro_usuario:
        query = query.filter_by(usuario_nome=filtro_usuario)

    logs = query.order_by(AuditLog.timestamp.desc()).limit(limite).all()
    return [log.to_dict() for log in logs]