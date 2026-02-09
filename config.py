import os
from datetime import timedelta

class Config:
    # Database - PostgreSQL
    # Senha: Adm@Ref212 (@ precisa ser %40 em URL encoding)
    SQLALCHEMY_DATABASE_URI = "postgresql://user_inventario:Adm%40Ref212@10.1.1.248/inventario-ti?sslmode=disable"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }
    
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sua-chave-super-secreta-mudeme-em-producao'
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'seu-jwt-secret-key-muito-seguro'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'