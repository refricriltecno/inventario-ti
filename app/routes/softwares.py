from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app import mongo
from app.services.audit import registrar_historico
from bson.objectid import ObjectId
from datetime import datetime

bp_softwares = Blueprint('softwares', __name__)

# --- ROTAS DE SOFTWARES/LICENÇAS ---

@bp_softwares.route('/api/softwares', methods=['GET'])
@jwt_required()
def get_softwares():
    """Listar todos os softwares, opcionalmente filtrar por asset_id ou filial"""
    asset_id = request.args.get('asset_id')
    filial = request.args.get('filial')
    
    query = {}
    if asset_id:
        try:
            query['asset_id'] = ObjectId(asset_id)
        except:
            pass
    if filial:
        query['filial'] = filial
    
    softwares = list(mongo.db.softwares.find(query))
    for software in softwares:
        software['_id'] = str(software['_id'])
        if 'asset_id' in software:
            software['asset_id'] = str(software['asset_id'])
    
    return jsonify(softwares), 200

@bp_softwares.route('/api/softwares/<id>', methods=['GET'])
@jwt_required()
def get_software(id):
    """Obter detalhes de um software específico"""
    try:
        software = mongo.db.softwares.find_one({'_id': ObjectId(id)})
        if not software:
            return jsonify({'erro': 'Software não encontrado'}), 404
        software['_id'] = str(software['_id'])
        if 'asset_id' in software:
            software['asset_id'] = str(software['asset_id'])
        return jsonify(software), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 400

@bp_softwares.route('/api/softwares', methods=['POST'])
@jwt_required()
def create_software():
    """Criar novo software/licença"""
    claims = get_jwt()
    user_name = claims.get('nome', 'Unknown')
    data = request.json
    
    # Validações obrigatórias
    if not data.get('nome') or not data.get('asset_id'):
        return jsonify({'erro': 'Nome e Asset ID são obrigatórios'}), 400
    
    # Converter asset_id para ObjectId se for string
    if isinstance(data.get('asset_id'), str):
        try:
            data['asset_id'] = ObjectId(data['asset_id'])
        except:
            return jsonify({'erro': 'Asset ID inválido'}), 400
    
    data['created_at'] = datetime.now()
    data['updated_at'] = datetime.now()
    data['status'] = data.get('status', 'Ativo')
    
    result = mongo.db.softwares.insert_one(data)
    registrar_historico(result.inserted_id, None, data, usuario=user_name)
    
    return jsonify({
        'msg': 'Software/Licença criado com sucesso!',
        'id': str(result.inserted_id)
    }), 201

@bp_softwares.route('/api/softwares/<id>', methods=['PUT'])
@jwt_required()
def update_software(id):
    """Atualizar software/licença existente"""
    claims = get_jwt()
    user_name = claims.get('nome', 'Unknown')
    data = request.json
    
    try:
        obj_id = ObjectId(id)
    except:
        return jsonify({'erro': 'ID inválido'}), 400
    
    software_antigo = mongo.db.softwares.find_one({'_id': obj_id})
    if not software_antigo:
        return jsonify({'erro': 'Software não encontrado'}), 404
    
    # Converter asset_id para ObjectId se for string
    if 'asset_id' in data and isinstance(data.get('asset_id'), str):
        try:
            data['asset_id'] = ObjectId(data['asset_id'])
        except:
            return jsonify({'erro': 'Asset ID inválido'}), 400
    
    data['updated_at'] = datetime.now()
    if '_id' in data:
        del data['_id']
    
    mongo.db.softwares.update_one({'_id': obj_id}, {'$set': data})
    registrar_historico(obj_id, software_antigo, data, usuario=user_name)
    
    return jsonify({'msg': 'Software/Licença atualizado com sucesso!'}), 200

@bp_softwares.route('/api/softwares/<id>', methods=['DELETE'])
@jwt_required()
def delete_software(id):
    """Inativar software/licença (soft delete)"""
    claims = get_jwt()
    user_name = claims.get('nome', 'Unknown')
    
    try:
        obj_id = ObjectId(id)
    except:
        return jsonify({'erro': 'ID inválido'}), 400
    
    software = mongo.db.softwares.find_one({'_id': obj_id})
    if not software:
        return jsonify({'erro': 'Software não encontrado'}), 404
    
    mongo.db.softwares.update_one(
        {'_id': obj_id},
        {'$set': {
            'status': 'Inativo',
            'deleted_at': datetime.now()
        }}
    )
    registrar_historico(obj_id, software, {'status': 'Inativo'}, usuario=user_name)
    
    return jsonify({'msg': 'Software/Licença inativado com sucesso!'}), 200

# --- ROTAS AUXILIARES ---

@bp_softwares.route('/api/softwares/verificar-vencimento', methods=['GET'])
@jwt_required()
def verificar_vencimento():
    """Listar softwares prestes a vencer (próximos 30 dias)"""
    dias = int(request.args.get('dias', 30))
    
    from datetime import timedelta
    data_limite = datetime.now() + timedelta(days=dias)
    
    softwares = list(mongo.db.softwares.find({
        'dt_vencimento': {
            '$gte': datetime.now(),
            '$lte': data_limite
        },
        'status': 'Ativo'
    }))
    
    for software in softwares:
        software['_id'] = str(software['_id'])
        if 'asset_id' in software:
            software['asset_id'] = str(software['asset_id'])
    
    return jsonify(softwares), 200
