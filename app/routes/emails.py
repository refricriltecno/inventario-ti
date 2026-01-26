from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app import mongo
from app.services.audit import registrar_historico
from bson.objectid import ObjectId
from datetime import datetime

bp_emails = Blueprint('emails', __name__)

# --- ROTAS DE EMAILS (ZIMBRA/GOOGLE) ---

@bp_emails.route('/api/emails', methods=['GET'])
@jwt_required()
def get_emails():
    """Listar todos os emails, opcionalmente filtrar por asset_id ou filial"""
    asset_id = request.args.get('asset_id')
    filial = request.args.get('filial')
    tipo = request.args.get('tipo')  # 'google' ou 'zimbra'
    
    query = {}
    if asset_id:
        try:
            query['asset_id'] = ObjectId(asset_id)
        except:
            pass
    if filial:
        query['filial'] = filial
    if tipo:
        query['tipo'] = tipo
    
    emails = list(mongo.db.emails.find(query))
    for email in emails:
        email['_id'] = str(email['_id'])
        if 'asset_id' in email:
            email['asset_id'] = str(email['asset_id'])
    
    return jsonify(emails), 200

@bp_emails.route('/api/emails/<id>', methods=['GET'])
@jwt_required()
def get_email(id):
    """Obter detalhes de um email específico"""
    try:
        email = mongo.db.emails.find_one({'_id': ObjectId(id)})
        if not email:
            return jsonify({'erro': 'Email não encontrado'}), 404
        email['_id'] = str(email['_id'])
        if 'asset_id' in email:
            email['asset_id'] = str(email['asset_id'])
        return jsonify(email), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 400

@bp_emails.route('/api/emails', methods=['POST'])
@jwt_required()
def create_email():
    """Criar novo email (Zimbra ou Google)"""
    claims = get_jwt()
    user_name = claims.get('nome', 'Unknown')
    data = request.json
    
    # Validações obrigatórias
    if not data.get('endereco') or not data.get('asset_id') or not data.get('tipo'):
        return jsonify({'erro': 'Endereço, Asset ID e Tipo são obrigatórios'}), 400
    
    if data.get('tipo') not in ['google', 'zimbra']:
        return jsonify({'erro': 'Tipo deve ser "google" ou "zimbra"'}), 400
    
    # Determinar tipo de asset se não informado
    if 'asset_type' not in data:
        data['asset_type'] = 'workstation'
    
    # Converter asset_id para ObjectId se for string
    if isinstance(data.get('asset_id'), str):
        try:
            data['asset_id'] = ObjectId(data['asset_id'])
        except:
            return jsonify({'erro': 'Asset ID inválido'}), 400
    
    data['created_at'] = datetime.now()
    data['updated_at'] = datetime.now()
    data['status'] = data.get('status', 'Ativo')
    
    result = mongo.db.emails.insert_one(data)
    registrar_historico(result.inserted_id, None, data, usuario=user_name)
    
    return jsonify({
        'msg': 'Email criado com sucesso!',
        'id': str(result.inserted_id)
    }), 201

@bp_emails.route('/api/emails/<id>', methods=['PUT'])
@jwt_required()
def update_email(id):
    """Atualizar email existente"""
    claims = get_jwt()
    user_name = claims.get('nome', 'Unknown')
    data = request.json
    
    try:
        obj_id = ObjectId(id)
    except:
        return jsonify({'erro': 'ID inválido'}), 400
    
    email_antigo = mongo.db.emails.find_one({'_id': obj_id})
    if not email_antigo:
        return jsonify({'erro': 'Email não encontrado'}), 404
    
    # Converter asset_id para ObjectId se for string
    if 'asset_id' in data and isinstance(data.get('asset_id'), str):
        try:
            data['asset_id'] = ObjectId(data['asset_id'])
        except:
            return jsonify({'erro': 'Asset ID inválido'}), 400
    
    data['updated_at'] = datetime.now()
    if '_id' in data:
        del data['_id']
    
    mongo.db.emails.update_one({'_id': obj_id}, {'$set': data})
    registrar_historico(obj_id, email_antigo, data, usuario=user_name)
    
    return jsonify({'msg': 'Email atualizado com sucesso!'}), 200

@bp_emails.route('/api/emails/<id>', methods=['DELETE'])
@jwt_required()
def delete_email(id):
    """Inativar email (soft delete)"""
    claims = get_jwt()
    user_name = claims.get('nome', 'Unknown')
    
    try:
        obj_id = ObjectId(id)
    except:
        return jsonify({'erro': 'ID inválido'}), 400
    
    email = mongo.db.emails.find_one({'_id': obj_id})
    if not email:
        return jsonify({'erro': 'Email não encontrado'}), 404
    
    mongo.db.emails.update_one(
        {'_id': obj_id},
        {'$set': {
            'status': 'Inativo',
            'deleted_at': datetime.now()
        }}
    )
    registrar_historico(obj_id, email, {'status': 'Inativo'}, usuario=user_name)
    
    return jsonify({'msg': 'Email inativado com sucesso!'}), 200
