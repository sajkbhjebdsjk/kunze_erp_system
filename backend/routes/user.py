import pymysql
from flask import Blueprint, jsonify, request
from config.database import get_db_connection
from utils.password_utils import hash_password
from utils.logger import log_user_action

user_bp = Blueprint('user', __name__)

@user_bp.route('/api/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 获取查询参数
        query = request.args.get('query')
        city_code = request.args.get('city_code')
        
        # 构建基础查询
        base_query = '''
            SELECT u.*, d.department_name, c.city_name, p.position_name 
            FROM users u 
            JOIN departments d ON u.department_id = d.department_id 
            JOIN cities c ON u.city_code = c.city_code
            JOIN positions p ON u.position_id = p.position_id
            WHERE 1=1
        '''
        params = []
        
        # 添加城市筛选
        if city_code and city_code != 'all':
            base_query += ' AND u.city_code = %s'
            params.append(city_code)
        
        # 添加查询条件
        if query:
            base_query += ' AND u.name LIKE %s'
            params.append(f'%{query}%')
        
        # 执行查询
        cursor.execute(base_query, params)
        
        users = cursor.fetchall()
        return jsonify({'success': True, 'users': users})
    except Exception as e:
        print(f'数据库错误: {e}')
        return jsonify({'success': False, 'message': '数据库错误'})
    finally:
        cursor.close()
        conn.close()

# 获取用户角色
@user_bp.route('/api/users/<int:user_id>/roles', methods=['GET'])
def get_user_roles(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        cursor.execute('''
            SELECT r.id, r.name, r.description 
            FROM roles r 
            JOIN user_roles ur ON r.id = ur.role_id 
            WHERE ur.user_id = %s
        ''', (user_id,))
        roles = cursor.fetchall()
        return jsonify({'success': True, 'roles': roles})
    except Exception as e:
        print(f'数据库错误: {e}')
        return jsonify({'success': False, 'message': '数据库错误'})
    finally:
        cursor.close()
        conn.close()

# 分配角色给用户
@user_bp.route('/api/users/<int:user_id>/roles', methods=['POST'])
def assign_user_role(user_id):
    data = request.get_json()
    role_id = data.get('role_id')
    
    if not role_id:
        return jsonify({'success': False, 'message': '角色ID不能为空'})
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('INSERT IGNORE INTO user_roles (user_id, role_id) VALUES (%s, %s)', (user_id, role_id))
        conn.commit()
        log_user_action(0, 'system', '分配角色', f'为用户ID {user_id} 分配角色ID: {role_id}', request.remote_addr)
        return jsonify({'success': True, 'message': '角色分配成功'})
    except Exception as e:
        print(f'数据库错误: {e}')
        conn.rollback()
        return jsonify({'success': False, 'message': '数据库错误'})
    finally:
        cursor.close()
        conn.close()

# 批量保存用户角色
@user_bp.route('/api/users/<int:user_id>/roles/batch', methods=['POST'])
def batch_assign_user_roles(user_id):
    data = request.get_json()
    role_ids = data.get('role_ids', [])
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 先删除用户现有的所有角色
        cursor.execute('DELETE FROM user_roles WHERE user_id = %s', (user_id,))
        
        # 批量添加新角色
        for role_id in role_ids:
            cursor.execute('INSERT INTO user_roles (user_id, role_id) VALUES (%s, %s)', (user_id, role_id))
        
        conn.commit()
        log_user_action(0, 'system', '批量分配角色', f'为用户ID {user_id} 批量分配角色: {role_ids}', request.remote_addr)
        return jsonify({'success': True, 'message': '角色分配成功'})
    except Exception as e:
        print(f'数据库错误: {e}')
        conn.rollback()
        return jsonify({'success': False, 'message': '数据库错误'})
    finally:
        cursor.close()
        conn.close()

# 删除用户
@user_bp.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 先删除用户关联的角色
        cursor.execute('DELETE FROM user_roles WHERE user_id = %s', (user_id,))
        # 再删除用户
        cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
        conn.commit()
        log_user_action(0, 'system', '删除用户', f'删除用户ID: {user_id}', request.remote_addr)
        return jsonify({'success': True, 'message': '用户删除成功'})
    except Exception as e:
        print(f'数据库错误: {e}')
        conn.rollback()
        return jsonify({'success': False, 'message': '数据库错误'})
    finally:
        cursor.close()
        conn.close()

# 创建用户
@user_bp.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    name = data.get('name')
    position_id = data.get('position_id')
    department_id = data.get('department_id')
    city_code = data.get('city_code')
    
    if not all([username, password, name, position_id, department_id, city_code]):
        return jsonify({'success': False, 'message': '所有字段不能为空'})
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        hashed_password = hash_password(password)
        cursor.execute('''
            INSERT INTO users (username, password, city_code, department_id, position_id, name)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (username, hashed_password, city_code, department_id, position_id, name))
        user_id = cursor.lastrowid
        
        # 为选择"全部城市"的用户自动分配"总部运营"角色
        if city_code == 'all':
            # 获取总部运营角色ID
            cursor.execute('SELECT id FROM roles WHERE name = %s', ('总部运营',))
            admin_role = cursor.fetchone()
            if admin_role:
                admin_role_id = admin_role[0]
                # 分配角色
                cursor.execute('INSERT IGNORE INTO user_roles (user_id, role_id) VALUES (%s, %s)', (user_id, admin_role_id))
        
        conn.commit()
        log_user_action(0, 'system', '创建用户', f'创建用户: {username}', request.remote_addr)
        return jsonify({'success': True, 'message': '用户创建成功', 'user_id': user_id})
    except Exception as e:
        print(f'数据库错误: {e}')
        conn.rollback()
        return jsonify({'success': False, 'message': '数据库错误'})
    finally:
        cursor.close()
        conn.close()