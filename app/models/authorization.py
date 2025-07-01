from ..extensions import db
from datetime import datetime

class Authorization(db.Model):
    __tablename__ = 'authorization'  # 保持原有表名
    
    id = db.Column(db.Integer, primary_key=True)
    auth_number = db.Column(db.String(20), unique=True, nullable=False)
    company = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(100))
    channel = db.Column(db.String(50))
    valid_period = db.Column(db.String(100))
    status = db.Column(db.String(20))
    system_key = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # 关联文档
    documents = db.relationship('Document', backref='authorization', lazy=True)

    @property
    def is_valid(self):
        """检查授权是否有效"""
        try:
            if not self.valid_period:
                return False
            start_date_str, end_date_str = self.valid_period.split(' to ')
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            today = datetime.now().date()
            return start_date <= today <= end_date
        except Exception:
            return False

    @property
    def valid_start(self):
        """获取授权开始时间"""
        if self.valid_period:
            start_date_str = self.valid_period.split(' to ')[0]
            return datetime.strptime(start_date_str, '%Y-%m-%d').date()
        return None

    @property
    def valid_end(self):
        """获取授权结束时间"""
        if self.valid_period:
            end_date_str = self.valid_period.split(' to ')[1]
            return datetime.strptime(end_date_str, '%Y-%m-%d').date()
        return None

    @staticmethod
    def verify_authorization(auth_number, system_key):
        """验证授权信息"""
        auth = Authorization.query.filter_by(
            auth_number=auth_number,
            system_key=system_key
        ).first()
        
        if not auth:
            return None
            
        # if query_date:
        #     try:
        #         query_date = datetime.strptime(query_date, '%Y-%m-%d').date()
        #         # 解析 valid_period 字段
        #         start_date_str, end_date_str = auth.valid_period.split(' to ')
        #         start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        #         end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                
        #         if not (start_date <= query_date <= end_date):
        #             return None
        #     except Exception as e:
        #         print(f"日期验证错误: {str(e)}")
        #         return None
                
        return auth

    def to_dict(self):
        """将授权信息转换为字典"""
        return {
            'id': self.id,
            'auth_number': self.auth_number,
            'company': self.company,
            'brand': self.brand,
            'channel': self.channel,
            'valid_period': self.valid_period,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'is_valid': self.is_valid,
            'document': self.documents[0].filename if self.documents else None
        }

    def __repr__(self):
        return f'<Authorization {self.auth_number}>'
