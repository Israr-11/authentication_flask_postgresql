from flask import Flask
from configuration.config import Config
#from routes.user_routes import user_bp
from models.auth_model import db
from routes.auth_routes import auth_bp
from flask_jwt_extended import JWTManager


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    
    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)

    
    # Register blueprints
    app.register_blueprint(auth_bp)

if __name__ == '__main__':
    app = create_app()
    # Uncomment to create tables on startup
    # with app.app_context():
    #     db.create_all()
    
    app.run(debug=True)
