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

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('请先登录', 'error')
            session['next_url'] = request.url
            return redirect(url_for('auth.login'))
        
        # 检查用户是否为管理员
        if session.get('username') != 'admin':
            flash('您没有权限访问此页面', 'error')
            return redirect(url_for('verify.query'))
            
        return f(*args, **kwargs)
    return decorated_function