from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from config import Config
from app.models import db

jwt = JWTManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializações
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Configurar CORS para aceitar requisições do frontend
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    jwt.init_app(app)

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