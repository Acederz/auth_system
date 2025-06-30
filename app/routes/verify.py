from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.authorization import Authorization
from app.models.document import Document
from flask import send_from_directory, current_app
import os
from sqlalchemy.exc import SQLAlchemyError

verify_bp = Blueprint('verify', __name__)

@verify_bp.route('/verify', methods=['GET', 'POST'])
def query():
    """查询界面和处理查询请求"""
    if request.method == 'POST':
        try:
            # 打印接收到的表单数据，用于调试
            print("接收到的表单数据:", request.form)
            
            auth_number = request.form.get('auth_number')
            system_key = request.form.get('system_key')  # 确保与前端表单中的name属性匹配
            
            # 打印每个字段的值，用于调试
            print(f"auth_number: {auth_number}")
            print(f"system_key: {system_key}")
            
            if not all([auth_number, system_key]):
                flash('请填写完整信息')
                return redirect(url_for('verify.query'))
            
            # 添加空值校验
            if not auth_number.strip() or not system_key.strip():
                flash('授权编码和系统密钥不能为空')
                return redirect(url_for('verify.query'))
            
            # 修改验证逻辑为安全查询
            auth = Authorization.verify_authorization(auth_number, system_key)
            if not auth:  # 添加状态检查
                flash('授权信息无效或已过期')
                return redirect(url_for('verify.query'))
            
            #查询授权文件
            if auth:
                print("授权信息:", auth.to_dict())
                document = Document.query.filter_by(auth_id=auth.id).order_by(Document.uploaded_at.desc()).first()
                if auth.documents:
                    print("文档信息:", {
                        "数量": len(auth.documents),
                        "第一个文档": {
                            "filename": auth.documents[0].filename if auth.documents else None,
                            "file_path": auth.documents[0].file_path if auth.documents else None
                        }
                    })
                return render_template('verify/result.html', auth=auth,document=document)
        except SQLAlchemyError as e:
            current_app.logger.error(f"数据库查询失败: {str(e)}")
            flash('系统繁忙，请稍后重试')
            return redirect(url_for('verify.query'))
        except Exception as e:
            current_app.logger.exception("验证过程发生意外错误")
            flash('系统发生未知错误')
            return redirect(url_for('verify.query')) 
        
    return render_template('verify/query.html') 

@verify_bp.route('/result/<int:id>')
def result(id):
    document = Document.query.get_or_404(id)
    return render_template('verify/result.html', 
                         document=document,
                         image_url=url_for('static', filename=f'uploads/{document.filename}')) 

@verify_bp.route('/file/<filename>')
def get_file(filename):
    if os.path.exists(current_app.config['VIEW_FOLDER']):
        print('存在')
    print(current_app.config['VIEW_FOLDER']+ filename)
    return send_from_directory(current_app.config['VIEW_FOLDER'], filename)