from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app.models import db, Asset, Filial, Celular, Usuario
from app.services.audit import registrar_historico, registrar_exclusao
from datetime import datetime, date

bp_assets = Blueprint('assets', __name__)


def _parse_date(value):
    if not value:
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value).date()
        except ValueError:
            return None
    return None


def _asset_fields_from_payload(payload, existing_especificacoes=None):
    allowed_fields = {
        'patrimonio', 'tipo', 'marca', 'modelo', 'numero_serie', 'filial', 'setor',
        'responsavel', 'status', 'observacoes', 'dt_compra', 'dt_garantia', 'valor',
        'fornecedor', 'nota_fiscal', 'especificacoes'
    }
    skip_fields = {'_id', 'id', 'created_at', 'updated_at', 'criado_em', 'atualizado_em'}

    campos = {}
    extras = {}

    for chave, valor in payload.items():
        if chave in skip_fields:
            continue
        if chave in allowed_fields:
            campos[chave] = valor
        else:
            extras[chave] = valor

    if 'dt_compra' in campos:
        campos['dt_compra'] = _parse_date(campos['dt_compra'])
    if 'dt_garantia' in campos:
        campos['dt_garantia'] = _parse_date(campos['dt_garantia'])

    especificacoes = {}
    if isinstance(existing_especificacoes, dict):
        especificacoes.update(existing_especificacoes)
    if isinstance(campos.get('especificacoes'), dict):
        especificacoes.update(campos['especificacoes'])
    if extras:
        especificacoes.update(extras)

    if especificacoes:
        campos['especificacoes'] = especificacoes

    return campos

# --- ROTAS DE ATIVOS ---

@bp_assets.route('/api/assets', methods=['GET'])
@jwt_required()
def get_assets():
    filial = request.args.get('filial')
    query = Asset.query
    if filial:
        query = query.filter_by(filial=filial)
    assets = query.all()
    return jsonify([asset.to_dict() for asset in assets])

@bp_assets.route('/api/assets/<id>', methods=['GET'])
@jwt_required()
def get_one_asset(id):
    try:
        asset_id = int(id)
    except ValueError:
        return jsonify({'erro': 'ID inválido'}), 400

    asset = Asset.query.get(asset_id)
    if not asset:
        return jsonify({'erro': 'Ativo não encontrado'}), 404
    return jsonify(asset.to_dict())

@bp_assets.route('/api/assets', methods=['POST'])
@jwt_required()
def create_asset():
    claims = get_jwt()
    user_name = claims.get('nome', 'Unknown')
    data = request.json or {}
    campos = _asset_fields_from_payload(data)
    asset = Asset(**campos)
    asset.atualizado_em = datetime.now()

    db.session.add(asset)
    db.session.commit()

    registrar_historico(asset.id, None, asset.to_dict(), usuario=user_name, entidade="Asset")
    return jsonify({"msg": "Criado com sucesso!", "id": str(asset.id)}), 201

@bp_assets.route('/api/assets/<id>', methods=['PUT'])
@jwt_required()
def update_asset(id):
    claims = get_jwt()
    user_name = claims.get('nome', 'Unknown')
    data = request.json or {}

    try:
        asset_id = int(id)
    except ValueError:
        return jsonify({'erro': 'ID inválido'}), 400

    asset = Asset.query.get(asset_id)
    if not asset:
        return jsonify({"erro": "Ativo não encontrado"}), 404

    antigo = asset.to_dict()
    campos = _asset_fields_from_payload(data, existing_especificacoes=asset.especificacoes)

    for chave, valor in campos.items():
        setattr(asset, chave, valor)
    asset.atualizado_em = datetime.now()

    db.session.commit()
    registrar_historico(asset.id, antigo, asset.to_dict(), usuario=user_name, entidade="Asset")
    return jsonify({"msg": "Atualizado com sucesso!"}), 200

@bp_assets.route('/api/assets/<id>', methods=['DELETE'])
@jwt_required()
def delete_asset(id):
    claims = get_jwt()
    user_name = claims.get('nome', 'Unknown')
    hard = request.args.get('hard', 'false').lower() == 'true'
    try:
        asset_id = int(id)
    except ValueError:
        return jsonify({'erro': 'ID inválido'}), 400

    asset = Asset.query.get(asset_id)
    if not asset:
        return jsonify({"erro": "Ativo não encontrado"}), 404

    antigo = asset.to_dict()

    if hard:
        db.session.delete(asset)
        db.session.commit()
        registrar_exclusao(asset_id, antigo, usuario=user_name, entidade="Asset")
        return jsonify({"msg": "Ativo excluido definitivamente!"}), 200

    asset.status = 'Inativo'
    asset.atualizado_em = datetime.now()
    db.session.commit()
    registrar_historico(asset_id, antigo, asset.to_dict(), usuario=user_name, entidade="Asset")
    return jsonify({"msg": "Ativo inativado com sucesso!"}), 200

# --- ROTAS DE FILIAIS (Gerenciamento Completo) ---

@bp_assets.route('/api/filiais', methods=['GET'])
def get_filiais():
    filiais = Filial.query.order_by(Filial.nome.asc()).all()
    return jsonify([f.to_dict() for f in filiais])

# --- NOVA ROTA: BUSCAR FUNCIONÁRIOS POR FILIAL ---

@bp_assets.route('/api/funcionarios/<filial>', methods=['GET'])
def get_funcionarios_by_filial(filial):
    """Retorna lista de funcionários de uma filial específica"""
    funcionarios = Usuario.query.filter_by(filial=filial).order_by(Usuario.nome.asc()).all()
    result = [f.nome for f in funcionarios]
    return jsonify(result)

@bp_assets.route('/api/filiais', methods=['POST'])
@jwt_required()
def create_filial():
    data = request.json or {}
    nome = data.get('nome')
    tipo = data.get('tipo') 
    
    if not nome or not tipo:
        return jsonify({"erro": "Nome e Tipo são obrigatórios"}), 400
        
    if Filial.query.filter(Filial.nome.ilike(nome)).first():
        return jsonify({"erro": "Filial já existe"}), 409

    filial = Filial(nome=nome)
    db.session.add(filial)
    db.session.commit()
    return jsonify({"msg": "Filial criada!"}), 201

# NOVA ROTA: DELETAR FILIAL
@bp_assets.route('/api/filiais/<id>', methods=['DELETE'])
@jwt_required()
def delete_filial(id):
    try:
        filial_id = int(id)
    except ValueError:
        return jsonify({'erro': 'ID inválido'}), 400

    filial = Filial.query.get(filial_id)
    if not filial:
        return jsonify({'erro': 'Filial não encontrada'}), 404

    db.session.delete(filial)
    db.session.commit()
    return jsonify({"msg": "Filial removida com sucesso!"}), 200

# --- NOVA ROTA: Listar Responsáveis por Filial ---
@bp_assets.route('/api/funcionarios/<path:filial>', methods=['GET'])
# @jwt_required() # Pode descomentar se quiser proteger
def get_funcionarios_por_filial(filial):
    try:
        # Decodifica a URL (ex: "01%20-%20Matriz" vira "01 - Matriz")
        from urllib.parse import unquote
        filial_decode = unquote(filial)
        
        # Busca no banco todos os responsáveis distintos dessa filial
        # 1. Busca em Workstations
        resps_assets = db.session.query(Asset.responsavel).filter(
            Asset.filial == filial_decode,
            Asset.responsavel.isnot(None),
            Asset.responsavel != ""
        ).distinct().all()
        
        # 2. Busca em Celulares (opcional, mas bom para garantir)
        resps_cel = db.session.query(Celular.responsavel).filter(
            Celular.filial == filial_decode,
            Celular.responsavel.isnot(None),
            Celular.responsavel != ""
        ).distinct().all()
        
        # Junta tudo, remove vazios e ordena
        todos = set([r[0] for r in resps_assets] + [r[0] for r in resps_cel])
        todos.discard("")
        todos.discard(None)
        
        return jsonify(sorted(list(todos))), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500