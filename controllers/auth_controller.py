from flask import request, jsonify, make_response
from services.auth_service import AuthService
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.user_model import User

class AuthController:
    def __init__(self):
        self.auth_service = AuthService()
    
    def register(self):
        """Register a new user"""
        data = request.get_json()
        
        # VALIDATE INPUT
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        
        if not name or not email or not password:
            return jsonify({"error": "Name, email, and password are required"}), 400
        
        # REGISTER USER THROUGH SERVICE
        user, error = self.auth_service.register_user(name, email, password)
        
        if error:
            return jsonify({"error": error}), 400
        
        # RESPOND WITH SUCCESS MESSAGE
        return jsonify({
            "message": "Registration successful! Please check your email for verification link.",
            "user": user.to_dict()
        }), 201
    
    def verify_email(self, token):
        """Verify a user's email address"""
        success, message = self.auth_service.verify_email(token)
        
        if not success:
            return jsonify({"error": message}), 400
        
        # COULD REDIRECT TO FRONTEND SUCCESS PAGE
        return jsonify({"message": message}), 200
    
    def login(self):
        """Login a user"""
        data = request.get_json()
        
        # VALIDATE INPUT
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        
        # COLLECT DEVICE INFO FOR SECURITY
        request_info = {
            "ip": request.remote_addr,
            "device": request.user_agent.string
        }
        
        # AUTHENTICATE USER
        result, error = self.auth_service.authenticate_user(email, password, request_info)
        
        if error:
            return jsonify({"error": error}), 401
        
        # CREATE RESPONSE WITH HTTP-ONLY COOKIE FOR ACCESS TOKEN
        response = make_response(jsonify({
            "message": "Login successful",
            "user": result["user"]
        }))
        
        # SET ACCESS TOKEN IN HTTP-ONLY COOKIE
        response.set_cookie(
            'access_token',
            result["access_token"],
            httponly=True,
            secure=request.is_secure,  # TRUE IN PRODUCTION
            max_age=3600,  # 1 HOUR
            samesite='Lax'  # HELPS PREVENT CSRF
        )
        
        # SEND REFRESH TOKEN IN RESPONSE FOR STORAGE
        # CLIENT SHOULD STORE THIS SECURELY
        response.json["refresh_token"] = result["refresh_token"]
        
        return response
    
    def refresh(self):
        """Generate new access token using refresh token"""
        data = request.get_json()
        print("Refresh request data:", data)  # FOR DEBUGGING PURPOSES
        if not data or not data.get('refresh_token'):
            return jsonify({"error": "Refresh token is required"}), 400
        
        refresh_token = data.get('refresh_token')
        print("Received refresh token:", refresh_token)  # FOR DEBUGGING PURPOSES
        
        # GET NEW ACCESS TOKEN
        result, error = self.auth_service.refresh_access_token(refresh_token)
        
        if error:
            return jsonify({"error": error}), 401
        
        # CREATE RESPONSE WITH HTTP-ONLY COOKIE FOR NEW ACCESS TOKEN
        response = make_response(jsonify({"message": "Token refreshed successfully"}))
        
        # SET NEW ACCESS TOKEN IN HTTP-ONLY COOKIE
        response.set_cookie(
            'access_token',
            result["access_token"],
            httponly=True,
            secure=request.is_secure,  # TRUE IN PRODUCTION
            max_age=3600,  # 1 HOUR
            samesite='Lax'  # HELPS PREVENT CSRF
        )
        
        return response
    
    def logout(self):
        """Log user out by invalidating tokens"""
        data = request.get_json() or {}
        refresh_token = data.get('refresh_token')
        
        # INVALIDATE REFRESH TOKEN
        self.auth_service.logout(refresh_token)
        
        # CLEAR ACCESS TOKEN COOKIE
        response = make_response(jsonify({"message": "Logout successful"}))
        response.delete_cookie('access_token')
        
        return response
    
    def forgot_password(self):
        """Request password reset email"""
        data = request.get_json()
        
        if not data or not data.get('email'):
            return jsonify({"error": "Email is required"}), 400
        
        email = data.get('email')
        print("Email for password reset:", email)  # FOR DEBUGGING PURPOSES
        # REQUEST PASSWORD RESET
        success, error = self.auth_service.request_password_reset(email)
        
        if not success:
            # DON'T REVEAL IF EMAIL EXISTS FOR SECURITY
            return jsonify({"message": "If your email exists in our system, you will receive a password reset link"}), 200
        
        return jsonify({
            "message": "Password reset instructions sent to your email"
        }), 200
    
    def reset_password(self, token):
        """Reset password using token"""
        data = request.get_json()
        
        if not data or not data.get('password'):
            return jsonify({"error": "New password is required"}), 400
        
        new_password = data.get('password')
        
        # RESET PASSWORD
        success, message = self.auth_service.reset_password(token, new_password)
        
        if not success:
            return jsonify({"error": message}), 400
        
        return jsonify({"message": message}), 200
    
    @jwt_required()
    def get_current_user(self):
        """Get current user details (protected route example)"""
        # GET USER ID FROM ACCESS TOKEN
        user_id = get_jwt_identity()
        print("Current user ID from token:", user_id)  # FOR DEBUGGING PURPOSES
        # GET USER FROM DATABASE
        user = User.query.get(int(user_id))
        
        if not user:
            return jsonify({"error": "User not found"}), 404
            
        return jsonify({"user": user.to_dict()}), 200