from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app.models import db, Software, Asset
from app.services.audit import registrar_historico
from datetime import datetime, date

bp_softwares = Blueprint('softwares', __name__)


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


def _status_to_ativo(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() != 'inativo'
    return True

# --- ROTAS DE SOFTWARES/LICENÇAS ---

@bp_softwares.route('/api/softwares', methods=['GET'])
@jwt_required()
def get_softwares():
    """Listar todos os softwares, opcionalmente filtrar por asset_id ou filial"""
    asset_id = request.args.get('asset_id')
    filial = request.args.get('filial')

    query = Software.query
    if asset_id:
        try:
            query = query.filter(Software.asset_id == int(asset_id))
        except ValueError:
            pass
    if filial:
        query = query.join(Asset).filter(Asset.filial == filial)

    softwares = query.all()
    return jsonify([software.to_dict() for software in softwares]), 200

@bp_softwares.route('/api/softwares/<id>', methods=['GET'])
@jwt_required()
def get_software(id):
    """Obter detalhes de um software específico"""
    try:
        software_id = int(id)
    except ValueError:
        return jsonify({'erro': 'ID inválido'}), 400

    software = Software.query.get(software_id)
    if not software:
        return jsonify({'erro': 'Software não encontrado'}), 404
    return jsonify(software.to_dict()), 200

@bp_softwares.route('/api/softwares', methods=['POST'])
@jwt_required()
def create_software():
    """Criar novo software/licença"""
    claims = get_jwt()
    user_name = claims.get('nome', 'Unknown')
    data = request.json or {}
    
    # Validações obrigatórias
    if not data.get('nome') or not data.get('asset_id'):
        return jsonify({'erro': 'Nome e Asset ID são obrigatórios'}), 400

    try:
        asset_id = int(data.get('asset_id'))
    except ValueError:
        return jsonify({'erro': 'Asset ID inválido'}), 400

    ativo = _status_to_ativo(data.get('ativo') if 'ativo' in data else data.get('status'))

    software = Software(
        nome=data.get('nome'),
        versao=data.get('versao'),
        asset_id=asset_id,
        tipo_licenca=data.get('tipo_licenca'),
        chave_licenca=data.get('chave_licenca'),
        dt_instalacao=_parse_date(data.get('dt_instalacao')),
        dt_vencimento=_parse_date(data.get('dt_vencimento')),
        custo_anual=data.get('custo_anual'),
        renovacao_automatica=data.get('renovacao_automatica', False),
        observacoes=data.get('observacoes'),
        ativo=ativo
    )

    software.atualizado_em = datetime.now()
    db.session.add(software)
    db.session.commit()

    registrar_historico(software.id, None, software.to_dict(), usuario=user_name, entidade="Software")

    return jsonify({
        'msg': 'Software/Licença criado com sucesso!',
        'id': str(software.id)
    }), 201

@bp_softwares.route('/api/softwares/<id>', methods=['PUT'])
@jwt_required()
def update_software(id):
    """Atualizar software/licença existente"""
    claims = get_jwt()
    user_name = claims.get('nome', 'Unknown')
    data = request.json or {}

    try:
        software_id = int(id)
    except ValueError:
        return jsonify({'erro': 'ID inválido'}), 400

    software = Software.query.get(software_id)
    if not software:
        return jsonify({'erro': 'Software não encontrado'}), 404

    software_antigo = software.to_dict()

    for chave in ['nome', 'versao', 'tipo_licenca', 'chave_licenca', 'observacoes']:
        if chave in data:
            setattr(software, chave, data.get(chave))

    if 'asset_id' in data:
        try:
            software.asset_id = int(data.get('asset_id'))
        except ValueError:
            return jsonify({'erro': 'Asset ID inválido'}), 400

    if 'dt_instalacao' in data:
        software.dt_instalacao = _parse_date(data.get('dt_instalacao'))
    if 'dt_vencimento' in data:
        software.dt_vencimento = _parse_date(data.get('dt_vencimento'))
    if 'custo_anual' in data:
        software.custo_anual = data.get('custo_anual')
    if 'renovacao_automatica' in data:
        software.renovacao_automatica = data.get('renovacao_automatica')
    if 'ativo' in data or 'status' in data:
        software.ativo = _status_to_ativo(data.get('ativo') if 'ativo' in data else data.get('status'))

    software.atualizado_em = datetime.now()
    db.session.commit()

    registrar_historico(software.id, software_antigo, software.to_dict(), usuario=user_name, entidade="Software")

    return jsonify({'msg': 'Software/Licença atualizado com sucesso!'}), 200

@bp_softwares.route('/api/softwares/<id>', methods=['DELETE'])
@jwt_required()
def delete_software(id):
    """Inativar software/licença (soft delete)"""
    claims = get_jwt()
    user_name = claims.get('nome', 'Unknown')

    try:
        software_id = int(id)
    except ValueError:
        return jsonify({'erro': 'ID inválido'}), 400

    software = Software.query.get(software_id)
    if not software:
        return jsonify({'erro': 'Software não encontrado'}), 404

    software_antigo = software.to_dict()
    software.ativo = False
    software.atualizado_em = datetime.now()
    db.session.commit()

    registrar_historico(software.id, software_antigo, software.to_dict(), usuario=user_name, entidade="Software")

    return jsonify({'msg': 'Software/Licença inativado com sucesso!'}), 200

# --- ROTAS AUXILIARES ---

@bp_softwares.route('/api/softwares/verificar-vencimento', methods=['GET'])
@jwt_required()
def verificar_vencimento():
    """Listar softwares prestes a vencer (próximos 30 dias)"""
    dias = int(request.args.get('dias', 30))
    
    from datetime import timedelta
    data_limite = datetime.now().date() + timedelta(days=dias)
    hoje = datetime.now().date()

    softwares = Software.query.filter(
        Software.dt_vencimento >= hoje,
        Software.dt_vencimento <= data_limite,
        Software.ativo.is_(True)
    ).all()

    return jsonify([software.to_dict() for software in softwares]), 200
