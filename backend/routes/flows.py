from flask import Blueprint, request, jsonify
from config.database import get_db_connection
import pymysql
import uuid
import os
from datetime import datetime, timedelta
import logging

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

flows_bp = Blueprint('flows', __name__)

@flows_bp.route('/api/flows', methods=['GET'])
def get_flows():
    """获取流程列表"""
    try:
        # 获取查询参数
        tab = request.args.get('tab', 'todo')
        user_id = request.args.get('user_id')
        status = request.args.get('status')
        
        # 如果没有提供user_id，可能是工作流配置页面加载，返回流程架构列表
        if not user_id:
            conn = get_db_connection()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            
            # 构建查询语句
            query = '''
                SELECT fa.*, 
                       (SELECT COUNT(*) FROM flow_architecture_steps WHERE architecture_id = fa.id) as step_count
                FROM flow_architectures fa
            '''
            
            # 如果提供了status参数，添加状态过滤
            if status:
                query += ' WHERE fa.status = %s'
                params = (status,)
            else:
                params = ()
            
            query += ' ORDER BY fa.updated_at DESC'
            
            # 执行查询
            cursor.execute(query, params)
            architectures = cursor.fetchall()
            
            # 格式化时间
            for arch in architectures:
                if arch['created_at']:
                    arch['created_at'] = arch['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                if arch['updated_at']:
                    arch['updated_at'] = arch['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
            
            return jsonify({'success': True, 'data': architectures}), 200
        
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        if tab == 'todo':
            # 获取待办流程
            cursor.execute('''
                SELECT f.*, ft.type_name, u.name as initiator_name 
                FROM flows f 
                LEFT JOIN flow_types ft ON f.type_id = ft.type_id 
                LEFT JOIN users u ON f.initiator_id = u.id 
                WHERE f.status = 'pending' 
                AND f.current_node IN (SELECT step_name FROM flow_steps WHERE approver_id = %s AND status = 'pending')
            ''', (user_id,))
        elif tab == 'initiated':
            # 获取我发起的流程
            cursor.execute('''
                SELECT f.*, ft.type_name, u.name as initiator_name 
                FROM flows f 
                LEFT JOIN flow_types ft ON f.type_id = ft.type_id 
                LEFT JOIN users u ON f.initiator_id = u.id 
                WHERE f.initiator_id = %s
            ''', (user_id,))
        elif tab == 'completed':
            # 获取已完结的流程
            cursor.execute('''
                SELECT f.*, ft.type_name, u.name as initiator_name 
                FROM flows f 
                LEFT JOIN flow_types ft ON f.type_id = ft.type_id 
                LEFT JOIN users u ON f.initiator_id = u.id 
                WHERE f.status = 'completed'
            ''')
        else:
            return jsonify({'error': '无效的标签'}), 400
        
        flows = cursor.fetchall()
        
        # 格式化时间
        for flow in flows:
            if flow['created_at']:
                flow['created_at'] = flow['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            if flow['updated_at']:
                flow['updated_at'] = flow['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
            if flow['completed_at']:
                flow['completed_at'] = flow['completed_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify(flows), 200
    except Exception as e:
        print(f'获取流程列表错误: {e}')
        return jsonify({'error': '获取流程列表失败'}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@flows_bp.route('/api/flows/<flow_id>/steps', methods=['GET'])
def get_flow_steps(flow_id):
    """获取流程步骤"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 获取流程ID
        cursor.execute('SELECT id FROM flows WHERE flow_id = %s', (flow_id,))
        flow = cursor.fetchone()
        if not flow:
            return jsonify({'error': '流程不存在'}), 404
        
        # 获取流程步骤
        cursor.execute('''
            SELECT fs.*, u.name as approver_name 
            FROM flow_steps fs 
            LEFT JOIN users u ON fs.approver_id = u.id 
            WHERE fs.flow_id = %s 
            ORDER BY fs.order_index ASC
        ''', (flow['id'],))
        
        steps = cursor.fetchall()
        
        # 格式化时间
        for step in steps:
            if step['created_at']:
                step['created_at'] = step['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            if step['updated_at']:
                step['updated_at'] = step['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify(steps), 200
    except Exception as e:
        print(f'获取流程步骤错误: {e}')
        return jsonify({'error': '获取流程步骤失败'}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@flows_bp.route('/api/flows/<flow_id>/detail', methods=['GET'])
def get_flow_detail(flow_id):
    """获取流程详细信息"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 获取流程基本信息
        cursor.execute('''
            SELECT f.*, ft.type_name, u.name as initiator_name 
            FROM flows f 
            LEFT JOIN flow_types ft ON f.type_id = ft.type_id 
            LEFT JOIN users u ON f.initiator_id = u.id 
            WHERE f.flow_id = %s
        ''', (flow_id,))
        flow = cursor.fetchone()
        if not flow:
            return jsonify({'error': '流程不存在'}), 404
        
        # 格式化时间
        if flow['created_at']:
            flow['created_at'] = flow['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        if flow['updated_at']:
            flow['updated_at'] = flow['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
        if flow['completed_at']:
            flow['completed_at'] = flow['completed_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        # 获取流程步骤
        cursor.execute('''
            SELECT fs.*, u.name as approver_name 
            FROM flow_steps fs 
            LEFT JOIN users u ON fs.approver_id = u.id 
            WHERE fs.flow_id = %s 
            ORDER BY fs.order_index ASC
        ''', (flow['id'],))
        steps = cursor.fetchall()
        
        # 格式化时间
        for step in steps:
            if step['created_at']:
                step['created_at'] = step['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            if step['updated_at']:
                step['updated_at'] = step['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        # 获取流程字段数据
        cursor.execute('''
            SELECT field_name, field_value
            FROM flow_field_data
            WHERE flow_id = %s
        ''', (flow['id'],))
        field_data = {}
        fields = cursor.fetchall()
        for field in fields:
            field_data[field['field_name']] = field['field_value']
        
        return jsonify({
            'flow': flow,
            'steps': steps,
            'fields': field_data
        }), 200
    except Exception as e:
        print(f'获取流程详细信息错误: {e}')
        return jsonify({'error': '获取流程详细信息失败'}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@flows_bp.route('/api/flows', methods=['POST'])
def create_flow():
    """创建流程或流程架构配置"""
    try:
        # 获取请求数据（JSON 或 FormData）
        data = request.get_json()
        if data is None:
            data = request.form.to_dict()
        
        # 确保 data 是字典类型
        if not isinstance(data, dict):
            data = {}
            
        # 处理文件上传
        files = request.files or {}
        
        # 检查是否是流程架构配置
        if 'flow_type' in data and 'steps' in data:
            # 流程架构配置
            flow_type = data.get('flow_type')
            flow_name = data.get('flow_name')
            description = data.get('description', '')
            steps = data.get('steps') or []
            fields = data.get('fields') or []
            
            if not flow_type or not flow_name or not steps:
                return jsonify({'error': '缺少必要参数'}), 400
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 生成流程架构ID
            architecture_id = f"ARCH-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
            
            # 总是创建新架构，不更新现有架构
            cursor.execute('''
                INSERT INTO flow_architectures (architecture_id, flow_type, flow_name, description, status, created_at, updated_at) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (architecture_id, flow_type, flow_name, description, 'disabled', datetime.now(), datetime.now()))
            architecture_id_db = cursor.lastrowid
            
            # 插入流程架构步骤
            step_ids = []
            for step in steps:
                step_name = step.get('name')
                approver_id = step.get('approver_id')
                step_order = step.get('step_order')
                
                if not all([step_name, approver_id, step_order]):
                    continue
                
                # 插入步骤
                cursor.execute('''
                    INSERT INTO flow_architecture_steps (architecture_id, step_name, approver_id, step_order) 
                    VALUES (%s, %s, %s, %s)
                ''', (architecture_id_db, step_name, approver_id, step_order))
                step_ids.append(cursor.lastrowid)
            
            # 插入流程字段
            for i, field in enumerate(fields):
                field_name = field.get('name')
                field_type = field.get('type')
                is_required = field.get('is_required', False)
                options = field.get('options') or []
                
                if field_name and field_type:
                    # 将字段关联到第一个步骤
                    if step_ids:
                        step_id = step_ids[0]
                        cursor.execute('''
                            INSERT INTO flow_fields (step_id, field_name, field_type) 
                            VALUES (%s, %s, %s)
                        ''', (step_id, field_name, field_type))
                        
                        # 如果有选项，保存选项数据
                        if options:
                            field_id = cursor.lastrowid
                            for option in options:
                                cursor.execute('''
                                    INSERT INTO flow_field_options (field_id, option_value) 
                                    VALUES (%s, %s)
                                ''', (field_id, option))
            
            conn.commit()
            return jsonify({'success': True, 'message': '流程架构配置保存成功'}), 201
        else:
            # 常规流程创建
            flow_id = data.get('flow_id')
            employee_name = data.get('employee_name')
            initiator_id = data.get('initiator_id')
            priority = data.get('priority', 'normal')
            
            if not all([flow_id, employee_name, initiator_id]):
                return jsonify({'error': '缺少必要参数'}), 400
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 生成流程ID
            new_flow_id = f"FLOW-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
            
            # 从流程架构获取步骤
            cursor.execute('SELECT id, flow_type FROM flow_architectures WHERE id = %s', (flow_id,))
            architecture = cursor.fetchone()
            
            if not architecture:
                return jsonify({'error': '流程架构不存在'}), 404
            
            # 获取流程类型ID
            flow_type = architecture[1]
            # 映射流程类型名称到type_id
            type_id_map = {
                '入职流程': 'onboarding',
                '离职流程': 'offboarding',
                '绩效方案': 'performance'
            }
            type_id = type_id_map.get(flow_type, 'onboarding')  # 默认使用onboarding
            
            # 从架构获取步骤
            cursor.execute('''
                SELECT step_name, approver_id, step_order 
                FROM flow_architecture_steps 
                WHERE architecture_id = %s 
                ORDER BY step_order ASC
            ''', (architecture[0],))
            architecture_steps = cursor.fetchall()
            
            if not architecture_steps:
                return jsonify({'error': '流程架构未配置步骤'}), 400
            
            current_node = architecture_steps[0][0]
            steps = [(step[0], step[2], step[1]) for step in architecture_steps]
            
            # 插入流程
            cursor.execute('''
                INSERT INTO flows (flow_id, type_id, employee_name, initiator_id, status, priority, current_node, progress) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (new_flow_id, type_id, employee_name, initiator_id, 'pending', priority, current_node, 0))
            
            flow_id_db = cursor.lastrowid
            
            # 插入流程步骤
            for step in steps:
                if len(step) == 3:
                    step_name, order_index, approver_id = step
                else:
                    step_name, order_index = step
                    approver_id = 1  # 管理员
                
                cursor.execute('''
                    INSERT INTO flow_steps (flow_id, step_name, approver_id, status, order_index) 
                    VALUES (%s, %s, %s, %s, %s)
                ''', (flow_id_db, step_name, approver_id, 'pending', order_index))
            
            # 保存流程字段数据
            # 创建上传目录
            upload_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads')
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            # 处理文本字段
            for key, value in (data or {}).items():
                if key.startswith('field_'):
                    field_name = key.replace('field_', '')
                    # 尝试获取字段的实际名称
                    try:
                        field_id = int(field_name)
                        # 根据字段ID获取字段名称和类型
                        cursor.execute('SELECT field_name, field_type FROM flow_fields WHERE id = %s', (field_id,))
                        field = cursor.fetchone()
                        if field:
                            field_name = field[0]
                            field_type = field[1]
                            
                            # 如果是薪资方案字段，将ID转换为名称
                            if field_type == '薪资方案' and value:
                                try:
                                    cursor.execute('SELECT plan_name FROM salary_plans WHERE id = %s', (value,))
                                    plan = cursor.fetchone()
                                    if plan:
                                        value = plan[0]
                                except:
                                    pass
                            # 如果是劳务合同签署字段，将ID转换为名称
                            elif field_type == '劳务合同签署' and value:
                                try:
                                    cursor.execute('SELECT name FROM contracts WHERE id = %s', (value,))
                                    contract = cursor.fetchone()
                                    if contract:
                                        value = contract[0]
                                except:
                                    pass
                            
                            cursor.execute('''
                                INSERT INTO flow_field_data (flow_id, field_name, field_value) 
                                VALUES (%s, %s, %s)
                            ''', (flow_id_db, field_name, value))
                    except:
                        # 如果不是数字ID，直接使用字段名
                        cursor.execute('''
                            INSERT INTO flow_field_data (flow_id, field_name, field_value) 
                            VALUES (%s, %s, %s)
                        ''', (flow_id_db, field_name, value))
            
            # 处理文件上传
            try:
                for key, file in (files or {}).items():
                    if key.startswith('field_') and file.filename:
                        field_name = key.replace('field_', '')
                        # 尝试获取字段的实际名称
                        try:
                            field_id = int(field_name)
                            # 根据字段ID获取字段名称
                            cursor.execute('SELECT field_name FROM flow_fields WHERE id = %s', (field_id,))
                            field = cursor.fetchone()
                            if field:
                                field_name = field[0]
                                # 生成唯一的文件名
                                ext = os.path.splitext(file.filename)[1]
                                filename = f"{uuid.uuid4()}{ext}"
                                # 保存文件
                                file_path = os.path.join(upload_dir, filename)
                                file.save(file_path)
                                # 保存文件路径到数据库
                                cursor.execute('''
                                    INSERT INTO flow_field_data (flow_id, field_name, field_value) 
                                    VALUES (%s, %s, %s)
                                ''', (flow_id_db, field_name, filename))
                        except Exception as e:
                            print(f'处理文件上传错误: {e}')
            except Exception as e:
                print(f'文件上传处理错误: {e}')
            
            # 为审批人创建通知
            for step in steps:
                if len(step) == 3:
                    step_name, order_index, approver_id = step
                    # 获取审批人姓名
                    cursor.execute('SELECT name FROM users WHERE id = %s', (approver_id,))
                    approver = cursor.fetchone()
                    approver_name = approver[0] if approver else '未知用户'
                    
                    # 获取发起人姓名
                    cursor.execute('SELECT name FROM users WHERE id = %s', (initiator_id,))
                    initiator = cursor.fetchone()
                    initiator_name = initiator[0] if initiator else '未知用户'
                    
                    # 创建通知
                    message = f'{initiator_name} 发起了 {flow_type} 流程，需要您审批'
                    cursor.execute('''
                        INSERT INTO notifications (user_id, type, message, related_id, is_read)
                        VALUES (%s, %s, %s, %s, %s)
                    ''', (approver_id, 'flow_approval', message, new_flow_id, 0))
            
            conn.commit()
            
            return jsonify({'flow_id': new_flow_id, 'message': '流程创建成功'}), 201
    except Exception as e:
        import traceback
        print(f'创建流程错误: {e}')
        print(f'错误堆栈:\n{traceback.format_exc()}')
        if 'conn' in locals():
            conn.rollback()
        return jsonify({'success': False, 'message': f'创建流程失败: {str(e)}'}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@flows_bp.route('/api/flows/architecture/<int:architecture_id>', methods=['GET'])
def get_flow_architecture(architecture_id):
    """获取流程架构详情"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 获取流程架构信息
        cursor.execute('SELECT * FROM flow_architectures WHERE id = %s', (architecture_id,))
        architecture = cursor.fetchone()
        
        if not architecture:
            return jsonify({'error': '流程架构不存在'}), 404
        
        # 格式化时间
        if architecture['created_at']:
            architecture['created_at'] = architecture['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        if architecture['updated_at']:
            architecture['updated_at'] = architecture['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        # 获取流程步骤
        cursor.execute('''
            SELECT fas.*, u.name as approver_name 
            FROM flow_architecture_steps fas 
            LEFT JOIN users u ON fas.approver_id = u.id 
            WHERE fas.architecture_id = %s 
            ORDER BY fas.step_order ASC
        ''', (architecture_id,))
        steps = cursor.fetchall()
        
        # 获取流程字段
        fields = []
        if steps:
            step_ids = [step['id'] for step in steps]
            placeholders = ','.join(['%s'] * len(step_ids))
            cursor.execute(f'SELECT * FROM flow_fields WHERE step_id IN ({placeholders})', step_ids)
            fields = cursor.fetchall()
            
            # 获取每个字段的选项
            for field in fields:
                cursor.execute('SELECT option_value FROM flow_field_options WHERE field_id = %s', (field['id'],))
                options = [row['option_value'] for row in cursor.fetchall()]
                field['options'] = options
        
        architecture['fields'] = fields
        architecture['steps'] = steps
        
        return jsonify({'success': True, 'architecture': architecture}), 200
    except Exception as e:
        print(f'获取流程架构详情错误: {e}')
        return jsonify({'error': '获取流程架构详情失败'}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@flows_bp.route('/api/flows/<flow_id>/approve', methods=['POST'])
def approve_flow(flow_id):
    """审批流程"""
    try:
        data = request.get_json()
        approver_id = data.get('approver_id')
        action = data.get('action')  # 'approve' 或 'reject'
        comment = data.get('comment', '')
        
        if not all([approver_id, action]):
            return jsonify({'error': '缺少必要参数'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取流程ID
        cursor.execute('SELECT id, status, current_node, type_id FROM flows WHERE flow_id = %s', (flow_id,))
        flow = cursor.fetchone()
        if not flow:
            return jsonify({'error': '流程不存在'}), 404
        
        if flow[1] != 'pending':
            return jsonify({'error': '流程已结束'}), 400
        
        # 获取当前待审批步骤
        cursor.execute('''
            SELECT id, step_name, order_index 
            FROM flow_steps 
            WHERE flow_id = %s AND status = 'pending' 
            ORDER BY order_index ASC 
            LIMIT 1
        ''', (flow[0],))
        current_step = cursor.fetchone()
        if not current_step:
            return jsonify({'error': '没有待审批的步骤'}), 400
        
        # 验证审批人
        cursor.execute('''
            SELECT * FROM flow_steps 
            WHERE id = %s AND approver_id = %s
        ''', (current_step[0], approver_id))
        if not cursor.fetchone():
            return jsonify({'error': '无权限审批此流程'}), 403
        
        # 更新步骤状态
        if action == 'approve':
            step_status = 'completed'
            # 检查是否所有步骤都已完成
            cursor.execute('''
                SELECT COUNT(*) FROM flow_steps 
                WHERE flow_id = %s AND status = 'pending'
            ''', (flow[0],))
            pending_steps = cursor.fetchone()[0]
            
            if pending_steps == 1:
                # 所有步骤都已完成
                flow_status = 'completed'
                completed_at = datetime.now()
                progress = 100
                current_node = '流程完成'
            else:
                # 还有后续步骤
                flow_status = 'pending'
                completed_at = None
                # 计算进度
                cursor.execute('''
                    SELECT COUNT(*) FROM flow_steps 
                    WHERE flow_id = %s
                ''', (flow[0],))
                total_steps = cursor.fetchone()[0]
                progress = int((current_step[2] / total_steps) * 100)
                # 获取下一步骤
                cursor.execute('''
                    SELECT step_name FROM flow_steps 
                    WHERE flow_id = %s AND order_index = %s
                ''', (flow[0], current_step[2] + 1))
                next_step = cursor.fetchone()
                current_node = next_step[0] if next_step else '流程完成'
        else:  # reject
            step_status = 'rejected'
            flow_status = 'rejected'
            completed_at = datetime.now()
            progress = 0
            current_node = '流程被拒绝'
        
        # 开始事务
        try:
            # 更新步骤状态
            cursor.execute('''
                UPDATE flow_steps 
                SET status = %s, comment = %s 
                WHERE id = %s
            ''', (step_status, comment, current_step[0]))
            
            # 更新流程状态
            cursor.execute('''
                UPDATE flows 
                SET status = %s, current_node = %s, progress = %s, completed_at = %s 
                WHERE id = %s
            ''', (flow_status, current_node, progress, completed_at, flow[0]))
            
            # 记录审批记录
            cursor.execute('''
                INSERT INTO approval_records (flow_id, step_id, approver_id, action, comment) 
                VALUES (%s, %s, %s, %s, %s)
            ''', (flow[0], current_step[0], approver_id, action, comment))
            
            # 如果流程审批通过，处理相应的业务逻辑
            if action == 'approve' and flow_status == 'completed':
                # 获取流程类型
                cursor.execute('SELECT type_id FROM flows WHERE id = %s', (flow[0],))
                flow_type = cursor.fetchone()
                
                if flow_type:
                    # 获取流程字段数据
                    cursor.execute('''
                        SELECT field_name, field_value
                        FROM flow_field_data
                        WHERE flow_id = %s
                    ''', (flow[0],))
                    field_data = {}
                    fields = cursor.fetchall()
                    for field in fields:
                        field_data[field[0]] = field[1]
                    
                    if flow_type[0] == 'onboarding':
                        # 入职流程处理
                        # 获取骑手风神ID
                        rider_id = field_data.get('骑手风神ID', field_data.get('风神ID', f"R{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"))
                        
                        # 处理工作性质 - 多重判断策略
                        work_nature = '全职'
                        
                        # 策略1: 检查表单字段数据中是否有工作性质字段
                        fn_candidates = ['工作性质', '用工类型', 'employment_type', 'work_nature']
                        for fn_key in fn_candidates:
                            fn_val = field_data.get(fn_key, '')
                            if fn_val and '兼职' in str(fn_val):
                                work_nature = '兼职'
                                print(f'[入职-DEBUG] 通过字段[{fn_key}]={fn_val}判定为兼职')
                                break
                        
                        # 策略2: 如果策略1未判定为兼职，通过type_id查找flow_type名称
                        if work_nature == '全职':
                            cursor.execute('SELECT name FROM flow_types WHERE id = %s', (flow[3],))
                            ft_result = cursor.fetchone()
                            if ft_result and ft_result[0] and '兼职' in str(ft_result[0]):
                                work_nature = '兼职'
                                print(f'[入职-DEBUG] 通过flow_type名称[{ft_result[0]}]判定为兼职')
                        
                        # 策略3: 如果仍未判定，通过flow_architecture名称判断（改进版）
                        if work_nature == '全职':
                            cursor.execute('''
                                SELECT fa.flow_name 
                                FROM flow_architectures fa
                                JOIN flow_types ft ON fa.flow_type = ft.name
                                WHERE ft.id = %s
                            ''', (flow[3],))
                            arch_result = cursor.fetchone()
                            if arch_result and arch_result[0] and '兼职' in str(arch_result[0]):
                                work_nature = '兼职'
                                print(f'[入职-DEBUG] 通过flow_architecture名称[{arch_result[0]}]判定为兼职')
                        
                        # 策略4: 最后兜底，检查薪资方案是否包含"兼职"
                        if work_nature == '全职':
                            salary_plan = field_data.get('薪资方案', field_data.get('薪资方案绑定', ''))
                            if salary_plan and '兼职' in str(salary_plan):
                                work_nature = '兼职'
                                print(f'[入职-DEBUG] 通过薪资方案[{salary_plan}]判定为兼职')
                        
                        print(f'[入职-DEBUG] 最终work_nature={work_nature}, flow_id={flow[0]}, field_data_keys={list(field_data.keys())}')
                        
                        # 从身份证号提取出生日期
                        def extract_birth_date_from_id_card(id_card):
                            if not id_card:
                                return None
                            id_card = str(id_card).strip()
                            if len(id_card) < 15:
                                return None
                            
                            try:
                                if len(id_card) == 18:
                                    # 18位身份证：第7-14位为出生日期，格式YYYYMMDD
                                    birth_date_str = id_card[6:14]
                                elif len(id_card) == 15:
                                    # 15位身份证：第7-12位为出生日期，格式YYMMDD，需要转换为YYYYMMDD
                                    birth_date_str = '19' + id_card[6:12]
                                else:
                                    return None
                                
                                # 转换为YYYY-MM-DD格式
                                if len(birth_date_str) == 8:
                                    year = birth_date_str[:4]
                                    month = birth_date_str[4:6]
                                    day = birth_date_str[6:8]
                                    return f'{year}-{month}-{day}'
                                return None
                            except:
                                return None
                        
                        # 检查是否有合同签署记录
                        contract_status = '未签订'
                        cursor.execute('''
                            SELECT id FROM contract_signatures 
                            WHERE flow_id = %s 
                            AND status = 'signed'
                        ''', (flow[0],))
                        if cursor.fetchone():
                            contract_status = '已签订'
                        
                        # 字段映射
                        rider_data = {
                            'rider_id': rider_id,
                            'name': field_data.get('姓名', 'none'),
                            'phone': field_data.get('手机号', 'none'),
                            'station_name': field_data.get('站点名称', 'none'),
                            'first_run_date': field_data.get('首跑日期', None),
                            'entry_date': field_data.get('入职日期', None),
                            'work_nature': work_nature,
                            'unit_price': field_data.get('单价', None),
                            'settlement_cycle': field_data.get('结算周期', 'none'),
                            'id_card': field_data.get('身份证号', 'none'),
                            'birth_date': field_data.get('出生日期', None),
                            'recruitment_channel': field_data.get('招聘渠道', 'none'),
                            'referral_name': field_data.get('三方/内推姓名', 'none'),
                            'salary_plan_id': field_data.get('薪资方案', field_data.get('薪资方案绑定', 'none')),
                            'emergency_phone': field_data.get('紧急联系人电话号码', 'none'),
                            'position_status': '在职',
                            'tags': field_data.get('人员标签', 'none'),
                            'remark': field_data.get('备注', 'none'),
                            'contract_status': contract_status
                        }
                        
                        # 如果没有出生日期，尝试从身份证号提取
                        if not rider_data['birth_date']:
                            extracted_birth_date = extract_birth_date_from_id_card(rider_data['id_card'])
                            if extracted_birth_date:
                                rider_data['birth_date'] = extracted_birth_date
                        
                        # 插入骑手数据
                        cursor.execute('''
                            INSERT INTO riders (
                                rider_id, name, phone, station_name, first_run_date, entry_date, 
                                work_nature, unit_price, settlement_cycle, id_card, birth_date, 
                                recruitment_channel, referral_name, salary_plan_id, emergency_phone, 
                                position_status, tags, remark, contract_status
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ''', (
                            rider_data['rider_id'],
                            rider_data['name'],
                            rider_data['phone'],
                            rider_data['station_name'],
                            rider_data['first_run_date'],
                            rider_data['entry_date'],
                            rider_data['work_nature'],
                            rider_data['unit_price'],
                            rider_data['settlement_cycle'],
                            rider_data['id_card'],
                            rider_data['birth_date'],
                            rider_data['recruitment_channel'],
                            rider_data['referral_name'],
                            rider_data['salary_plan_id'],
                            rider_data['emergency_phone'],
                            rider_data['position_status'],
                            rider_data['tags'],
                            rider_data['remark'],
                            rider_data['contract_status']
                        ))
                    elif flow_type[0] == 'offboarding':
                        # 离职流程处理
                        # 获取骑手风神ID
                        rider_id = field_data.get('骑手风神ID', field_data.get('风神ID', None))
                        if rider_id:
                            # 获取离职日期和离岗日期
                            exit_date = field_data.get('离职日期', None)
                            leave_date = field_data.get('离岗日期', None)
                            
                            # 如果没有提供离职日期，使用当前日期作为默认值
                            if not exit_date:
                                exit_date = datetime.now().strftime('%Y-%m-%d')
                            
                            # 如果没有提供离岗日期，使用离职日期+1天作为默认值
                            if not leave_date and exit_date:
                                try:
                                    leave_date_obj = datetime.strptime(exit_date, '%Y-%m-%d') + timedelta(days=1)
                                    leave_date = leave_date_obj.strftime('%Y-%m-%d')
                                except:
                                    leave_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
                            
                            # 判定岗位状态
                            position_status = '离职'
                            # 计算离职时间和离岗时间的间隔
                            days_diff = 0
                            if exit_date and leave_date:
                                try:
                                    exit_date_obj = datetime.strptime(exit_date, '%Y-%m-%d')
                                    leave_date_obj = datetime.strptime(leave_date, '%Y-%m-%d')
                                    # 待离职判定：离岗日期大于离职日期
                                    if leave_date_obj > exit_date_obj:
                                        position_status = '待离职'
                                    # 计算间隔天数，用于判定自离/正常离职
                                    days_diff = (leave_date_obj - exit_date_obj).days
                                except:
                                    pass
                            
                            # 判定自离/正常离职，添加到人员标签
                            tags = field_data.get('人员标签', '')
                            # 处理none值
                            if tags == 'none':
                                tags = ''
                            if days_diff >= 30:
                                if '正常离职' not in tags:
                                    tags = tags + '正常离职' if tags else '正常离职'
                            else:
                                if '自离' not in tags:
                                    tags = tags + '自离' if tags else '自离'
                            
                            # 获取离职原因
                            exit_reason = field_data.get('离职原因', '无')
                            
                            # 更新骑手数据
                            cursor.execute('''
                                UPDATE riders 
                                SET exit_date = %s, leave_date = %s, position_status = %s, tags = %s, remark = %s
                                WHERE rider_id = %s
                            ''', (exit_date, leave_date, position_status, tags, exit_reason, rider_id))
                            
                            # 插入离职记录
                            cursor.execute('''
                                INSERT INTO rider_exit_records (rider_id, name, exit_date, exit_reason, station_name, status) 
                                VALUES (%s, %s, %s, %s, %s, %s)
                            ''', (rider_id, field_data.get('姓名', '未知'), exit_date, field_data.get('离职原因', '无'), field_data.get('站点名称', '未知'), 'completed'))
            
            conn.commit()
            return jsonify({'message': '审批成功'}), 200
        except Exception as e:
            conn.rollback()
            raise e
    except Exception as e:
        print(f'审批流程错误: {e}')
        return jsonify({'error': '审批流程失败'}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@flows_bp.route('/api/flows/<flow_id>/cancel', methods=['POST'])
def cancel_flow(flow_id):
    """撤销流程"""
    try:
        data = request.get_json()
        initiator_id = data.get('initiator_id')
        
        if not initiator_id:
            return jsonify({'error': '缺少必要参数'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取流程ID
        cursor.execute('SELECT id, status, initiator_id FROM flows WHERE flow_id = %s', (flow_id,))
        flow = cursor.fetchone()
        if not flow:
            return jsonify({'error': '流程不存在'}), 404
        
        if flow[1] != 'pending':
            return jsonify({'error': '流程已结束，无法撤销'}), 400
        
        if flow[2] != int(initiator_id):
            return jsonify({'error': '只有发起人可以撤销流程'}), 403
        
        # 开始事务
        try:
            # 更新流程状态为已撤销
            cursor.execute('''
                UPDATE flows 
                SET status = 'cancelled', current_node = '流程已撤销', progress = 0, completed_at = %s 
                WHERE id = %s
            ''', (datetime.now(), flow[0]))
            
            # 更新所有步骤状态为已撤销
            cursor.execute('''
                UPDATE flow_steps 
                SET status = 'cancelled' 
                WHERE flow_id = %s
            ''', (flow[0],))
            
            conn.commit()
            return jsonify({'message': '流程撤销成功'}), 200
        except Exception as e:
            conn.rollback()
            raise e
    except Exception as e:
        print(f'撤销流程错误: {e}')
        return jsonify({'error': '撤销流程失败'}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
# 修改add_comment函数，确保@提及的通知正确关联到被@的用户
@flows_bp.route('/api/flows/<flow_id>/comment', methods=['POST'])
def add_comment(flow_id):
    """添加评论"""
    conn = None
    cursor = None
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        comment = data.get('comment')
        
        if not all([user_id, comment]):
            return jsonify({'error': '缺少必要参数'}), 400
        
        # 确保user_id是整数
        try:
            user_id = int(user_id)
        except ValueError:
            return jsonify({'error': '无效的用户ID'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取流程ID
        cursor.execute('SELECT id FROM flows WHERE flow_id = %s', (flow_id,))
        flow = cursor.fetchone()
        if not flow:
            return jsonify({'error': '流程不存在'}), 404
        
        # 插入评论
        cursor.execute('''
            INSERT INTO flow_comments (flow_id, user_id, comment, created_at) 
            VALUES (%s, %s, %s, %s)
        ''', (flow[0], user_id, comment, datetime.now()))
        
        # 检测评论中的@提及
        mentions = []
        # 简单的字符串搜索方法
        if '@' in comment:
            # 分割字符串，找到所有@开头的部分
            parts = comment.split('@')
            for part in parts[1:]:  # 跳过第一个部分，因为它不包含@
                # 获取@后面的内容，直到遇到空格或结束
                mention = part.split()[0] if part.split() else ''
                if mention:
                    mentions.append(mention)
        
        logger.debug(f'检测到@提及: {mentions}')
        logger.debug(f'评论内容: {comment}')
        logger.debug(f'用户ID: {user_id}')
        
        # 获取评论者姓名
        cursor.execute('SELECT name FROM users WHERE id = %s', (user_id,))
        commenter = cursor.fetchone()
        commenter_name = commenter[0] if commenter else '未知用户'
        
        logger.debug(f'评论者姓名: {commenter_name}')
        
        # 获取流程信息
        cursor.execute('SELECT flow_id, type_id FROM flows WHERE id = %s', (flow[0],))
        flow_info = cursor.fetchone()
        flow_id_str = flow_info[0] if flow_info else flow_id
        
        logger.debug(f'流程ID: {flow_id_str}')
        
        # 为每个被@的用户创建通知
        if mentions:
            # 获取所有用户，用于模糊匹配
            cursor.execute('SELECT id, name FROM users WHERE id != %s', (user_id,))
            all_users = cursor.fetchall()
            
            logger.debug(f'所有用户: {all_users}')
            
            for mention_name in mentions:
                logger.debug(f'被@的用户: {mention_name}')
                
                # 遍历所有用户，进行模糊匹配
                for user in all_users:
                    user_id_db = user[0]
                    user_name_db = user[1]
                    
                    logger.debug(f'检查用户: {user_name_db} (ID: {user_id_db})')
                    
                    # 检查用户名是否包含@提及的内容
                    if mention_name in user_name_db:
                        logger.debug(f'匹配到用户: {user_name_db} (ID: {user_id_db})')
                        # 创建通知
                        message = f'{commenter_name} 在流程评论中@了您'
                        logger.debug(f'创建通知: {message}')
                        cursor.execute('''
                            INSERT INTO notifications (user_id, type, message, related_id, is_read)
                            VALUES (%s, %s, %s, %s, %s)
                        ''', (user_id_db, 'mention', message, flow_id_str, 0))
                        logger.debug('通知创建成功')
        
        # 为所有用户创建通知（测试用）
        cursor.execute('SELECT id FROM users WHERE id != %s', (user_id,))
        all_users = cursor.fetchall()
        
        for user in all_users:
            user_id_to_notify = user[0]
            # 创建通知
            message = f'{commenter_name} 在流程评论中@了您'
            logger.debug(f'创建通知给用户 {user_id_to_notify}: {message}')
            cursor.execute('''
                INSERT INTO notifications (user_id, type, message, related_id, is_read)
                VALUES (%s, %s, %s, %s, %s)
            ''', (user_id_to_notify, 'mention', message, flow_id_str, 0))
            logger.debug('通知创建成功')
        
        conn.commit()
        return jsonify({'message': '评论成功'}), 200
    except Exception as e:
        print(f'添加评论错误: {e}')
        if conn:
            conn.rollback()
        return jsonify({'error': '添加评论失败'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@flows_bp.route('/api/flows/<flow_id>/comments', methods=['GET'])
def get_comments(flow_id):
    """获取评论列表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 获取流程ID
        cursor.execute('SELECT id FROM flows WHERE flow_id = %s', (flow_id,))
        flow = cursor.fetchone()
        if not flow:
            return jsonify({'error': '流程不存在'}), 404
        
        # 获取评论列表
        cursor.execute('''
            SELECT fc.*, u.name as user_name 
            FROM flow_comments fc 
            LEFT JOIN users u ON fc.user_id = u.id 
            WHERE fc.flow_id = %s 
            ORDER BY fc.created_at DESC
        ''', (flow['id'],))
        comments = cursor.fetchall()
        
        # 格式化时间
        for comment in comments:
            if comment['created_at']:
                comment['created_at'] = comment['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({'comments': comments}), 200
    except Exception as e:
        print(f'获取评论列表错误: {e}')
        return jsonify({'error': '获取评论列表失败'}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@flows_bp.route('/api/users', methods=['GET'])
def get_users():
    """获取用户列表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 获取查询参数
        query = request.args.get('query')
        
        if query:
            # 模糊查询用户
            cursor.execute('SELECT id, name FROM users WHERE name LIKE %s', (f'%{query}%',))
        else:
            # 获取所有用户
            cursor.execute('SELECT id, name FROM users')
        
        users = cursor.fetchall()
        
        return jsonify({'success': True, 'users': users}), 200
    except Exception as e:
        print(f'获取用户列表错误: {e}')
        return jsonify({'error': '获取用户列表失败'}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@flows_bp.route('/api/notifications', methods=['GET'])
def get_notifications():
    """获取用户通知列表"""
    conn = None
    cursor = None
    try:
        # 获取用户ID
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': '缺少用户ID'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 检查notifications表是否存在
        cursor.execute("SHOW TABLES LIKE 'notifications'")
        table_exists = cursor.fetchone()
        if not table_exists:
            print('通知表不存在')
            return jsonify({'notifications': [], 'unread_count': 0}), 200
        
        # 获取通知列表
        cursor.execute('''
            SELECT * FROM notifications 
            WHERE user_id = %s 
            ORDER BY created_at DESC
        ''', (user_id,))
        notifications = cursor.fetchall()
        
        # 格式化时间
        for notification in notifications:
            if notification['created_at']:
                notification['created_at'] = notification['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        # 获取未读通知数量
        cursor.execute('SELECT COUNT(*) as unread_count FROM notifications WHERE user_id = %s AND is_read = 0', (user_id,))
        result = cursor.fetchone()
        unread_count = result['unread_count'] if result else 0
        
        return jsonify({'notifications': notifications, 'unread_count': unread_count}), 200
    except Exception as e:
        print(f'获取通知列表错误: {type(e).__name__}: {str(e)}')
        import traceback
        traceback.print_exc()
        return jsonify({'error': '获取通知列表失败'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@flows_bp.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
def mark_notification_read(notification_id):
    """标记通知为已读"""
    try:
        # 获取用户ID
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': '缺少用户ID'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 标记通知为已读
        cursor.execute('''
            UPDATE notifications 
            SET is_read = 1 
            WHERE id = %s AND user_id = %s
        ''', (notification_id, user_id))
        
        conn.commit()
        return jsonify({'message': '通知已标记为已读'}), 200
    except Exception as e:
        print(f'标记通知已读错误: {e}')
        return jsonify({'error': '标记通知已读失败'}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@flows_bp.route('/api/test-mention', methods=['POST'])
def test_mention():
    """测试@提及功能"""
    try:
        data = request.get_json()
        comment = data.get('comment')
        
        if not comment:
            return jsonify({'error': '缺少评论内容'}), 400
        
        # 检测评论中的@提及
        mentions = []
        words = comment.split()
        for word in words:
            if word.startswith('@'):
                mentions.append(word[1:])
        
        print(f'检测到@提及: {mentions}')
        print(f'评论内容: {comment}')
        
        # 查找用户
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        found_users = []
        for mention_name in mentions:
            # 去除空格
            mention_name = mention_name.strip()
            print(f'查找用户: {mention_name}')
            cursor.execute('SELECT id, name FROM users WHERE name = %s', (mention_name,))
            user = cursor.fetchone()
            if user:
                found_users.append(user)
                print(f'找到用户: {user}')
            else:
                print(f'未找到用户: {mention_name}')
        
        conn.close()
        
        return jsonify({'mentions': mentions, 'found_users': found_users}), 200
    except Exception as e:
        print(f'测试@提及错误: {e}')
        return jsonify({'error': '测试@提及失败'}), 500

@flows_bp.route('/api/flows/architecture/<int:architecture_id>', methods=['DELETE'])
def delete_flow_architecture(architecture_id):
    """删除流程架构"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取与该架构相关的步骤ID
        cursor.execute('SELECT id FROM flow_architecture_steps WHERE architecture_id = %s', (architecture_id,))
        step_ids = [row[0] for row in cursor.fetchall()]
        
        # 删除流程字段选项
        if step_ids:
            # 先获取所有字段ID
            placeholders = ','.join(['%s'] * len(step_ids))
            cursor.execute(f'SELECT id FROM flow_fields WHERE step_id IN ({placeholders})', step_ids)
            field_ids = [row[0] for row in cursor.fetchall()]
            
            # 删除字段选项
            if field_ids:
                field_placeholders = ','.join(['%s'] * len(field_ids))
                cursor.execute(f'DELETE FROM flow_field_options WHERE field_id IN ({field_placeholders})', field_ids)
        
        # 删除流程字段
        if step_ids:
            placeholders = ','.join(['%s'] * len(step_ids))
            cursor.execute(f'DELETE FROM flow_fields WHERE step_id IN ({placeholders})', step_ids)
        
        # 删除流程架构步骤
        cursor.execute('DELETE FROM flow_architecture_steps WHERE architecture_id = %s', (architecture_id,))
        
        # 删除流程架构
        cursor.execute('DELETE FROM flow_architectures WHERE id = %s', (architecture_id,))
        
        conn.commit()
        return jsonify({'success': True, 'message': '流程架构删除成功'}), 200
    except Exception as e:
        print(f'删除流程架构错误: {e}')
        if 'conn' in locals():
            conn.rollback()
        return jsonify({'success': False, 'message': '删除流程架构失败'}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@flows_bp.route('/api/flows/architecture/<int:architecture_id>', methods=['PUT'])
def update_flow_architecture(architecture_id):
    """更新流程架构"""
    try:
        data = request.get_json()
        flow_type = data.get('flow_type')
        flow_name = data.get('flow_name')
        description = data.get('description', '')
        steps = data.get('steps')
        fields = data.get('fields', [])
        
        if not flow_type or not flow_name or not steps:
            return jsonify({'error': '缺少必要参数'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 更新流程架构基本信息
        cursor.execute('''
            UPDATE flow_architectures 
            SET flow_type = %s, flow_name = %s, description = %s, updated_at = %s 
            WHERE id = %s
        ''', (flow_type, flow_name, description, datetime.now(), architecture_id))
        
        # 获取与该架构相关的步骤ID
        cursor.execute('SELECT id FROM flow_architecture_steps WHERE architecture_id = %s', (architecture_id,))
        step_ids = [row[0] for row in cursor.fetchall()]
        
        # 删除流程字段选项
        if step_ids:
            # 先获取所有字段ID
            placeholders = ','.join(['%s'] * len(step_ids))
            cursor.execute(f'SELECT id FROM flow_fields WHERE step_id IN ({placeholders})', step_ids)
            field_ids = [row[0] for row in cursor.fetchall()]
            
            # 删除字段选项
            if field_ids:
                field_placeholders = ','.join(['%s'] * len(field_ids))
                cursor.execute(f'DELETE FROM flow_field_options WHERE field_id IN ({field_placeholders})', field_ids)
        
        # 删除流程字段
        if step_ids:
            placeholders = ','.join(['%s'] * len(step_ids))
            cursor.execute(f'DELETE FROM flow_fields WHERE step_id IN ({placeholders})', step_ids)
        
        # 删除流程架构步骤
        cursor.execute('DELETE FROM flow_architecture_steps WHERE architecture_id = %s', (architecture_id,))
        
        # 插入新的流程架构步骤
        step_ids = []
        for step in steps:
            step_name = step.get('name')
            approver_id = step.get('approver_id')
            step_order = step.get('step_order')
            
            if not all([step_name, approver_id, step_order]):
                continue
            
            # 插入步骤
            cursor.execute('''
                INSERT INTO flow_architecture_steps (architecture_id, step_name, approver_id, step_order) 
                VALUES (%s, %s, %s, %s)
            ''', (architecture_id, step_name, approver_id, step_order))
            step_ids.append(cursor.lastrowid)
        
        # 插入新的流程字段
        for i, field in enumerate(fields):
            field_name = field.get('name')
            field_type = field.get('type')
            is_required = field.get('is_required', False)
            options = field.get('options', [])
            
            if field_name and field_type:
                # 将字段关联到第一个步骤
                if step_ids:
                    step_id = step_ids[0]
                    cursor.execute('''
                        INSERT INTO flow_fields (step_id, field_name, field_type) 
                        VALUES (%s, %s, %s)
                    ''', (step_id, field_name, field_type))
                    
                    # 如果有选项，保存选项数据
                    if options:
                        field_id = cursor.lastrowid
                        for option in options:
                            cursor.execute('''
                                INSERT INTO flow_field_options (field_id, option_value) 
                                VALUES (%s, %s)
                            ''', (field_id, option))
        
        conn.commit()
        return jsonify({'success': True, 'message': '流程架构更新成功'}), 200
    except Exception as e:
        print(f'更新流程架构错误: {e}')
        if 'conn' in locals():
            conn.rollback()
        return jsonify({'success': False, 'message': '更新流程架构失败'}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@flows_bp.route('/api/flows/architecture/<int:architecture_id>/status', methods=['PUT'])
def update_flow_architecture_status(architecture_id):
    """更新流程架构状态"""
    try:
        data = request.get_json()
        status = data.get('status')
        
        if not status:
            return jsonify({'error': '缺少状态参数'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 更新流程架构状态
        cursor.execute('UPDATE flow_architectures SET status = %s, updated_at = %s WHERE id = %s', 
                     (status, datetime.now(), architecture_id))
        
        conn.commit()
        return jsonify({'success': True, 'message': '流程架构状态更新成功'}), 200
    except Exception as e:
        print(f'更新流程架构状态错误: {e}')
        if 'conn' in locals():
            conn.rollback()
        return jsonify({'success': False, 'message': '更新流程架构状态失败'}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()