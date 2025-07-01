from app.extensions import db
from datetime import datetime

class Enroll(db.Model):
    __tablename__ = 'enroll'
    
    id = db.Column(db.Integer, primary_key=True)

    # 基本信息
    project_name = db.Column(db.String(200), nullable=False, comment='项目名')
    start_date = db.Column(db.Date, nullable=False, comment='项目开始时间')
    end_date = db.Column(db.Date, nullable=False, comment='项目结束时间')
    company = db.Column(db.String(200), nullable=False, comment='报备公司')
    authorized_company = db.Column(db.String(200), nullable=False, comment='项目承接授权公司全称')
    business = db.Column(db.String(100), nullable=False, comment='对接业务')
    category = db.Column(db.String(50), nullable=False, comment='报表品类')
    status = db.Column(db.String(50), nullable=False, comment='状态')
    bid = db.Column(db.String(50), nullable=False, comment='中标情况')
    username = db.Column(db.String(50), nullable=False, comment='用户名')
    # 创建时间
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # 关联型号数量表
    model_quantities = db.relationship('ModelQuantity', backref='enroll', lazy=True, cascade='all, delete-orphan')

class ModelQuantity(db.Model):
    __tablename__ = 'model_quantity'
    
    id = db.Column(db.Integer, primary_key=True)
    enroll_id = db.Column(db.Integer, db.ForeignKey('enroll.id'), nullable=False)
    model = db.Column(db.String(100), nullable=False, comment='型号')
    quantity = db.Column(db.Integer, nullable=False, comment='数量')
    status = db.Column(db.String(50), nullable=True, comment='状态')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
