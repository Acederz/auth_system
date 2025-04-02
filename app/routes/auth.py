from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from app.utils.decorators import login_required
from functools import wraps

auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    # 如果用户已登录，直接重定向到授权列表页面
    if session.get('logged_in'):
        return redirect(url_for('main.list'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # 添加日志输出，便于调试
        current_app.logger.info(f"Login attempt for user: {username}")
        
        if not username or not password:
            flash('请输入用户名和密码', 'error')
            return render_template('auth/login.html')
        
        # 简单的硬编码验证，实际项目中应该使用更安全的方式
        if username == 'admin' and password == 'admin123':
            session['logged_in'] = True
            session['username'] = username
            current_app.logger.info(f"User {username} logged in successfully")
            return redirect(url_for('main.list'))
        else:
            flash('用户名或密码错误', 'error')
            current_app.logger.warning(f"Failed login attempt for user: {username}")
    
    return render_template('auth/login.html')

@auth.route('/logout')
@login_required
def logout():
    session.clear()
    flash('您已成功退出登录', 'info')
    return redirect(url_for('auth.login'))
