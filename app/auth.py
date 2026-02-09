import bcrypt
from flask_jwt_extended import create_access_token, get_jwt
from app.models import db, Usuario
from datetime import datetime

def hash_password(password):
    """Hash da senha com bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    """Verifica senha com bcrypt"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_user(username, password, nome, filial, email=None, permissoes=None):
    """Cria novo usuário"""
    if Usuario.query.filter_by(username=username).first():
        return {'erro': 'Usuário já existe'}, 400
    
    user = Usuario(
        username=username,
        password=hash_password(password),
        nome=nome,
        filial=filial,
        email=email,
        permissoes=permissoes or ['view'],
        ativo=True
    )
    
    db.session.add(user)
    db.session.commit()
    
    return {'id': str(user.id), 'msg': 'Usuário criado com sucesso!'}, 201

def get_user_by_username(username):
    """Busca usuário por username"""
    return Usuario.query.filter_by(username=username).first()

def login_user(username, password):
    """Autentica usuário"""
    user = get_user_by_username(username)
    
    if not user or not user.ativo:
        return {'erro': 'Usuário ou senha inválidos'}, 401
    
    if not verify_password(password, user.password):
        return {'erro': 'Usuário ou senha inválidos'}, 401
    
    # Criar token JWT
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={
            'username': user.username,
            'nome': user.nome,
            'filial': user.filial,
            'permissoes': user.permissoes or []
        }
    )
    
    return {
        'access_token': access_token,
        'usuario': {
            'id': str(user.id),
            'username': user.username,
            'nome': user.nome,
            'filial': user.filial,
            'permissoes': user.permissoes or []
        }
    }, 200

def get_current_user():
    """Retorna usuário atual do JWT"""
    claims = get_jwt()
    return {
        'id': claims.get('sub'),
        'username': claims.get('username'),
        'nome': claims.get('nome'),
        'filial': claims.get('filial'),
        'permissoes': claims.get('permissoes', [])
    }
