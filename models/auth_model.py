from flask_sqlalchemy import SQLAlchemy
import bcrypt

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    #SPECIAL METHOD TO REPRESENT THE OBJECT AS A STRING
    def __repr__(self):
        return f'<User {self.email}>'
    
    #METHOD TO CONVERT THE OBJECT TO A DICTIONARY
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email
        }
    def set_password(self, password):
        """Hash password before storing it"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Verify password against stored hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))