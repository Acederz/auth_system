from functools import wraps
from urllib.parse import urlparse
from flask import session, redirect, url_for, flash, request

def _is_login_page(url):
    """检查URL是否是登录页面，避免循环重定向"""
    parsed = urlparse(url)
    path = parsed.path.rstrip('/')
    
    login_path = url_for('auth.login', _external=False).rstrip('/')
    admin_login_path = url_for('auth.admin_login', _external=False).rstrip('/')
    
    return path == login_path or path == admin_login_path

def _normalize_path(path_or_url):
    """标准化路径，用于比较"""
    if path_or_url.startswith('http'):
        return urlparse(path_or_url).path.rstrip('/')
    return path_or_url.rstrip('/')

def _get_default_page_by_role(role):
    """根据用户角色返回默认页面"""
    if role == 'admin':
        return url_for('main.list')
    elif role == 'project':
        return url_for('enroll.enroll')
    elif role == 'generated':
        return url_for('upload_generated.list_page')
    elif role == 'generate_admin':
        return url_for('upload_generated.menu_page')
    else:
        # 默认跳转到验证查询页面（通常不需要登录）
        return url_for('verify.query')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            # 避免循环重定向：如果当前请求就是登录页面，直接返回
            if _is_login_page(request.url):
                return f(*args, **kwargs)
            
            flash('请先登录', 'error')
            # 只有在不是登录页面时才设置next_url
            if not _is_login_page(request.url):
                session['next_url'] = request.url
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

#授权书验证管理员——一期、二期
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            # 避免循环重定向
            if _is_login_page(request.url):
                return f(*args, **kwargs)
            
            flash('请先登录', 'error')
            if not _is_login_page(request.url):
                session['next_url'] = request.url
            return redirect(url_for('auth.login'))
        
        # 检查用户是否为管理员
        if session.get('role') != 'admin':
            # 已登录但权限不足，根据用户角色跳转到有权限的页面
            role = session.get('role')
            default_page = _get_default_page_by_role(role)
            
            # 避免循环：如果目标页面就是当前页面，跳转到默认页面
            current_path = _normalize_path(request.url)
            target_path = _normalize_path(default_page)
            
            if current_path == target_path:
                flash('您没有权限访问此页面', 'error')
                return redirect(url_for('verify.query'))
            
            flash('您没有权限访问此页面,已为您跳转至相应页面', 'error')
            return redirect(default_page)
            
        return f(*args, **kwargs)
    return decorated_function

#项目保护系统登录——二期
def project_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            # 避免循环重定向
            if _is_login_page(request.url):
                return f(*args, **kwargs)
            
            flash('请先登录', 'error')
            if not _is_login_page(request.url):
                session['next_url'] = request.url
            return redirect(url_for('auth.login'))
        
        # 检查用户是否为project用户
        if session.get('role') not in ['admin', 'project']:
            # 已登录但权限不足，根据用户角色跳转
            role = session.get('role')
            default_page = _get_default_page_by_role(role)
            
            # 避免循环
            current_path = _normalize_path(request.url)
            target_path = _normalize_path(default_page)
            
            if current_path == target_path:
                flash('您没有权限访问此页面', 'error')
                return redirect(url_for('verify.query'))
            
            flash('您没有权限访问此页面', 'error')
            return redirect(default_page)
        
        return f(*args, **kwargs)
    return decorated_function

#授权书模板生成用户——三期
def generated_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            # 避免循环重定向
            if _is_login_page(request.url):
                return f(*args, **kwargs)
            
            flash('请先登录', 'error')
            if not _is_login_page(request.url):
                session['next_url'] = request.url
            return redirect(url_for('auth.login'))
        
        # 检查用户是否为generated用户
        if session.get('role') not in ['generate_admin', 'generated']:
            # 已登录但权限不足，根据用户角色跳转
            role = session.get('role')
            default_page = _get_default_page_by_role(role)
            
            # 避免循环
            current_path = _normalize_path(request.url)
            target_path = _normalize_path(default_page)
            
            if current_path == target_path:
                flash('您没有权限访问此页面', 'error')
                return redirect(url_for('verify.query'))
            
            flash('您没有权限访问此页面', 'error')
            return redirect(default_page)
        
        return f(*args, **kwargs)
    return decorated_function

#授权书模板生成管理员——三期
def generate_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            # 避免循环重定向
            if _is_login_page(request.url):
                return f(*args, **kwargs)
            
            flash('请先登录', 'error')
            if not _is_login_page(request.url):
                session['next_url'] = request.url
            return redirect(url_for('auth.login'))
        
        # 检查用户是否为generate_admin
        if session.get('role') not in ['generate_admin']:
            # 已登录但权限不足，根据用户角色跳转
            role = session.get('role')
            default_page = _get_default_page_by_role(role)
            
            # 避免循环
            current_path = _normalize_path(request.url)
            target_path = _normalize_path(default_page)
            
            if current_path == target_path:
                flash('您没有权限访问此页面', 'error')
                return redirect(url_for('verify.query'))
            
            flash('您没有权限访问此页面', 'error')
            return redirect(default_page)
        
        return f(*args, **kwargs)
    return decorated_function