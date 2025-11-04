from ..extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(255))  # 使用 password_hash 而不是 password
    role = db.Column(db.String(255))  # 区分用户
    entity = db.Column(db.String(255))  # 用户所属主体/公司
    
    def __init__(self, username, password=None, role=None, entity=None):
        self.username = username
        self.role = role
        self.entity = entity
        if password:
            self.set_password(password)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'