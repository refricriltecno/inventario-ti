import bcrypt
from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt
from app import mongo
from datetime import datetime

def hash_password(password):
    """Hash da senha com bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    """Verifica senha com bcrypt"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_user(username, password, nome, filial, permissoes=['view']):
    """Cria novo usuário"""
    if mongo.db.usuarios.find_one({'username': username}):
        return {'erro': 'Usuário já existe'}, 400
    
    user = {
        'username': username,
        'senha': hash_password(password),
        'nome': nome,
        'filial': filial,
        'permissoes': permissoes,
        'created_at': datetime.now(),
        'updated_at': datetime.now(),
        'ativo': True
    }
    
    result = mongo.db.usuarios.insert_one(user)
    return {'id': str(result.inserted_id), 'msg': 'Usuário criado com sucesso!'}, 201

def get_user_by_username(username):
    """Busca usuário por username"""
    return mongo.db.usuarios.find_one({'username': username})

def login_user(username, password):
    """Autentica usuário"""
    user = get_user_by_username(username)
    
    if not user or not user.get('ativo'):
        return {'erro': 'Usuário ou senha inválidos'}, 401
    
    if not verify_password(password, user['senha']):
        return {'erro': 'Usuário ou senha inválidos'}, 401
    
    # Atualizar último login
    mongo.db.usuarios.update_one(
        {'_id': user['_id']},
        {'$set': {'ultimo_login': datetime.now()}}
    )
    
    # Criar token JWT - identity deve ser string (user ID)
    access_token = create_access_token(
        identity=str(user['_id']),
        additional_claims={
            'username': user['username'],
            'nome': user['nome'],
            'filial': user['filial'],
            'permissoes': user['permissoes']
        }
    )
    
    return {
        'access_token': access_token,
        'usuario': {
            'id': str(user['_id']),
            'username': user['username'],
            'nome': user['nome'],
            'filial': user['filial'],
            'permissoes': user['permissoes']
        }
    }, 200

def get_current_user():
    """Retorna usuário atual do JWT - retorna os claims completos"""
    claims = get_jwt()
    return {
        'id': claims.get('sub'),  # 'sub' é o identity (user ID)
        'username': claims.get('username'),
        'nome': claims.get('nome'),
        'filial': claims.get('filial'),
        'permissoes': claims.get('permissoes', [])
    }
