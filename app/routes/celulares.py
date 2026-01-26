from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app import mongo
from app.services.audit import registrar_historico
from bson.objectid import ObjectId
from datetime import datetime

bp_celulares = Blueprint('celulares', __name__)

# --- ROTAS DE CELULARES ---

@bp_celulares.route('/api/celulares', methods=['GET'])
@jwt_required()
def get_celulares():
    """Listar todos os celulares, opcionalmente filtrar por filial"""
    filial = request.args.get('filial')
    query = {'filial': filial} if filial else {}
    celulares = list(mongo.db.celulares.find(query))
    for celular in celulares:
        celular['_id'] = str(celular['_id'])
    return jsonify(celulares), 200

@bp_celulares.route('/api/celulares/<id>', methods=['GET'])
@jwt_required()
def get_celular(id):
    """Obter detalhes de um celular específico"""
    try:
        celular = mongo.db.celulares.find_one({'_id': ObjectId(id)})
        if not celular:
            return jsonify({'erro': 'Celular não encontrado'}), 404
        celular['_id'] = str(celular['_id'])
        return jsonify(celular), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 400

@bp_celulares.route('/api/celulares', methods=['POST'])
@jwt_required()
def create_celular():
    """Criar novo celular"""
    claims = get_jwt()
    user_name = claims.get('nome', 'Unknown')
    data = request.json
    
    # Validações obrigatórias
    if not data.get('patrimonio') or not data.get('filial'):
        return jsonify({'erro': 'Patrimônio e Filial são obrigatórios'}), 400
    
    # Verificar unicidade de patrimônio
    if mongo.db.celulares.find_one({'patrimonio': data['patrimonio']}):
        return jsonify({'erro': 'Patrimônio já cadastrado'}), 409
    
    data['created_at'] = datetime.now()
    data['updated_at'] = datetime.now()
    
    result = mongo.db.celulares.insert_one(data)
    registrar_historico(result.inserted_id, None, data, usuario=user_name)
    
    return jsonify({
        'msg': 'Celular criado com sucesso!',
        'id': str(result.inserted_id)
    }), 201

@bp_celulares.route('/api/celulares/<id>', methods=['PUT'])
@jwt_required()
def update_celular(id):
    """Atualizar celular existente"""
    claims = get_jwt()
    user_name = claims.get('nome', 'Unknown')
    data = request.json
    
    try:
        obj_id = ObjectId(id)
    except:
        return jsonify({'erro': 'ID inválido'}), 400
    
    celular_antigo = mongo.db.celulares.find_one({'_id': obj_id})
    if not celular_antigo:
        return jsonify({'erro': 'Celular não encontrado'}), 404
    
    data['updated_at'] = datetime.now()
    if '_id' in data:
        del data['_id']
    
    mongo.db.celulares.update_one({'_id': obj_id}, {'$set': data})
    registrar_historico(obj_id, celular_antigo, data, usuario=user_name)
    
    return jsonify({'msg': 'Celular atualizado com sucesso!'}), 200

@bp_celulares.route('/api/celulares/<id>', methods=['DELETE'])
@jwt_required()
def delete_celular(id):
    """Inativar celular (soft delete)"""
    claims = get_jwt()
    user_name = claims.get('nome', 'Unknown')
    
    try:
        obj_id = ObjectId(id)
    except:
        return jsonify({'erro': 'ID inválido'}), 400
    
    celular = mongo.db.celulares.find_one({'_id': obj_id})
    if not celular:
        return jsonify({'erro': 'Celular não encontrado'}), 404
    
    mongo.db.celulares.update_one(
        {'_id': obj_id},
        {'$set': {
            'status': 'Inativo',
            'deleted_at': datetime.now()
        }}
    )
    registrar_historico(obj_id, celular, {'status': 'Inativo'}, usuario=user_name)
    
    return jsonify({'msg': 'Celular inativado com sucesso!'}), 200
