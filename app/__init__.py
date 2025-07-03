from flask import Flask, current_app, redirect, url_for
from .extensions import db  # 导入 db 实例
from config import config
# 注释掉OCR相关导入
# from .utils.ocr import OCRProcessor
from .routes.verify import verify_bp  # 修改为导入 verify_bp
from .routes.auth import auth
from .routes.main import main
from .routes.upload import upload
from .routes.enroll import enroll_bp
from .routes.audited import audited_bp
from .models.user import User

# 注释掉OCR处理器获取函数
# def get_ocr_processor():
#     """获取OCR处理器实例"""
#     if not hasattr(current_app, 'ocr_processor'):
#         current_app.ocr_processor = OCRProcessor()
#     return current_app.ocr_processor

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # 配置加载
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    
    # 修改根路由 - 直接重定向到验证查询页面
    @app.route('/')
    def index():
        return redirect(url_for('verify.query'))  # 假设查询页面的路由名为 verify.query
    
    # 注册蓝图
    app.register_blueprint(verify_bp)
    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(upload)
    app.register_blueprint(enroll_bp)
    app.register_blueprint(audited_bp)

    # 创建数据库表
    with app.app_context():
        db.create_all()
        # 创建默认管理员账户（如果不存在）
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', password='admin123')
            db.session.add(admin)
            db.session.commit()
    
    return app
