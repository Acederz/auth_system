import os
from werkzeug.utils import secure_filename
from datetime import datetime

def generate_unique_filename(filename):
    """生成唯一的文件名"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    secure_name = secure_filename(filename)
    name, ext = os.path.splitext(secure_name)
    return f"{name}_{timestamp}{ext}"

def get_file_size_display(size_in_bytes):
    """将文件大小转换为人类可读格式"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.1f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.1f} TB"

def allowed_file(filename, allowed_extensions):
    """检查文件类型是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def create_directory_if_not_exists(directory):
    """创建目录（如果不存在）"""
    if not os.path.exists(directory):
        os.makedirs(directory)
