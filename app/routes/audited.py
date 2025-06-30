from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session, abort, jsonify
from app.models.enroll import Enroll, ModelQuantity
from app.extensions import db
from datetime import datetime
import io
import csv
from functools import wraps
from app.utils.decorators import login_required, admin_required
from sqlalchemy import func

audited_bp = Blueprint('audited', __name__)

@audited_bp.route('/admin/enrolls', methods=['GET'])
@admin_required
def enroll_list():
    """管理员查看所有登记申请列表"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # 获取搜索参数
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    bid = request.args.get('bid', '')
    
    # 构建查询
    query = Enroll.query
    
    # 应用搜索过滤
    if search:
        query = query.filter(
            (Enroll.project_name.contains(search)) |
            (Enroll.company.contains(search)) |
            (Enroll.authorized_company.contains(search)) |
            (Enroll.username.contains(search))
        )
    
    if status:
        query = query.filter(Enroll.status == status)
    
    if bid:
        query = query.filter(Enroll.bid == bid)
    
    # 按创建时间正序排序
    query = query.order_by(Enroll.created_at.asc())
    
    # 分页
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    enrolls = pagination.items
    
    return render_template('audited/enroll_list.html', enrolls=enrolls, pagination=pagination)

@audited_bp.route('/admin/enrolls/<int:enroll_id>', methods=['GET'])
@admin_required
def enroll_detail(enroll_id):
    """管理员查看登记申请详情"""
    enroll = Enroll.query.get_or_404(enroll_id)
    return render_template('audited/enroll_detail.html', enroll=enroll)

@audited_bp.route('/admin/model_stats', methods=['GET'])
@admin_required
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

@audited_bp.route('/admin/enrolls/audit', methods=['POST'])
@admin_required
def audit_enroll():
    """管理员审核登记申请"""
    data = request.get_json()
    
    # 检查必要的字段
    if not data or 'enroll_id' not in data or 'status' not in data:
        return jsonify({'success': False, 'message': '无效的请求数据，缺少 enroll_id, status 或 authorized_models'}), 400
    
    enroll_id = data.get('enroll_id')
    status = data.get('status')
    authorized_models = data.get('authorized_models') # 获取授权的模型ID列表

    print(authorized_models)
    try:
        enroll = Enroll.query.get(enroll_id)
        print(enroll.model_quantities)
        if not enroll:
            return jsonify({'success': False, 'message': '记录未找到'}), 404
        
        # 更新状态和审核意见
        enroll.status = status
        
        # 更新关联的 ModelQuantity 状态
        if hasattr(enroll, 'model_quantities') and enroll.model_quantities:
            for model_quantity in enroll.model_quantities:
                # 如果 model_quantity 的 ID 在授权列表中，则设置为"已通过"，否则设置为"未通过"
                if model_quantity.id in set(map(int, authorized_models)):
                    model_quantity.status = '已通过'
                else:
                    model_quantity.status = '未通过'
        # else:
        #     current_app.logger.info(f"Enroll ID {enroll_id} has no model_quantities to update or attribute not found.")


        db.session.commit()
        return jsonify({'success': True, 'message': '审核成功'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"审核失败: {str(e)}")
        return jsonify({'success': False, 'message': '审核失败，请稍后重试'}), 500

@audited_bp.route('/admin/enrolls/export', methods=['GET'])
@admin_required
def export_enrolls():
    """导出登记申请为CSV"""
    # 获取搜索参数
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    bid = request.args.get('bid', '')
    
    # 构建查询
    query = Enroll.query
    
    # 应用搜索过滤
    if search:
        query = query.filter(
            (Enroll.project_name.contains(search)) |
            (Enroll.company.contains(search)) |
            (Enroll.authorized_company.contains(search)) |
            (Enroll.username.contains(search))
        )
    
    if status:
        query = query.filter(Enroll.status == status)
    
    if bid:
        query = query.filter(Enroll.bid == bid)
    
    # 按创建时间正序排序
    enrolls = query.order_by(Enroll.created_at.asc()).all()
    
    # 创建CSV文件
    output = io.StringIO()
    writer = csv.writer(output)
    
    # 写入表头
    writer.writerow(['登记ID', '项目名称', '报备公司', '授权公司', '开始时间', '结束时间', 
                     '对接业务', '报表品类', '中标情况', '状态', '申请人', '审核意见'])
    
    # 写入数据
    for enroll in enrolls:
        writer.writerow([
            enroll.id,
            enroll.project_name,
            enroll.company,
            enroll.authorized_company,
            enroll.start_date,
            enroll.end_date,
            enroll.business,
            enroll.category,
            enroll.bid,
            enroll.status,
            enroll.username,
            enroll.audit_comment or ''
        ])
    
    # 设置响应头
    from flask import Response
    output.seek(0)
    return Response(
        output.getvalue().encode('utf-8-sig'),  # 使用UTF-8 with BOM以支持中文
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=enrolls.csv'}
    )

@audited_bp.route('/admin/models', methods=['GET'])
@admin_required
def model_list():
    """管理员查看所有型号列表"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # 获取搜索参数
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    
    # 构建基础查询 - 获取所有型号的统计信息
    query = db.session.query(
        ModelQuantity.model,
        func.sum(ModelQuantity.quantity).label('total_quantity'),
        func.count(ModelQuantity.id).label('usage_count'),
        func.group_concat(ModelQuantity.status).label('statuses')
    ).group_by(ModelQuantity.model)
    
    # 应用搜索过滤
    if search:
        query = query.filter(ModelQuantity.model.contains(search))
    
    if status:
        query = query.filter(ModelQuantity.status == status)
    
    # 按型号名称排序
    query = query.order_by(ModelQuantity.model)
    
    # 分页
    total_count = query.count()
    models_data = query.limit(per_page).offset((page - 1) * per_page).all()
    
    # 创建自定义分页对象
    class CustomPagination:
        def __init__(self, page, per_page, total_count):
            self.page = page
            self.per_page = per_page
            self.total = total_count
            self.pages = (total_count - 1) // per_page + 1 if total_count > 0 else 1
        
        @property
        def has_prev(self):
            return self.page > 1
        
        @property
        def has_next(self):
            return self.page < self.pages
        
        @property
        def prev_num(self):
            return self.page - 1 if self.has_prev else None
        
        @property
        def next_num(self):
            return self.page + 1 if self.has_next else None
        
        def iter_pages(self, left_edge=2, left_current=2, right_current=3, right_edge=2):
            last = 0
            for num in range(1, self.pages + 1):
                if (num <= left_edge or
                    (self.page - left_current <= num <= self.page + right_current) or
                    num > self.pages - right_edge):
                    if last + 1 != num:
                        yield None
                    yield num
                    last = num
    
    pagination = CustomPagination(page, per_page, total_count)
    
    return render_template(
        'audited/model_list.html', 
        models_data=models_data, 
        pagination=pagination,
        search=search,
        status=status
    )

@audited_bp.route('/admin/models/<string:model_name>', methods=['GET'])
@admin_required
def model_detail(model_name):
    """管理员查看型号详情"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # 查询使用该型号的所有记录
    query = db.session.query(
        Enroll, ModelQuantity
    ).join(
        ModelQuantity, 
        Enroll.id == ModelQuantity.enroll_id
    ).filter(
        ModelQuantity.model == model_name
    ).order_by(Enroll.created_at.asc())  # 按创建时间正序排序
    
    # 分页
    total_count = query.count()
    results = query.limit(per_page).offset((page - 1) * per_page).all()
    
    # 格式化结果
    model_details = []
    for enroll, model_quantity in results:
        model_details.append({
            'enroll_id': enroll.id,
            'project_name': enroll.project_name,
            'company': enroll.company,
            'authorized_company': enroll.authorized_company,
            'model': model_quantity.model,
            'quantity': model_quantity.quantity,
            'status': model_quantity.status or '未审核',
            'enroll_status': enroll.status,
            'bid_status': enroll.bid,
            'start_date': enroll.start_date.strftime('%Y-%m-%d'),
            'end_date': enroll.end_date.strftime('%Y-%m-%d'),
            'username': enroll.username,
            'created_at': enroll.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    # 创建自定义分页对象
    class CustomPagination:
        def __init__(self, page, per_page, total_count):
            self.page = page
            self.per_page = per_page
            self.total = total_count
            self.pages = (total_count - 1) // per_page + 1 if total_count > 0 else 1
        
        @property
        def has_prev(self):
            return self.page > 1
        
        @property
        def has_next(self):
            return self.page < self.pages
        
        @property
        def prev_num(self):
            return self.page - 1 if self.has_prev else None
        
        @property
        def next_num(self):
            return self.page + 1 if self.has_next else None
        
        def iter_pages(self, left_edge=2, left_current=2, right_current=3, right_edge=2):
            last = 0
            for num in range(1, self.pages + 1):
                if (num <= left_edge or
                    (self.page - left_current <= num <= self.page + right_current) or
                    num > self.pages - right_edge):
                    if last + 1 != num:
                        yield None
                    yield num
                    last = num
    
    pagination = CustomPagination(page, per_page, total_count)
    
    return render_template(
        'audited/model_detail.html',
        model_name=model_name,
        model_details=model_details,
        pagination=pagination
    )