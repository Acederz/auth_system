from ..extensions import db
from datetime import datetime


class Generated(db.Model):
    __tablename__ = 'generated'

    id = db.Column(db.Integer, primary_key=True)

    # 上传Excel的完整字段
    template_used = db.Column(db.String(100), comment='使用模板')
    store_type = db.Column(db.String(100), comment='店铺类型')
    authorized_entity = db.Column(db.String(200), comment='授权主体')
    platform = db.Column(db.String(100), comment='授权平台')
    brand = db.Column(db.String(200), comment='授权品牌')
    trademark_no = db.Column(db.String(200), comment='品牌商标号')
    store_name = db.Column(db.String(200), comment='店铺名称')
    store_id = db.Column(db.String(200), comment='店铺ID')
    subsidiary = db.Column(db.String(200), comment='所属分公司')
    period = db.Column(db.String(200), comment='授权期间 原样存储，例如 2025-01-01 至 2026-12-31')
    auth_number = db.Column(db.String(100), comment='授权字号')
    stamping_entity = db.Column(db.String(200), comment='授权方（盖章）主体')
    stamping_date = db.Column(db.String(50), comment='用印时间')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'template_used': self.template_used,
            'store_type': self.store_type,
            'authorized_entity': self.authorized_entity,
            'platform': self.platform,
            'brand': self.brand,
            'trademark_no': self.trademark_no,
            'store_name': self.store_name,
            'store_id': self.store_id,
            'subsidiary': self.subsidiary,
            'period': self.period,
            'auth_number': self.auth_number,
            'stamping_entity': self.stamping_entity,
            'stamping_date': self.stamping_date,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }


