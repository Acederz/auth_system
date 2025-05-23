import os
from app import create_app, db  # 确保从 app/__init__.py 导入
from flask_migrate import upgrade
from config import Config  # 导入配置类

os.environ['FLAGS_use_avx'] = '0'
os.environ['FLAGS_use_mkldnn'] = '0' 
os.environ['OMP_NUM_THREADS'] = '1'

# 创建应用实例
app = create_app()  # 使用 create_app 函数创建应用，而不是直接实例化 Flask

# 添加上传文件夹配置
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app/static/uploads')
# 添加密钥配置（用于flash消息等功能）
app.config['SECRET_KEY'] = 'dev_secret_key_123'  
app.config['VIEW_FOLDER'] = 'uploads'

@app.shell_context_processor
def make_shell_context():
    """为 Flask shell 添加数据库实例和模型"""
    from app.models.authorization import Authorization
    from app.models.document import Document
    from app.models.systemkey import SystemKey
    return dict(db=db, Authorization=Authorization, Document=Document, SystemKey=SystemKey)

@app.cli.command()
def deploy():
    """部署命令"""
    # 运行数据库迁移
    upgrade()

@app.cli.command()
def test():
    """运行单元测试"""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

if __name__ == '__main__':
    try:
        # 确保上传文件夹存在
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        
        # 在应用上下文中创建所有数据库表和初始化 OCR
        with app.app_context():
            db.create_all()
            from app import get_ocr_processor
            from paddleocr import PaddleOCR
            print("正在初始化 OCR 模型，首次运行可能需要下载模型文件...")
            PaddleOCR(use_angle_cls=False, lang='ch', show_log=False,enable_mkldnn=False,rec_image_shape='3,32,320',det_limit_side_len=480  )  # 这一步会自动下载所需模型
            get_ocr_processor()
            print("数据库表创建成功")
        
        # 运行应用
        print("启动应用服务器...")
        app.run(host='0.0.0.0', port=5001, debug=True)
    except Exception as e:
        print(f"应用启动错误: {str(e)}")
        raise
