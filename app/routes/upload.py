import cv2
from flask import Blueprint, request, jsonify, current_app, render_template
from werkzeug.utils import secure_filename
from app.models.authorization import Authorization
from app.models.document import Document
from app.models.systemkey import SystemKey
from app.utils.decorators import login_required,admin_required
from app import db
import os
import secrets
import time
from app.utils.ocrDeal import orcScan

upload = Blueprint('upload', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@upload.route('/generate-key', methods=['POST'])
@admin_required
def generate_key():
    data = request.get_json()
    auth_number = data.get('auth_number')
    
    if not auth_number:
        return jsonify({'success': False, 'error': 'Missing auth number'})
    
    # 检查授权编号是否已存在
    if Authorization.query.filter_by(auth_number=auth_number).first():
        return jsonify({'success': False, 'error': 'Auth number already exists'})
    
    system_key = SystemKey.get_system_key(auth_number)
    print(system_key)
    if system_key is None:
        #system_key = secrets.token_hex(8)
        chars = 'abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'
        system_key = ''.join(secrets.choice(chars) for _ in range(6))
        systemKey = SystemKey(
            auth_number = auth_number,
            system_key = system_key
        )
        print('systemKey：'+systemKey.auth_number+';'+systemKey.system_key)
        db.session.add(systemKey)
        db.session.commit()
    return jsonify({'success': True, 'systemKey': system_key})

@upload.route('/upload', methods=['POST'])
@admin_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'})
    
    if file and allowed_file(file.filename):
        file_base, file_ext = os.path.splitext(file.filename)
        timestamp = int(time.time() * 1000)
        filename = f"{timestamp}{file_ext.lower()}"
        #filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        # 如果是tif文件,转换为jpg
        if filename.lower().endswith('.tif'):
            file.save(filepath)
            # 读取tif文件并转换为jpg
            img = cv2.imread(filepath)
            jpg_filepath = filepath.rsplit('.', 1)[0] + '.jpg'
            cv2.imwrite(jpg_filepath, img)
            # 更新filepath为jpg文件路径
            filepath = jpg_filepath
        else:
            file.save(filepath)
        # TODO: 添加OCR处理逻辑
        if not filename.lower().endswith('.pdf') :
            ocrResults = orcScan(filepath)
        else:
            ocrResults = []
        filename = filename.replace('tif','jpg')
        return jsonify({
            'success': True,
            'filename': filename,
            'filepath': filepath,
            'ocrResults' : ocrResults
        })
    
    return jsonify({'success': False, 'error': 'File type not allowed'})

@upload.route('/submit-auth', methods=['POST'])
@admin_required
def submit_auth():
    data = request.get_json()
    
    try:
        auth = Authorization(
            auth_number=data['authNumber'],
            system_key=data['systemKey'],
            company=data['company'],
            channel=data['channel'],
            valid_period=data['validPeriod'],
            brand=data['brand'],
            status='生效中'
        )
        db.session.add(auth)
        db.session.flush()  # 获取auth.id
        
        # 保存文件记录
        for file_info in data['files']:
            doc = Document(
                auth_id=auth.id,
                filename=file_info['filename'],
                file_path=file_info['filepath'],
                file_type=file_info['filename'].rsplit('.', 1)[1].lower(),
                file_size=os.path.getsize(file_info['filepath'])
            )
            db.session.add(doc)
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@upload.route('/upload-page')
@admin_required
def upload_page():
    """显示上传页面"""
    return render_template('main/upload.html')
