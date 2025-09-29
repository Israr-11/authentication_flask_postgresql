from models.user_model import db, User
from flask_jwt_extended import create_access_token, create_refresh_token
from email_validator import validate_email, EmailNotValidError

class AuthService:
    def register_user(self, email, name, password):
        """Register a new user"""

        print(f'Attempting to register user with email: {email}')
        print(f'Name: {name}, Password: {"*" * len(password) if password else None}')
        # Validate email
        try:
            validate_email(email)
        except EmailNotValidError as e:
            return None, str(e)

        # CHECKING IF USER ALREADY EXISTS
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return None, "Email already exists"
            
        # Create new user
        user = User(name=name, email=email)
        user.set_password(password)
        
        # Save to database
        db.session.add(user)
        db.session.commit()
        
        return user, None
    
    def authenticate_user(self,email, password):
        """Authenticate a user and return tokens if valid"""
        user = User.query.filter_by(email=email).first()
        
        # IF USER DOESN'T EXIST OR PASSWORD IS WRONG, RETURN NONE
        if not user or not user.check_password(password):
            return None, "Invalid email or password"
        
        # GENERATING TOKENS
        access_token = create_access_token(identity={"id": user.id, "name": user.name, "email": user.email})
        refresh_token = create_refresh_token(identity={"id": user.id, "name": user.name, "email": user.email})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user.to_dict()
        }, None
    
    def refresh_access_token(self, user):
        """Generate a new access token from a user's data"""
        return create_access_token(identity={"id": user.id, "name": user.name, "email": user.email})