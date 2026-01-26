from flask import Flask
from flask_pymongo import PyMongo
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config

mongo = PyMongo()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    mongo.init_app(app)
    jwt.init_app(app)
    CORS(app)

    # JWT Error Handlers
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        print(f"INVALID TOKEN: {error}")
        return {'erro': f'Token inválido: {error}'}, 422

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        print(f"EXPIRED TOKEN")
        return {'erro': 'Token expirado'}, 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        print(f"MISSING TOKEN: {error}")
        return {'erro': f'Token ausente: {error}'}, 401

    from app.routes.assets import bp_assets
    from app.routes.auth import bp_auth
    from app.routes.celulares import bp_celulares
    from app.routes.softwares import bp_softwares
    from app.routes.emails import bp_emails
    
    app.register_blueprint(bp_assets)
    app.register_blueprint(bp_auth)
    app.register_blueprint(bp_celulares)
    app.register_blueprint(bp_softwares)
    app.register_blueprint(bp_emails)

    return app