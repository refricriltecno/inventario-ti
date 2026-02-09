from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app.models import db, Celular
from app.services.audit import registrar_historico, registrar_exclusao
from datetime import datetime, date

bp_celulares = Blueprint('celulares', __name__)


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


def _status_value(payload):
    status = payload.get('status')
    return status if status else 'Ativo'

# --- ROTAS DE CELULARES ---

@bp_celulares.route('/api/celulares', methods=['GET'])
@jwt_required()
def get_celulares():
    """Listar todos os celulares, opcionalmente filtrar por filial"""
    filial = request.args.get('filial')
    query = Celular.query
    if filial:
        query = query.filter_by(filial=filial)
    celulares = query.all()
    return jsonify([celular.to_dict() for celular in celulares]), 200

@bp_celulares.route('/api/celulares/<id>', methods=['GET'])
@jwt_required()
def get_celular(id):
    """Obter detalhes de um celular específico"""
    try:
        celular_id = int(id)
    except ValueError:
        return jsonify({'erro': 'ID inválido'}), 400

    celular = Celular.query.get(celular_id)
    if not celular:
        return jsonify({'erro': 'Celular não encontrado'}), 404
    return jsonify(celular.to_dict()), 200

@bp_celulares.route('/api/celulares', methods=['POST'])
@jwt_required()
def create_celular():
    """Criar novo celular"""
    claims = get_jwt()
    user_name = claims.get('nome', 'Unknown')
    data = request.json or {}
    
    # Validações obrigatórias
    if not data.get('patrimonio') or not data.get('filial'):
        return jsonify({'erro': 'Patrimônio e Filial são obrigatórios'}), 400
    
    # Verificar unicidade de patrimônio
    if Celular.query.filter_by(patrimonio=data['patrimonio']).first():
        return jsonify({'erro': 'Patrimônio já cadastrado'}), 409
    
    celular = Celular(
        patrimonio=data.get('patrimonio'),
        filial=data.get('filial'),
        modelo=data.get('modelo'),
        imei=data.get('imei'),
        numero=data.get('numero'),
        operadora=data.get('operadora'),
        responsavel=data.get('responsavel'),
        status=_status_value(data),
        observacoes=data.get('observacoes'),
        dt_compra=_parse_date(data.get('dt_compra')),
        valor=data.get('valor')
    )

    celular.atualizado_em = datetime.now()
    db.session.add(celular)
    db.session.commit()

    registrar_historico(celular.id, None, celular.to_dict(), usuario=user_name, entidade="Celular")

    return jsonify({
        'msg': 'Celular criado com sucesso!',
        'id': str(celular.id)
    }), 201

@bp_celulares.route('/api/celulares/<id>', methods=['PUT'])
@jwt_required()
def update_celular(id):
    """Atualizar celular existente"""
    claims = get_jwt()
    user_name = claims.get('nome', 'Unknown')
    data = request.json or {}

    try:
        celular_id = int(id)
    except ValueError:
        return jsonify({'erro': 'ID inválido'}), 400

    celular = Celular.query.get(celular_id)
    if not celular:
        return jsonify({'erro': 'Celular não encontrado'}), 404

    celular_antigo = celular.to_dict()

    for chave in ['patrimonio', 'filial', 'modelo', 'imei', 'numero', 'operadora', 'responsavel', 'observacoes']:
        if chave in data:
            setattr(celular, chave, data.get(chave))

    if 'status' in data:
        celular.status = _status_value(data)

    if 'dt_compra' in data:
        celular.dt_compra = _parse_date(data.get('dt_compra'))

    if 'valor' in data:
        celular.valor = data.get('valor')

    celular.atualizado_em = datetime.now()
    db.session.commit()

    registrar_historico(celular.id, celular_antigo, celular.to_dict(), usuario=user_name, entidade="Celular")

    return jsonify({'msg': 'Celular atualizado com sucesso!'}), 200

@bp_celulares.route('/api/celulares/<id>', methods=['DELETE'])
@jwt_required()
def delete_celular(id):
    """Inativar ou excluir celular (hard delete apenas admin)"""
    claims = get_jwt()
    user_name = claims.get('nome', 'Unknown')
    permissoes = claims.get('permissoes', [])
    hard = request.args.get('hard', 'false').lower() == 'true'
    
    try:
        celular_id = int(id)
    except ValueError:
        return jsonify({'erro': 'ID inválido'}), 400

    celular = Celular.query.get(celular_id)
    if not celular:
        return jsonify({'erro': 'Celular não encontrado'}), 404

    celular_antigo = celular.to_dict()

    if hard:
        if 'admin' not in permissoes:
            return jsonify({'erro': 'Apenas admins podem excluir definitivamente'}), 403
        db.session.delete(celular)
        db.session.commit()
        registrar_exclusao(celular_id, celular_antigo, usuario=user_name, entidade="Celular")
        return jsonify({'msg': 'Celular excluido definitivamente!'}), 200

    celular.status = 'Inativo'
    celular.atualizado_em = datetime.now()
    db.session.commit()
    registrar_historico(celular_id, celular_antigo, celular.to_dict(), usuario=user_name, entidade="Celular")

    return jsonify({'msg': 'Celular inativado com sucesso!'}), 200
