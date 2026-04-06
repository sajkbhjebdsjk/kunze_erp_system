from flask import Blueprint, request, jsonify
from config.database import get_db_connection
import pymysql
import uuid
import os
from datetime import datetime

salary_plans_bp = Blueprint('salary_plans', __name__)

@salary_plans_bp.route('/api/salary-plans', methods=['GET'])
def get_salary_plans():
    """获取薪资方案列表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 获取查询参数
        status = request.args.get('status')
        
        # 构建查询语句
        query = 'SELECT * FROM salary_plans'
        
        # 如果提供了status参数，添加状态过滤
        if status:
            query += ' WHERE status = %s'
            params = (status,)
        else:
            params = ()
        
        query += ' ORDER BY updated_at DESC'
        
        # 执行查询
        cursor.execute(query, params)
        plans = cursor.fetchall()
        
        # 格式化时间
        for plan in plans:
            if plan['created_at']:
                plan['created_at'] = plan['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            if plan['updated_at']:
                plan['updated_at'] = plan['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({'success': True, 'data': plans}), 200
    except Exception as e:
        print(f'获取薪资方案列表错误: {e}')
        return jsonify({'error': '获取薪资方案列表失败'}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@salary_plans_bp.route('/api/salary-plans', methods=['POST'])
def create_salary_plan():
    """创建薪资方案"""
    try:
        # 获取表单数据
        plan_name = request.form.get('plan_name')
        plan_type = request.form.get('plan_type')
        description = request.form.get('description', '')
        
        if not plan_name or not plan_type:
            return jsonify({'error': '缺少必要参数'}), 400
        
        # 处理文件上传
        file_path = ''
        if 'file' in request.files:
            file = request.files['file']
            if file.filename:
                # 确保上传目录存在
                upload_dir = 'uploads/salary_plans'
                os.makedirs(upload_dir, exist_ok=True)
                
                # 生成唯一文件名
                file_ext = os.path.splitext(file.filename)[1]
                file_name = f"{uuid.uuid4()}{file_ext}"
                file_path = os.path.join(upload_dir, file_name)
                file.save(file_path)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 插入薪资方案
        cursor.execute('''
            INSERT INTO salary_plans (plan_name, plan_type, description, file_path, status, created_at, updated_at) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (plan_name, plan_type, description, file_path, 'disabled', datetime.now(), datetime.now()))
        
        conn.commit()
        return jsonify({'success': True, 'message': '薪资方案创建成功'}), 201
    except Exception as e:
        print(f'创建薪资方案错误: {e}')
        if 'conn' in locals():
            conn.rollback()
        return jsonify({'success': False, 'message': '创建薪资方案失败'}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@salary_plans_bp.route('/api/salary-plans/<int:plan_id>', methods=['GET'])
def get_salary_plan(plan_id):
    """获取薪资方案详情"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 获取薪资方案信息
        cursor.execute('SELECT * FROM salary_plans WHERE id = %s', (plan_id,))
        plan = cursor.fetchone()
        
        if not plan:
            return jsonify({'error': '薪资方案不存在'}), 404
        
        # 格式化时间
        if plan['created_at']:
            plan['created_at'] = plan['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        if plan['updated_at']:
            plan['updated_at'] = plan['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({'success': True, 'plan': plan}), 200
    except Exception as e:
        print(f'获取薪资方案详情错误: {e}')
        return jsonify({'error': '获取薪资方案详情失败'}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@salary_plans_bp.route('/api/salary-plans/<int:plan_id>', methods=['PUT'])
def update_salary_plan(plan_id):
    """更新薪资方案"""
    try:
        # 获取表单数据
        plan_name = request.form.get('plan_name')
        plan_type = request.form.get('plan_type')
        description = request.form.get('description', '')
        
        if not plan_name or not plan_type:
            return jsonify({'error': '缺少必要参数'}), 400
        
        # 处理文件上传
        file_path = None
        if 'file' in request.files:
            file = request.files['file']
            if file.filename:
                # 确保上传目录存在
                upload_dir = 'uploads/salary_plans'
                os.makedirs(upload_dir, exist_ok=True)
                
                # 生成唯一文件名
                file_ext = os.path.splitext(file.filename)[1]
                file_name = f"{uuid.uuid4()}{file_ext}"
                file_path = os.path.join(upload_dir, file_name)
                file.save(file_path)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 构建更新语句
        if file_path:
            # 如果上传了新文件，更新文件路径
            cursor.execute('''
                UPDATE salary_plans 
                SET plan_name = %s, plan_type = %s, description = %s, file_path = %s, updated_at = %s 
                WHERE id = %s
            ''', (plan_name, plan_type, description, file_path, datetime.now(), plan_id))
        else:
            # 如果没有上传新文件，只更新其他字段
            cursor.execute('''
                UPDATE salary_plans 
                SET plan_name = %s, plan_type = %s, description = %s, updated_at = %s 
                WHERE id = %s
            ''', (plan_name, plan_type, description, datetime.now(), plan_id))
        
        conn.commit()
        return jsonify({'success': True, 'message': '薪资方案更新成功'}), 200
    except Exception as e:
        print(f'更新薪资方案错误: {e}')
        if 'conn' in locals():
            conn.rollback()
        return jsonify({'success': False, 'message': '更新薪资方案失败'}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@salary_plans_bp.route('/api/salary-plans/<int:plan_id>', methods=['DELETE'])
def delete_salary_plan(plan_id):
    """删除薪资方案"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 删除薪资方案
        cursor.execute('DELETE FROM salary_plans WHERE id = %s', (plan_id,))
        
        conn.commit()
        return jsonify({'success': True, 'message': '薪资方案删除成功'}), 200
    except Exception as e:
        print(f'删除薪资方案错误: {e}')
        if 'conn' in locals():
            conn.rollback()
        return jsonify({'success': False, 'message': '删除薪资方案失败'}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@salary_plans_bp.route('/api/salary-plans/<int:plan_id>/status', methods=['PUT'])
def update_salary_plan_status(plan_id):
    """更新薪资方案状态"""
    try:
        data = request.get_json()
        status = data.get('status')
        
        if not status:
            return jsonify({'error': '缺少状态参数'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 更新薪资方案状态
        cursor.execute('UPDATE salary_plans SET status = %s, updated_at = %s WHERE id = %s', 
                     (status, datetime.now(), plan_id))
        
        conn.commit()
        return jsonify({'success': True, 'message': '薪资方案状态更新成功'}), 200
    except Exception as e:
        print(f'更新薪资方案状态错误: {e}')
        if 'conn' in locals():
            conn.rollback()
        return jsonify({'success': False, 'message': '更新薪资方案状态失败'}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()