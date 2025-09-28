from flask import request, jsonify
from services.auth_service import AuthService
from flask_jwt_extended import jwt_required, get_jwt_identity

class AuthController:
    def __init__(self):
        self.auth_service = AuthService()
    
    def register(self):
        """Register a new user"""
        data = request.get_json()
        
        # IF DATA OR EMAIL, NAME OR PASSWORD MISSING, RETURN ERROR
        if not data or not data.get('email') or not data.get('name') or not data.get('password'):
            return jsonify({"error": "Email, name and password are required"}), 400

        user, error = self.auth_service.register_user(data.get('email'), data.get('name'), data.get('password'))

        if error:
            return jsonify({"error": error}), 400
        
        return jsonify({"message": "User registered successfully", "user": user.to_dict()}), 201
    
    def login(self):
        """Login a user"""
        data = request.get_json()
        
        # Validate input
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({"error": "Email and password are required"}), 400

        result, error = self.auth_service.authenticate_user(data.get('email'), data.get('password'))

        if error:
            return jsonify({"error": error}), 401
        
        return jsonify(result), 200
    
    @jwt_required(refresh=True)
    def refresh(self):
        """Generate a new access token using refresh token"""
        # GET THE IDENTITY FROM THE REFRESH TOKEN
        current_user = get_jwt_identity()
        
        # CREATING A NEW ACCESS TOKEN
        access_token = self.auth_service.refresh_access_token(current_user)
        
        return jsonify(access_token=access_token), 200