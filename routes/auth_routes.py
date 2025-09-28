from flask import Blueprint
from controllers.auth_controller import AuthController

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
auth_controller = AuthController()

@auth_bp.route('/register', methods=['POST'])
def register():
    return auth_controller.register()

@auth_bp.route('/login', methods=['POST'])
def login():
    return auth_controller.login()

@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    return auth_controller.refresh()