from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from app.utils.decorators import login_required, admin_required
from functools import wraps
from app.models.user import User  # 导入用户模型
from werkzeug.security import check_password_hash, generate_password_hash  # 用于密码验证
from app.extensions import db

auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    # 从会话中获取next_url，而不是URL参数
    next_url = session.get('next_url')
    
    # 如果用户已登录，直接重定向到授权列表页面或next_url
    if session.get('logged_in'):
        if next_url:
            # 使用后清除会话中的next_url
            session.pop('next_url', None)
            return redirect(next_url)
        return redirect(url_for('main.list'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # 添加日志输出，便于调试
        current_app.logger.info(f"Login attempt for user: {username}")
        
        if not username or not password:
            flash('请输入用户名和密码', 'error')
            return render_template('auth/login.html')
        
        # 从数据库查询用户
        user = User.query.filter_by(username=username).first()
        
        # 验证用户和密码
        if user and check_password_hash(user.password_hash, password):
            session['logged_in'] = True
            session['username'] = username
            session['user_id'] = user.id  # 存储用户ID，便于后续操作
            current_app.logger.info(f"User {username} logged in successfully")
            
            # 如果有next_url，则重定向到原始请求页面
            if next_url:
                # 使用后清除会话中的next_url
                session.pop('next_url', None)
                
                # 检查权限
                if username == 'admin':
                    # 管理员有所有权限
                    return redirect(next_url)
                else:
                    # 非管理员，检查是否访问的是管理员页面
                    if 'users' in next_url:  # 简单判断是否为用户管理相关页面
                        flash('您没有权限访问该页面', 'error')
                        return redirect(url_for('enroll.enroll'))
                    return redirect(next_url)
            else:
                # 没有next_url，使用默认重定向
                if username == 'admin':
                    return redirect(url_for('main.list'))
                else:
                    return redirect(url_for('enroll.enroll'))
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

@auth.route('/users')
@admin_required
def user_list():
    users = User.query.all()
    return render_template('auth/user_list.html', users=users)

@auth.route('/users/add', methods=['GET', 'POST'])
@admin_required
def add_user():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not username or not password:
            flash('请输入用户名和密码', 'error')
            return render_template('auth/add_user.html')
            
        if password != confirm_password:
            flash('两次输入的密码不一致', 'error')
            return render_template('auth/add_user.html')
            
        # 检查用户名是否已存在
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('用户名已存在', 'error')
            return render_template('auth/add_user.html')
            
        # 创建新用户
        new_user = User(username=username)
        new_user.set_password(password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('用户添加成功', 'success')
            return redirect(url_for('auth.user_list'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error adding user: {str(e)}")
            flash('添加用户失败', 'error')
            
    return render_template('auth/add_user.html')

@auth.route('/users/change_password', methods=['GET', 'POST'])
@admin_required
def change_password():
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # 获取当前登录用户
        user = User.query.filter_by(username=session.get('username')).first()
        
        if not user:
            flash('用户不存在', 'error')
            return redirect(url_for('auth.logout'))
            
        # 验证旧密码
        if not user.verify_password(old_password):
            flash('原密码不正确', 'error')
            return render_template('auth/change_password.html')
            
        # 验证新密码
        if new_password != confirm_password:
            flash('两次输入的新密码不一致', 'error')
            return render_template('auth/change_password.html')
            
        # 更新密码
        user.set_password(new_password)
        
        try:
            db.session.commit()
            flash('密码修改成功', 'success')
            return redirect(url_for('main.list'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error changing password: {str(e)}")
            flash('密码修改失败', 'error')
            
    return render_template('auth/change_password.html')
