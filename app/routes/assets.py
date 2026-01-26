from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app import mongo
from app.services.audit import registrar_historico
from bson.objectid import ObjectId
from datetime import datetime

bp_assets = Blueprint('assets', __name__)

# --- ROTAS DE ATIVOS ---

@bp_assets.route('/api/assets', methods=['GET'])
@jwt_required()
def get_assets():
    filial = request.args.get('filial')
    query = {'filial': filial} if filial else {}
    assets = list(mongo.db.workstations.find(query))
    for asset in assets: asset['_id'] = str(asset['_id'])
    return jsonify(assets)

@bp_assets.route('/api/assets/<id>', methods=['GET'])
@jwt_required()
def get_one_asset(id):
    asset = mongo.db.workstations.find_one_or_404({'_id': ObjectId(id)})
    asset['_id'] = str(asset['_id'])
    return jsonify(asset)

@bp_assets.route('/api/assets', methods=['POST'])
@jwt_required()
def create_asset():
    claims = get_jwt()
    user_name = claims.get('nome', 'Unknown')
    data = request.json
    data['updated_at'] = datetime.now()
    res = mongo.db.workstations.insert_one(data)
    registrar_historico(res.inserted_id, None, data, usuario=user_name)
    return jsonify({"msg": "Criado com sucesso!", "id": str(res.inserted_id)}), 201

@bp_assets.route('/api/assets/<id>', methods=['PUT'])
@jwt_required()
def update_asset(id):
    claims = get_jwt()
    user_name = claims.get('nome', 'Unknown')
    data = request.json
    data['updated_at'] = datetime.now()
    if '_id' in data: del data['_id']
    antigo = mongo.db.workstations.find_one({'_id': ObjectId(id)})
    mongo.db.workstations.update_one({'_id': ObjectId(id)}, {'$set': data})
    registrar_historico(ObjectId(id), antigo, data, usuario=user_name)
    return jsonify({"msg": "Atualizado com sucesso!"}), 200

@bp_assets.route('/api/assets/<id>', methods=['DELETE'])
@jwt_required()
def delete_asset(id):
    claims = get_jwt()
    user_name = claims.get('nome', 'Unknown')
    asset = mongo.db.workstations.find_one({'_id': ObjectId(id)})
    
    if not asset:
        return jsonify({"erro": "Ativo não encontrado"}), 404
    
    # Opção 1: Marcar como Inativo (soft delete)
    mongo.db.workstations.update_one(
        {'_id': ObjectId(id)},
        {'$set': {'status': 'Inativo', 'deleted_at': datetime.now()}}
    )
    registrar_historico(ObjectId(id), asset, {'status': 'Inativo'}, usuario=user_name)
    return jsonify({"msg": "Ativo inativado com sucesso!"}), 200

# --- ROTAS DE FILIAIS (Gerenciamento Completo) ---

@bp_assets.route('/api/filiais', methods=['GET'])
def get_filiais():
    filiais = list(mongo.db.filiais.find().sort("nome", 1))
    for f in filiais: f['_id'] = str(f['_id'])
    return jsonify(filiais)

# --- NOVA ROTA: BUSCAR FUNCIONÁRIOS POR FILIAL ---

@bp_assets.route('/api/funcionarios/<filial>', methods=['GET'])
def get_funcionarios_by_filial(filial):
    """Retorna lista de funcionários de uma filial específica"""
    funcionarios = list(mongo.db.funcionarios.find({'filial': filial}).sort('nome', 1))
    # Retorna apenas nome para usar no select
    result = [f['nome'] for f in funcionarios]
    return jsonify(result)

@bp_assets.route('/api/filiais', methods=['POST'])
@jwt_required()
def create_filial():
    data = request.json
    nome = data.get('nome')
    tipo = data.get('tipo') 
    
    if not nome or not tipo:
        return jsonify({"erro": "Nome e Tipo são obrigatórios"}), 400
        
    if mongo.db.filiais.find_one({"nome": {"$regex": f"^{nome}$", "$options": "i"}}):
        return jsonify({"erro": "Filial já existe"}), 409

    mongo.db.filiais.insert_one({"nome": nome, "tipo": tipo})
    return jsonify({"msg": "Filial criada!"}), 201

# NOVA ROTA: DELETAR FILIAL
@bp_assets.route('/api/filiais/<id>', methods=['DELETE'])
@jwt_required()
def delete_filial(id):
    mongo.db.filiais.delete_one({'_id': ObjectId(id)})
    return jsonify({"msg": "Filial removida com sucesso!"}), 200