import os
from datetime import timedelta

class Config:
    # Database
    MONGO_URI = "mongodb+srv://tecnologia_db_user:afbn3vtexZUN3zPh@refricril.lfg6bem.mongodb.net/inventario_ti?appName=Refricril"
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sua-chave-super-secreta-mudeme-em-producao'
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'seu-jwt-secret-key-muito-seguro'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'