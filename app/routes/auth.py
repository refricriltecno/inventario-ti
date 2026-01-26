from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import mongo
from app.auth import create_user, login_user, get_current_user
from app.services.audit import obter_logs_ativo, obter_todos_os_logs
from bson.objectid import ObjectId
from datetime import datetime

bp_auth = Blueprint('auth', __name__)

# --- ROTAS DE AUTENTICAÇÃO ---

@bp_auth.route('/api/auth/login', methods=['POST'])
def login():
    """Login do usuário"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'erro': 'Username e password são obrigatórios'}), 400
    
    result, status_code = login_user(username, password)
    return jsonify(result), status_code

@bp_auth.route('/api/auth/register', methods=['POST'])
def register():
    """Registrar novo usuário (apenas admin)"""
    data = request.json
    
    username = data.get('username')
    password = data.get('password')
    nome = data.get('nome')
    filial = data.get('filial')
    
    if not all([username, password, nome, filial]):
        return jsonify({'erro': 'Dados incompletos'}), 400
    
    result, status_code = create_user(username, password, nome, filial)
    return jsonify(result), status_code

@bp_auth.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_me():
    """Retorna dados do usuário autenticado"""
    current_user = get_current_user()
    return jsonify(current_user), 200

@bp_auth.route('/api/auth/usuarios', methods=['GET'])
@jwt_required()
def list_usuarios():
    """Lista todos os usuários (apenas admin)"""
    usuarios = list(mongo.db.usuarios.find({}, {'senha': 0}))
    for u in usuarios:
        u['_id'] = str(u['_id'])
        u['created_at'] = u['created_at'].isoformat()
        u['updated_at'] = u['updated_at'].isoformat()
        if 'ultimo_login' in u:
            u['ultimo_login'] = u['ultimo_login'].isoformat()
    return jsonify(usuarios), 200

@bp_auth.route('/api/auth/usuarios/<usuario_id>', methods=['PUT'])
@jwt_required()
def update_usuario(usuario_id):
    """Atualiza permissões e status do usuário"""
    data = request.json
    
    update_fields = {}
    if 'permissoes' in data:
        update_fields['permissoes'] = data['permissoes']
    if 'ativo' in data:
        update_fields['ativo'] = data['ativo']
    if 'nome' in data:
        update_fields['nome'] = data['nome']
    if 'filial' in data:
        update_fields['filial'] = data['filial']
    
    update_fields['updated_at'] = datetime.now()
    
    result = mongo.db.usuarios.update_one(
        {'_id': ObjectId(usuario_id)},
        {'$set': update_fields}
    )
    
    if result.matched_count == 0:
        return jsonify({'erro': 'Usuário não encontrado'}), 404
    
    return jsonify({'msg': 'Usuário atualizado com sucesso!'}), 200

@bp_auth.route('/api/auth/usuarios/<usuario_id>', methods=['DELETE'])
@jwt_required()
def delete_usuario(usuario_id):
    """Deleta um usuário"""
    result = mongo.db.usuarios.delete_one({'_id': ObjectId(usuario_id)})
    
    if result.deleted_count == 0:
        return jsonify({'erro': 'Usuário não encontrado'}), 404
    
    return jsonify({'msg': 'Usuário deletado com sucesso!'}), 200

# --- ROTAS DE AUDITORIA/LOGS ---

@bp_auth.route('/api/logs/ativo/<asset_id>', methods=['GET'])
@jwt_required()
def get_logs_ativo(asset_id):
    """Retorna logs de um ativo específico"""
    try:
        logs = obter_logs_ativo(asset_id)
        return jsonify(logs), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 400

@bp_auth.route('/api/logs', methods=['GET'])
@jwt_required()
def get_logs():
    """Retorna todos os logs do sistema"""
    filtro_usuario = request.args.get('usuario')
    limite = int(request.args.get('limite', 100))
    
    logs = obter_todos_os_logs(filtro_usuario=filtro_usuario, limite=limite)
    return jsonify(logs), 200

@bp_auth.route('/api/logs/estatisticas', methods=['GET'])
@jwt_required()
def get_estatisticas_logs():
    """Retorna estatísticas dos logs"""
    total_logs = mongo.db.logs.count_documents({})
    usuarios_unicos = mongo.db.logs.distinct('usuario')
    acoes = mongo.db.logs.distinct('acao')
    
    # Logs por ação
    logs_por_acao = {}
    for acao in acoes:
        count = mongo.db.logs.count_documents({'acao': acao})
        logs_por_acao[acao] = count
    
    return jsonify({
        'total_logs': total_logs,
        'usuarios': usuarios_unicos,
        'acoes': acoes,
        'logs_por_acao': logs_por_acao
    }), 200
