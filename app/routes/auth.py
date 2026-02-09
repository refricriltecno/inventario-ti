from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models import db, Usuario, AuditLog
from app.auth import create_user, login_user, get_current_user
from sqlalchemy import func

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
    email = data.get('email')
    permissoes = data.get('permissoes', ['view'])
    
    if not all([username, password, nome, filial]):
        return jsonify({'erro': 'Dados incompletos'}), 400
    
    result, status_code = create_user(username, password, nome, filial, email, permissoes)
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
    usuarios = Usuario.query.all()
    return jsonify([u.to_dict() for u in usuarios]), 200

@bp_auth.route('/api/auth/usuarios/<int:usuario_id>', methods=['PUT'])
@jwt_required()
def update_usuario(usuario_id):
    """Atualiza permissões e status do usuário"""
    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        return jsonify({'erro': 'Usuário não encontrado'}), 404
    
    data = request.json
    
    if 'permissoes' in data:
        usuario.permissoes = data['permissoes']
    if 'ativo' in data:
        usuario.ativo = data['ativo']
    if 'nome' in data:
        usuario.nome = data['nome']
    if 'filial' in data:
        usuario.filial = data['filial']
    if 'email' in data:
        usuario.email = data['email']
    
    db.session.commit()
    return jsonify({'msg': 'Usuário atualizado com sucesso!'}), 200

@bp_auth.route('/api/auth/usuarios/<int:usuario_id>', methods=['DELETE'])
@jwt_required()
def delete_usuario(usuario_id):
    """Deleta um usuário"""
    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        return jsonify({'erro': 'Usuário não encontrado'}), 404
    
    db.session.delete(usuario)
    db.session.commit()
    return jsonify({'msg': 'Usuário deletado com sucesso!'}), 200


# --- ROTAS DE AUDITORIA/LOGS ---

@bp_auth.route('/api/logs/ativo/<int:asset_id>', methods=['GET'])
@jwt_required()
def get_logs_ativo(asset_id):
    """Retorna logs de um ativo específico"""
    logs = AuditLog.query.filter_by(entidade_id=str(asset_id)).order_by(AuditLog.timestamp.desc()).limit(100).all()
    return jsonify([log.to_dict() for log in logs]), 200

@bp_auth.route('/api/logs', methods=['GET'])
@jwt_required()
def get_logs():
    """Retorna todos os logs do sistema"""
    filtro_usuario = request.args.get('usuario')
    limite = int(request.args.get('limite', 100))
    
    query = AuditLog.query
    
    if filtro_usuario:
        query = query.filter_by(usuario_nome=filtro_usuario)
    
    logs = query.order_by(AuditLog.timestamp.desc()).limit(limite).all()
    return jsonify([log.to_dict() for log in logs]), 200

@bp_auth.route('/api/logs/estatisticas', methods=['GET'])
@jwt_required()
def get_estatisticas_logs():
    """Retorna estatísticas dos logs"""
    total_logs = db.session.query(func.count(AuditLog.id)).scalar()
    
    usuarios_unicos = db.session.query(AuditLog.usuario_nome).distinct().all()
    usuarios_unicos = [u[0] for u in usuarios_unicos if u[0]]
    
    acoes = db.session.query(AuditLog.acao).distinct().all()
    acoes = [a[0] for a in acoes]
    
    # Logs por ação
    logs_por_acao = {}
    for acao in acoes:
        count = db.session.query(func.count(AuditLog.id)).filter_by(acao=acao).scalar()
        logs_por_acao[acao] = count
    
    return jsonify({
        'total_logs': total_logs,
        'usuarios': usuarios_unicos,
        'acoes': acoes,
        'logs_por_acao': logs_por_acao
    }), 200
