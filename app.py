from flask import Flask, jsonify
from configuration.config import Config
from models.user_model import db
from routes.auth_routes import auth_bp
from flask_jwt_extended import JWTManager
from sqlalchemy import text

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)

    # Register blueprints
    app.register_blueprint(auth_bp)

    # Home/status route
    @app.route("/")
    def home():
        # Check DB connection
        try:
            with app.app_context():
                db.session.execute(text("SELECT 1"))
            db_status = "Connected"
        except Exception as e:
            db_status = f"Error: {str(e)}"

        # Get port (from config if you set one)
        port = app.config.get("PORT", 5000)

        return jsonify({
            "message": "Flask app is running!",
            "port": port,
            "database": db_status
        })

    return app

if __name__ == '__main__':
    app = create_app()
    # Uncomment to create tables on startup
    # with app.app_context():
    #     db.create_all()

    app.run(debug=True)
