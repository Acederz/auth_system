from flask import Blueprint, render_template, request, jsonify, redirect, url_for, send_file, session
from app.models.authorization import Authorization
from app.models.document import Document
from app.utils.decorators import login_required
from app import db
import pandas as pd
from datetime import datetime
import os
from flask import current_app
import re

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/index')
def index():
    # 修改为：如果未登录，重定向到登录页面；如果已登录，重定向到授权列表页面
    if not session.get('logged_in'):
        return redirect(url_for('auth.login'))
    return redirect(url_for('main.list'))

@main.route('/main/list')
@login_required
def list():
    # 获取查询参数
    search = request.args.get('search', '')
    channel = request.args.get('channel', '')
    status = request.args.get('status', '')
    year = request.args.get('year', '')
    # 构建查询
    query = Authorization.query
    if search:
        query = query.filter(
            db.or_(
                Authorization.auth_number.contains(search),
                Authorization.company.contains(search),
                Authorization.brand.contains(search)
            )
        )
    if channel:
        query = query.filter(Authorization.channel == channel)
    if status:
        query = query.filter(Authorization.status == status)
    if year:
        query = query.filter(Authorization.valid_period.contains(year))

    authorizations = query.order_by(Authorization.created_at.desc()).all()
    # 获取所有授权书的有效期
    yearSet = set()
    channelSet = set()
    for auth in authorizations :
         print(auth.valid_period+'  '+auth.channel)
         yearSet.update(re.findall(r'\d{4}', auth.valid_period))
         channelSet.add(auth.channel)
    years = sorted(yearSet)
    return render_template('main/list.html', authorizations=authorizations, years=years,channels = channelSet)

@main.route('/export-excel')
@login_required
def export_excel():
    authorizations = Authorization.query.all()
    
    data = []
    for auth in authorizations:
        data.append({
            '授权编号': auth.auth_number,
            '被授权人': auth.company,
            '授权品牌': auth.brand,
            '授权渠道': auth.channel,
            '授权时间范围': auth.valid_period,
            '授权状态': auth.status,
            '创建时间': auth.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    df = pd.DataFrame(data)
    filename = f'授权书列表_{datetime.now().strftime("%Y%m%d%H%M%S")}.xlsx'
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    df.to_excel(filepath, index=False)
    
    return send_file(
        filepath,
        as_attachment=True,
        download_name=filename
    )

@main.route('/main/images', methods=['POST'])
def get_auth_images():
    """获取授权书的图片列表"""
    data = request.get_json()
    authid = data.get('authid')
    print('开始获取:'+authid)
    document = Document.query.filter_by(auth_id=authid)
    # 假设图片路径存储在 images 字段中，格式为逗号分隔的字符串
    if document:
        # 确保返回完整的URL路径
        image_urls = [f'/static/uploads/{img.filename}' for img in document]
    else:
        image_urls = []
    return jsonify({'success': True, 'images': image_urls})

@main.route('/downloadauth/<auth_id>')
@login_required
def download_auth(auth_id):
    """下载授权书图片"""
    documents = Document.query.filter_by(auth_id=auth_id).all()
    if not documents:
        return jsonify({'error': '未找到相关文件'}), 404
        
    # 如果只有一个文件，直接下载
    if len(documents) == 1:
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], documents[0].filename)
        return send_file(filepath, as_attachment=True)
    
    # 如果有多个文件，创建zip文件
    import zipfile
    from io import BytesIO
    
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        for doc in documents:
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], doc.filename)
            if os.path.exists(filepath):
                zf.write(filepath, doc.filename)
    
    memory_file.seek(0)
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f'授权书_{auth_id}.zip'
    )

@main.route('/updateauth', methods=['POST'])
@login_required
def update_auth():
    data = request.get_json()
    auth_id = data.get('authId')
    auth_number = data.get('authNumber')
    company = data.get('company')
    brand = data.get('brand')
    channel = data.get('channel')
    valid_period = data.get('validPeriod')

    auth = Authorization.query.get(auth_id)
    if auth:
        auth.auth_number = auth_number
        auth.company = company
        auth.brand = brand
        auth.channel = channel
        auth.valid_period = valid_period
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'error': '未找到授权书'}), 404

@main.route('/download_template')
def download_template():
    """下载授权书模板"""
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], '授权模版.docx')
    return send_file(filepath, as_attachment=True)

@main.route('/deleteauth/<auth_id>', methods=['DELETE'])
def delete_auth(auth_id):
    """删除授权书及其相关文档"""
    try:
        # 查找授权记录
        auth = Authorization.query.get(auth_id)
        if not auth:
            return jsonify({'success': False, 'error': '未找到授权记录'}), 404
        
        # 查找相关文档
        documents = Document.query.filter_by(auth_id=auth_id).all()
        
        # 删除文件系统中的文档文件
        for doc in documents:
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], doc.filename)
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except Exception as e:
                    current_app.logger.error(f"删除文件失败: {filepath}, 错误: {str(e)}")
            
            # 从数据库中删除文档记录
            db.session.delete(doc)
        
        # 删除授权记录
        db.session.delete(auth)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"删除授权记录失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500