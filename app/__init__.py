from flask import Flask
from flask_pymongo import PyMongo
from flask_cors import CORS
from flask_jwt_extended import JWTManager # <--- 1. Importar isso
from config import Config

mongo = PyMongo()
jwt = JWTManager() # <--- 2. Criar o objeto

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializações
    mongo.init_app(app)
    CORS(app)
    jwt.init_app(app) # <--- 3. Ligar o JWT ao App (Fundamental!)

    # Importação dos Blueprints
    from app.routes.assets import bp_assets
    from app.routes.auth import bp_auth
    from app.routes.celulares import bp_celulares
    from app.routes.emails import bp_emails
    from app.routes.softwares import bp_softwares
    from app.routes.imports import bp_imports

    # Registro dos Blueprints
    app.register_blueprint(bp_assets)
    app.register_blueprint(bp_auth)
    app.register_blueprint(bp_celulares)
    app.register_blueprint(bp_emails)
    app.register_blueprint(bp_softwares)
    app.register_blueprint(bp_imports)

    return app