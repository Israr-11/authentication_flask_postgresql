from datetime import datetime, timezone, timedelta
from flask import current_app
from flask_jwt_extended import create_access_token, create_refresh_token, decode_token
from models.user_model import db, User
from models.verification_model import VerificationToken
from models.refresh_token_model import RefreshToken
from services.email_service import EmailService
import bcrypt

class AuthService:
    def __init__(self):
        self.email_service = EmailService()
    
    def register_user(self, name, email, password, role="user"):
        """Register a new user and send verification email"""
        # CHECK IF USER ALREADY EXISTS
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return None, "Email already registered"
        
        try:
            # CREATE NEW USER WITH VERIFIED=FALSE
            user = User(
                name=name,
                email=email,
                role=role,
                is_verified=False
            )
            user.set_password(password)
            
            # SAVE USER TO DATABASE
            db.session.add(user)
            db.session.flush()  # To get the user ID without committing
            
            # GENERATE VERIFICATION TOKEN
            token = VerificationToken.generate_token(user.id, "email")
            
            # COMMIT TRANSACTION
            db.session.commit()
            
            # SEND VERIFICATION EMAIL
            self.email_service.send_verification_email(user, token)
            
            return user, None
        
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    def verify_email(self, token_string):
        """Verify a user's email address using token"""
        # FIND THE TOKEN IN DATABASE
        token = VerificationToken.query.filter_by(token=token_string, type="email").first()
        
        if not token or not token.is_valid():
            return False, "Invalid or expired verification link"
        
        try:
            # GET THE USER
            user = User.query.get(token.user_id)
            
            if not user:
                return False, "User not found"
            
            # MARK USER AS VERIFIED
            user.is_verified = True
            
            # INVALIDATE TOKEN AFTER USE
            token.use_token()
            
            db.session.commit()
            return True, "Email verified successfully"
            
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    def authenticate_user(self, email, password, request_info=None):
        """Authenticate a user and return tokens if valid"""
        # FIND USER BY EMAIL
        user = User.query.filter_by(email=email).first()
        
        # CHECK IF USER EXISTS AND PASSWORD IS CORRECT
        if not user or not user.check_password(password):
            return None, "Invalid email or password"
        
        # CHECK IF EMAIL IS VERIFIED
        if not user.is_verified:
            return None, "Email not verified. Please check your inbox for verification link."
        
        try:
            # GENERATE TOKENS
            access_token = create_access_token(identity=user.id)
            refresh_token_str = create_refresh_token(identity=user.id)
            
            # DECODE REFRESH TOKEN TO GET EXPIRY
            decoded = decode_token(refresh_token_str)
            expires_at = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
            
            # STORE REFRESH TOKEN IN DATABASE
            refresh_token = RefreshToken(
                token=refresh_token_str,
                user_id=user.id,
                expires_at=expires_at,
                device_info=request_info.get("device") if request_info else None,
                ip_address=request_info.get("ip") if request_info else None
            )
            
            db.session.add(refresh_token)
            db.session.commit()
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token_str,
                "user": user.to_dict()
            }, None
            
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    def refresh_access_token(self, refresh_token_str):
        """Generate a new access token from refresh token"""
        # VERIFY REFRESH TOKEN EXISTS IN DATABASE
        token_record = RefreshToken.query.filter_by(token=refresh_token_str).first()
        
        if not token_record or not token_record.is_valid():
            return None, "Invalid or expired refresh token"
        
        try:
            # CREATE NEW ACCESS TOKEN
            access_token = create_access_token(identity=token_record.user_id)
            return {"access_token": access_token}, None
            
        except Exception as e:
            return None, str(e)
    
    def logout(self, refresh_token_str):
        """Invalidate refresh token on logout"""
        if not refresh_token_str:
            return True, None  # Nothing to do
            
        token = RefreshToken.query.filter_by(token=refresh_token_str).first()
        
        if token:
            # INVALIDATE TOKEN
            token.invalidate()
            
        return True, None
    
    def request_password_reset(self, email):
        """Send password reset email to user"""
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return False, "Email not found"
        
        try:
            # GENERATE PASSWORD RESET TOKEN
            token = VerificationToken.generate_token(user.id, "password_reset")
            
            # SEND PASSWORD RESET EMAIL
            self.email_service.send_password_reset_email(user, token)
            
            return True, None
            
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    def reset_password(self, token_string, new_password):
        """Reset user password using token"""
        # FIND TOKEN IN DATABASE
        token = VerificationToken.query.filter_by(token=token_string, type="password_reset").first()
        
        if not token or not token.is_valid():
            return False, "Invalid or expired reset link"
        
        try:
            # GET USER
            user = User.query.get(token.user_id)
            
            if not user:
                return False, "User not found"
            
            # UPDATE PASSWORD
            user.set_password(new_password)
            
            # INVALIDATE TOKEN AFTER USE
            token.use_token()
            
            # INVALIDATE ALL EXISTING REFRESH TOKENS FOR SECURITY
            RefreshToken.query.filter_by(user_id=user.id).update({
                "expires_at": datetime.now(timezone.utc)
            })
            
            db.session.commit()
            return True, "Password reset successful"
            
        except Exception as e:
            db.session.rollback()
            return False, str(e)