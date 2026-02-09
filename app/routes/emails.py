from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app.models import db, Email, Asset
from app.services.audit import registrar_historico
from datetime import datetime

bp_emails = Blueprint('emails', __name__)


def _status_to_ativo(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() != 'inativo'
    return True

# --- ROTAS DE EMAILS (ZIMBRA/GOOGLE) ---

@bp_emails.route('/api/emails', methods=['GET'])
@jwt_required()
def get_emails():
    """Listar todos os emails, opcionalmente filtrar por asset_id ou filial"""
    asset_id = request.args.get('asset_id')
    filial = request.args.get('filial')
    tipo = request.args.get('tipo')  # 'google' ou 'zimbra'

    query = Email.query
    if asset_id:
        try:
            query = query.filter(Email.asset_id == int(asset_id))
        except ValueError:
            pass
    if filial:
        query = query.join(Asset).filter(Asset.filial == filial)
    if tipo:
        query = query.filter(Email.tipo == tipo)

    emails = query.all()
    return jsonify([email.to_dict() for email in emails]), 200

@bp_emails.route('/api/emails/<id>', methods=['GET'])
@jwt_required()
def get_email(id):
    """Obter detalhes de um email específico"""
    try:
        email_id = int(id)
    except ValueError:
        return jsonify({'erro': 'ID inválido'}), 400

    email = Email.query.get(email_id)
    if not email:
        return jsonify({'erro': 'Email não encontrado'}), 404
    return jsonify(email.to_dict()), 200

@bp_emails.route('/api/emails', methods=['POST'])
@jwt_required()
def create_email():
    """Criar novo email (Zimbra ou Google)"""
    claims = get_jwt()
    user_name = claims.get('nome', 'Unknown')
    data = request.json or {}
    
    # Validações obrigatórias
    if not data.get('endereco') or not data.get('asset_id') or not data.get('tipo'):
        return jsonify({'erro': 'Endereço, Asset ID e Tipo são obrigatórios'}), 400
    
    if data.get('tipo') not in ['google', 'zimbra', 'microsoft']:
        return jsonify({'erro': 'Tipo deve ser "google", "zimbra" ou "microsoft"'}), 400
    
    try:
        asset_id = int(data.get('asset_id'))
    except ValueError:
        return jsonify({'erro': 'Asset ID inválido'}), 400

    ativo = _status_to_ativo(data.get('ativo') if 'ativo' in data else data.get('status'))

    email = Email(
        endereco=data.get('endereco'),
        tipo=data.get('tipo'),
        asset_id=asset_id,
        usuario=data.get('usuario'),
        senha=data.get('senha'),
        recuperacao=data.get('recuperacao'),
        observacoes=data.get('observacoes'),
        ativo=ativo
    )

    email.atualizado_em = datetime.now()
    db.session.add(email)
    db.session.commit()

    registrar_historico(email.id, None, email.to_dict(include_password=True), usuario=user_name, entidade="Email")

    return jsonify({
        'msg': 'Email criado com sucesso!',
        'id': str(email.id)
    }), 201

@bp_emails.route('/api/emails/<id>', methods=['PUT'])
@jwt_required()
def update_email(id):
    """Atualizar email existente"""
    claims = get_jwt()
    user_name = claims.get('nome', 'Unknown')
    data = request.json or {}

    try:
        email_id = int(id)
    except ValueError:
        return jsonify({'erro': 'ID inválido'}), 400

    email = Email.query.get(email_id)
    if not email:
        return jsonify({'erro': 'Email não encontrado'}), 404

    email_antigo = email.to_dict(include_password=True)

    for chave in ['endereco', 'tipo', 'usuario', 'senha', 'recuperacao', 'observacoes']:
        if chave in data:
            setattr(email, chave, data.get(chave))

    if 'asset_id' in data:
        try:
            email.asset_id = int(data.get('asset_id'))
        except ValueError:
            return jsonify({'erro': 'Asset ID inválido'}), 400

    if 'ativo' in data or 'status' in data:
        email.ativo = _status_to_ativo(data.get('ativo') if 'ativo' in data else data.get('status'))

    email.atualizado_em = datetime.now()
    db.session.commit()

    registrar_historico(email.id, email_antigo, email.to_dict(include_password=True), usuario=user_name, entidade="Email")

    return jsonify({'msg': 'Email atualizado com sucesso!'}), 200

@bp_emails.route('/api/emails/<id>', methods=['DELETE'])
@jwt_required()
def delete_email(id):
    """Inativar email (soft delete)"""
    claims = get_jwt()
    user_name = claims.get('nome', 'Unknown')

    try:
        email_id = int(id)
    except ValueError:
        return jsonify({'erro': 'ID inválido'}), 400

    email = Email.query.get(email_id)
    if not email:
        return jsonify({'erro': 'Email não encontrado'}), 404

    email_antigo = email.to_dict(include_password=True)
    email.ativo = False
    email.atualizado_em = datetime.now()
    db.session.commit()

    registrar_historico(email.id, email_antigo, email.to_dict(include_password=True), usuario=user_name, entidade="Email")

    return jsonify({'msg': 'Email inativado com sucesso!'}), 200
