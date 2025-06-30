from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session, abort, jsonify
from app.models.enroll import Enroll, ModelQuantity
from app.extensions import db
from datetime import datetime
from app.utils.decorators import login_required, admin_required

enroll_bp = Blueprint('enroll', __name__)

@enroll_bp.route('/enroll/form', methods=['GET', 'POST'])
@login_required
def enroll():
    if request.method == 'POST':
        try:
            # 获取表单数据
            project_name = request.form.get('project_name')
            start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
            end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
            company = request.form.get('company')
            authorized_company = request.form.get('authorized_company')
            business = request.form.get('business')
            category = request.form.get('category')
            bid = request.form.get('bid_status')
            username = session.get('username')
            # 创建主表记录
            new_enroll = Enroll(
                project_name=project_name,
                start_date=start_date,
                end_date=end_date,
                company=company,
                authorized_company=authorized_company,
                business=business,
                category=category,
                status='待审核',
                bid = bid,
                username = username
            )
            
            db.session.add(new_enroll)
            db.session.flush()  # 获取new_enroll的id
            
            # 处理型号和数量
            models = request.form.getlist('model[]')
            quantities = request.form.getlist('quantity[]')
            
            for model, quantity in zip(models, quantities):
                model_quantity = ModelQuantity(
                    enroll_id=new_enroll.id,
                    model=model,
                    quantity=int(quantity)
                )
                db.session.add(model_quantity)
            
            db.session.commit()
            flash('登记成功！', 'success')
            return redirect(url_for('enroll.success', enroll_id=new_enroll.id))
            
        except Exception as e:
            current_app.logger.error(f"登记失败: {str(e)}")
            flash('系统错误，请稍后重试', 'error')
            db.session.rollback()
            
    return render_template('enroll/enroll.html')

@enroll_bp.route('/success/<int:enroll_id>')
@login_required
def success(enroll_id):
    """登记成功页面"""
    enroll = Enroll.query.get_or_404(enroll_id)
    return render_template('enroll/success.html', enroll=enroll)

@enroll_bp.route('/enroll/list', methods=['GET'])
@login_required
def enroll_list():
    """用户查看自己的登记列表"""
    page = request.args.get('page', 1, type=int) # 获取当前页码，默认为1
    per_page = 10 # 每页显示的条数，可以根据需要调整
    # 查询当前用户的登记记录并进行分页
    pagination = Enroll.query.filter_by(username=session.get('username')).paginate(
        page=page,
        per_page=per_page,
        error_out=False # 当页码超出范围时不报错，返回空列表
    )
     # 获取当前页的数据
    user_enrolls = pagination.items

    return render_template('enroll/list.html', enrolls=user_enrolls, pagination=pagination) # 传递分页对象给模板


@enroll_bp.route('/enroll/detail/<int:enroll_id>', methods=['GET']) # 新增详情路由
@login_required
def enroll_detail(enroll_id):
    """用户查看自己的登记详情"""
    enroll = Enroll.query.get_or_404(enroll_id) # 根据ID获取登记记录，未找到则返回404

    # 验证当前用户是否有权限查看此记录
    if enroll.username != session.get('username'):
        abort(403) # 如果不是当前用户的记录，返回403 Forbidden

    return render_template('enroll/detail.html', enroll=enroll) # 渲染新的详情模板

@enroll_bp.route('/enroll/model_stats', methods=['GET'])
@login_required
def get_model_stats():
    """获取型号的使用统计"""
    model = request.args.get('model', '')
    current_enroll_id = request.args.get('enroll_id', type=int)
    
    if not model:
        return jsonify({'success': False, 'message': '缺少model参数'}), 400
    
    try:
        # 查询相同型号的记录数，排除当前详情页的enrollid
        query = ModelQuantity.query.filter_by(model=model)
        
        # 如果提供了enroll_id，排除该记录
        if current_enroll_id:
            query = query.filter(ModelQuantity.enroll_id != current_enroll_id)
            
        total_count = query.count()
        
        # 查询相同型号且状态为已通过的记录数，同样排除当前详情页
        approved_query = ModelQuantity.query.filter_by(model=model, status='已通过')
        
        if current_enroll_id:
            approved_query = approved_query.filter(ModelQuantity.enroll_id != current_enroll_id)
            
        approved_count = approved_query.count()
        
        # 查询是否存在已通过的记录
        has_approved = approved_count > 0
        
        return jsonify({
            'success': True,
            'total_count': total_count,
            'approved_count': approved_count,
            'has_approved': has_approved
        })
    except Exception as e:
        current_app.logger.error(f"获取型号统计失败: {str(e)}")
        return jsonify({'success': False, 'message': '获取统计信息失败'}), 500

@enroll_bp.route('/enroll/update_bid_status/<int:enroll_id>', methods=['POST']) # 新增用于更新中标情况的路由
@login_required # 确保用户已登录
def update_bid_status(enroll_id):
    """更新登记记录的中标情况"""
    enroll = Enroll.query.get(enroll_id) # 根据ID获取登记记录

    # 检查记录是否存在且属于当前用户
    if not enroll:
        return jsonify({'success': False, 'message': '记录未找到'}), 404
    if enroll.username != session.get('username'): # 假设Enroll模型有user_id字段关联用户
        return jsonify({'success': False, 'message': '无权操作'}), 403

    # 从请求体中获取新的中标情况值 (假设前端发送的是JSON)
    data = request.get_json()
    if not data or 'bid_status' not in data:
        return jsonify({'success': False, 'message': '无效的请求数据'}), 400

    new_bid_status = data['bid_status']

    # 验证新的中标情况值是否有效 (可选但推荐)
    valid_statuses = ['已中标', '未中标', '未开始']
    if new_bid_status not in valid_statuses:
         return jsonify({'success': False, 'message': '无效的中标情况值'}), 400

    try:
        # 更新中标情况字段
        enroll.bid = new_bid_status # 假设模型字段是bid
        db.session.commit() # 提交数据库更改
        flash('中标情况更新成功', 'success')
        return jsonify({'success': True, 'message': '中标情况更新成功'}) # 返回成功响应
    except Exception as e:
        db.session.rollback() # 发生错误时回滚
        current_app.logger.error(f"更新中标情况失败 (Enroll ID: {enroll_id}): {str(e)}")
        return jsonify({'success': False, 'message': '更新失败，请稍后重试'}), 500 # 返回失败响应

@enroll_bp.route('/enroll/search_auth', methods=['GET'])
@login_required
def search_auth():
    """根据平台和商品查询是否已有授权登记"""
    search_project = request.args.get('search_project', '')
    search_model = request.args.get('search_model', '')
    
    # 如果两个参数都为空，返回空结果
    if not search_project and not search_model:
        return jsonify({
            'success': False,
            'message': '请至少输入一个查询条件'
        }), 400
    
    try:
        # 构建查询
        query = db.session.query(Enroll, ModelQuantity).join(
            ModelQuantity, 
            Enroll.id == ModelQuantity.enroll_id
        )
        
        # 根据输入条件过滤
        if search_project:
            query = query.filter(Enroll.project_name.like(f'%{search_project}%'))
        
        if search_model:
            query = query.filter(ModelQuantity.model.like(f'%{search_model}%'))
        
        # 执行查询
        results = query.all()
        
        # 格式化结果
        formatted_results = []
        for enroll, model_quantity in results:
            formatted_results.append({
                'enroll_id': enroll.id,
                'project_name': enroll.project_name,
                'model': model_quantity.model,
                'quantity': model_quantity.quantity,
                'status': enroll.status,
                'bid_status': enroll.bid,
                'start_date': enroll.start_date.strftime('%Y-%m-%d'),
                'end_date': enroll.end_date.strftime('%Y-%m-%d')
            })
        
        return jsonify({
            'success': True,
            'count': len(formatted_results),
            'results': formatted_results
        })
        
    except Exception as e:
        current_app.logger.error(f"查询授权信息失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '查询失败，请稍后重试'
        }), 500