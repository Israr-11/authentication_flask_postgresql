from flask import current_app
from flask_mail import Mail, Message
import os

class EmailService:
    def __init__(self):
        # MAIL WILL BE INITIALIZED WITH THE APP CONTEXT
        self.mail = None
    
    def init_mail(self, app):
        """Initialize the mail service with Flask app"""
        self.mail = Mail(app)
    
    def send_verification_email(self, user, token):
        """Send email verification link to the user"""
        if not self.mail:
            self.mail = Mail(current_app)
            
        # CREATE THE VERIFICATION URL
        # IN PRODUCTION, USE PROPER FRONTEND URL
        verification_url = f"http://localhost:5000/auth/verify-email/{token.token}"
        
        # PREPARE EMAIL CONTENT
        subject = "Verify Your Email Address"
        body = f"""
        Hello {user.name},
        
        Thank you for registering! Please verify your email by clicking the link below:
        
        {verification_url}
        
        This link will expire in 24 hours.
        
        Best regards,
        Israr Team
        """
        
        # SEND THE EMAIL
        msg = Message(
            subject=subject,
            recipients=[user.email],
            body=body,
            sender=current_app.config['MAIL_DEFAULT_SENDER'] or 'noreply@yourapp.com'
        )
        
        self.mail.send(msg)
        
    def send_password_reset_email(self, user, token):
        """Send password reset link to the user"""
        if not self.mail:
            self.mail = Mail(current_app)
            
        # CREATE THE RESET URL
        reset_url = f"http://localhost:5000/auth/reset-password/{token.token}"
        
        # PREPARE EMAIL CONTENT
        subject = "Password Reset Request"
        body = f"""
        Hello {user.name},
        
        You recently requested to reset your password. Click the link below to reset it:
        
        {reset_url}
        
        This link will expire in 24 hours.
        If you did not request a password reset, please ignore this email.
        
        Best regards,
        Israr Team
        """
        
        # SEND THE EMAIL
        msg = Message(
            subject=subject,
            recipients=[user.email],
            body=body,
            sender=current_app.config['MAIL_DEFAULT_SENDER'] or 'noreply@yourapp.com'
        )
        
        self.mail.send(msg)