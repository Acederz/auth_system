from flask import Flask, current_app, redirect, url_for
from .extensions import db  # 导入 db 实例
from config import config
from .utils.ocr import OCRProcessor
from .routes.verify import verify_bp  # 修改为导入 verify_bp
from .routes.auth import auth
from .routes.main import main
from .routes.upload import upload

def get_ocr_processor():
    """获取OCR处理器实例"""
    if not hasattr(current_app, 'ocr_processor'):
        current_app.ocr_processor = OCRProcessor()
    return current_app.ocr_processor

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
    
    return app
