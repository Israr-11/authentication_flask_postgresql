from datetime import datetime, timezone, timedelta
from models.user_model import db, User
from models.verification_model import VerificationToken
from models.refresh_token_model import RefreshToken
from services.email_service import EmailService
from flask_jwt_extended import create_access_token
from flask import current_app
import re

class AuthService:
    def __init__(self):
        self.email_service = None  # INITIALIZED ON DEMAND TO AVOID CIRCULAR IMPORTS
        
    def _get_email_service(self):
        """Lazy load email service to avoid circular imports"""
        if self.email_service is None:
            self.email_service = EmailService()
        return self.email_service
        
    def register_user(self, name, email, password):
        """Register a new user"""
        # CHECK IF USER ALREADY EXISTS
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return None, "Email already registered"
            
        # VALIDATE EMAIL FORMAT
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return None, "Invalid email format"
            
        # VALIDATE PASSWORD STRENGTH
        if len(password) < 8:
            return None, "Password must be at least 8 characters"
            
        # CREATE NEW USER (UNVERIFIED)
        user = User(
            name=name,
            email=email,
            is_verified=False,
            role='user'
        )
        user.set_password(password)
        
        # SAVE TO DATABASE
        db.session.add(user)
        db.session.commit()
        
        # GENERATE VERIFICATION TOKEN
        verification_token = VerificationToken.generate_token(
            user_id=user.id,
            token_type='email',
            expiration_hours=24
        )
        
        # SEND VERIFICATION EMAIL
        try:
            self._get_email_service().send_verification_email(
                user.email,
                user.name,
                verification_token
            )
        except Exception as e:
            current_app.logger.error(f"Failed to send verification email: {str(e)}")
            # WE STILL RETURN SUCCESS TO USER EVEN IF EMAIL FAILS
        
        return user, None
        
    def verify_email(self, token):
        """Verify user email with token"""
        user_id = VerificationToken.validate_token(token, 'email')
        
        if not user_id:
            return False, "Invalid or expired verification link"
            
        user = User.query.get(user_id)
        if not user:
            return False, "User not found"
            
        # MARK USER AS VERIFIED
        user.is_verified = True
        db.session.commit()
        
        return True, "Email verified successfully! You can now log in."
        
    def authenticate_user(self, email, password, request_info=None):
        """Authenticate user and generate tokens"""
        user = User.query.filter_by(email=email).first()
        
        # CHECK IF USER EXISTS AND PASSWORD IS CORRECT
        if not user or not user.check_password(password):
            return None, "Invalid email or password"
            
        # CHECK IF USER IS VERIFIED
        if not user.is_verified:
            return None, "Please verify your email before logging in"
            
        # GENERATE ACCESS TOKEN
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                "email": user.email,
                "role": user.role
            }
        )
        
        # CREATE REFRESH TOKEN WITH DEVICE INFO
        refresh_token = self._create_refresh_token(
            user.id, 
            ip_address=request_info.get('ip') if request_info else None,
            user_agent=request_info.get('device') if request_info else None
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user.to_dict()
        }, None
        
    def refresh_access_token(self, refresh_token_str):
        """Generate new access token using refresh token"""
        # VALIDATE REFRESH TOKEN
        is_valid, user_id = RefreshToken.is_valid(refresh_token_str)
        
        if not is_valid or not user_id:
            return None, "Invalid or expired refresh token"
            
        user = User.query.get(user_id)
        if not user:
            return None, "User not found"
            
        # GENERATE NEW ACCESS TOKEN
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                "email": user.email,
                "role": user.role
            }
        )
        
        return {"access_token": access_token}, None
        
    def logout(self, refresh_token_str):
        """Revoke refresh token on logout"""
        if refresh_token_str:
            RefreshToken.revoke(refresh_token_str)
        return True
        
    def request_password_reset(self, email):
        """Generate and send password reset token"""
        user = User.query.filter_by(email=email).first()
    
        # DON'T REVEAL IF EMAIL EXISTS FOR SECURITY
        if not user:
            return True, None
            
        # GENERATE PASSWORD RESET TOKEN (EXPIRES IN 1 HOUR)
        reset_token = VerificationToken.generate_token(
            user_id=user.id,
            token_type='password_reset',
            expiration_hours=1
        )
        
        print("Reset Token:", reset_token)  # FOR DEBUGGING PURPOSES
        # SEND PASSWORD RESET EMAIL
        try:
            self._get_email_service().send_password_reset_email(
                user.email,
                user.name,
                reset_token
            )
        except Exception as e:
            current_app.logger.error(f"Failed to send password reset email: {str(e)}")
            return False, "Failed to send password reset email"
            
        return True, None
        
    def reset_password(self, token, new_password):
        """Reset user password using token"""
        user_id = VerificationToken.validate_token(token, 'password_reset')
        
        if not user_id:
            return False, "Invalid or expired reset link"
            
        # VALIDATE PASSWORD STRENGTH
        if len(new_password) < 8:
            return False, "Password must be at least 8 characters"
            
        user = User.query.get(user_id)
        if not user:
            return False, "User not found"
            
        # UPDATE PASSWORD
        user.set_password(new_password)
        
        # REVOKE ALL REFRESH TOKENS FOR THIS USER (FORCE LOGIN AGAIN)
        RefreshToken.query.filter_by(user_id=user.id).update({'is_revoked': True})
        
        db.session.commit()
        
        return True, "Password reset successfully! You can now log in with your new password."
        
    def _create_refresh_token(self, user_id, ip_address=None, user_agent=None):
        """Create and store refresh token"""
        # GENERATE TOKEN
        token_str = RefreshToken.generate_token()
        
        # SET EXPIRATION (30 DAYS)
        expires_at = datetime.now(timezone.utc) + timedelta(
            seconds=current_app.config.get('JWT_REFRESH_TOKEN_EXPIRES', 2592000)
        )
        
        # CREATE TOKEN RECORD
        token = RefreshToken(
            token=token_str,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at
        )
        
        db.session.add(token)
        db.session.commit()
        
        return token_str