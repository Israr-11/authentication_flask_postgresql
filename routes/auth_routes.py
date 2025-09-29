from flask import Blueprint
from controllers.auth_controller import AuthController

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
auth_controller = AuthController()

# REGISTRATION AND EMAIL VERIFICATION ROUTES
@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user and send verification email"""
    return auth_controller.register()

@auth_bp.route('/verify/<token>', methods=['GET'])
def verify_email(token):
    """Verify user email with token from email"""
    return auth_controller.verify_email(token)

# LOGIN, REFRESH AND LOGOUT ROUTES
@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and issue tokens"""
    return auth_controller.login()

@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    """Generate new access token using refresh token"""
    return auth_controller.refresh()

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Log user out and invalidate tokens"""
    return auth_controller.logout()

# PASSWORD RESET ROUTES
@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Request password reset email"""
    return auth_controller.forgot_password()

@auth_bp.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    """Reset password using token from email"""
    return auth_controller.reset_password(token)

# PROTECTED ROUTE EXAMPLE
@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """Get current user (example of protected route)"""
    return auth_controller.get_current_user()