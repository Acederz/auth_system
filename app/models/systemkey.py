from ..extensions import db
from datetime import datetime

class SystemKey(db.Model):
    __tablename__ = 'systemkey'
    
    id = db.Column(db.Integer, primary_key=True)
    auth_number = db.Column(db.String(20), unique=True, nullable=False)
    system_key = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def get_system_key(auth_number):
        """
        根据授权号查询system_key
        
        Args:
            auth_number (str): 授权号
            
        Returns:
            str: 如果找到记录则返回system_key，否则返回None
        """
        record = SystemKey.query.filter_by(auth_number=auth_number).first()
        return record.system_key if record else None

    def to_dict(self):
        """将记录转换为字典格式"""
        return {
            'id': self.id,
            'auth_number': self.auth_number,
            'system_key': self.system_key,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    def __repr__(self):
        return f'<SystemKey {self.auth_number}>' 