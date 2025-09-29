from flask import current_app
from flask_mail import Mail, Message

class EmailService:
    def __init__(self):
        self.mail = Mail(current_app)
        
    def send_verification_email(self, user_email, user_name, verification_token):
        """Send email verification link to user"""
        # CREATE EMAIL VERIFICATION URL
        verification_url = f"{current_app.config.get('FRONTEND_URL', 'http://localhost:5000')}/auth/verify/{verification_token}"
        
        subject = "Verify Your Email Address"
        body = f"""
        Hi {user_name},
        
        Thank you for registering! Please verify your email address by clicking the link below:
        
        {verification_url}
        
        This link will expire in 24 hours.
        
        If you did not register for an account, please ignore this email.
        
        Best regards,
        The Team
        """
        
        self._send_email(user_email, subject, body)
        
    def send_password_reset_email(self, user_email, user_name, reset_token):
        """Send password reset link to user"""
        # CREATE PASSWORD RESET URL
        reset_url = f"{current_app.config.get('FRONTEND_URL', 'http://localhost:5000')}/auth/reset-password/{reset_token}"
        
        subject = "Reset Your Password"
        body = f"""
        Hi {user_name},
        
        We received a request to reset your password. If this was you, please click the link below to reset your password:
        
        {reset_url}
        
        This link will expire in 1 hour.
        
        If you did not request a password reset, please ignore this email.
        
        Best regards,
        The Team
        """
        
        self._send_email(user_email, subject, body)
        
    def _send_email(self, to, subject, body):
        """Helper method to send an email"""
        msg = Message(
            subject=subject,
            recipients=[to],
            body=body,
            sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@example.com')
        )
        
        self.mail.send(msg)