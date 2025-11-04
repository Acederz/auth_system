from functools import wraps
from flask import session, redirect, url_for, flash, request

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('请先登录', 'error')
            session['next_url'] = request.url
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

#授权书验证管理员——一期、二期
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('请先登录', 'error')
            session['next_url'] = request.url
            return redirect(url_for('auth.login'))
        
        # 检查用户是否为管理员
        if session.get('role') != 'admin' :
            flash('您没有权限访问此页面,已为您跳转至登记列表页面', 'error')
            return redirect(url_for('enroll.enroll_list'))
            
        return f(*args, **kwargs)
    return decorated_function

#项目保护系统登录——二期
def project_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('请先登录', 'error')
            session['next_url'] = request.url
            return redirect(url_for('auth.login'))
        
        # 检查用户是否为project用户
        if session.get('role') not in ['admin', 'project']:
            flash('您没有权限访问此页面', 'error')
            return redirect(url_for('auth.login'))
        
        return f(*args, **kwargs)
    return decorated_function

#授权书模板生成用户——三期
def generated_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('请先登录', 'error')
            session['next_url'] = request.url
            return redirect(url_for('auth.login'))
        
        # 检查用户是否为project用户
        if session.get('role') not in ['generate_admin', 'generated']:
            flash('您没有权限访问此页面', 'error')
            return redirect(url_for('verify.query'))
        return f(*args, **kwargs)
    return decorated_function

#授权书模板生成管理员——三期
def generate_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('请先登录', 'error')
            session['next_url'] = request.url
            return redirect(url_for('auth.login'))
        
        # 检查用户是否为project用户
        if session.get('role') not in ['generate_admin']:
            flash('您没有权限访问此页面', 'error')
            return redirect(url_for('verify.query'))
        return f(*args, **kwargs)
    return decorated_function