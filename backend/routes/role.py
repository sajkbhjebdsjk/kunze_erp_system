import pymysql
from flask import Blueprint, jsonify, request
from config.database import get_db_connection

role_bp = Blueprint('role', __name__)

@role_bp.route('/api/roles', methods=['GET'])
def get_roles():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        cursor.execute('SELECT * FROM roles')
        roles = cursor.fetchall()
        return jsonify({'success': True, 'roles': roles})
    except Exception as e:
        print(f'数据库错误: {e}')
        return jsonify({'success': False, 'message': '数据库错误'})
    finally:
        cursor.close()
        conn.close()

@role_bp.route('/api/permissions', methods=['GET'])
def get_permissions():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        cursor.execute('SELECT * FROM permissions')
        permissions = cursor.fetchall()
        return jsonify({'success': True, 'permissions': permissions})
    except Exception as e:
        print(f'数据库错误: {e}')
        return jsonify({'success': False, 'message': '数据库错误'})
    finally:
        cursor.close()
        conn.close()

# 获取角色权限
@role_bp.route('/api/roles/<int:role_id>/permissions', methods=['GET'])
def get_role_permissions(role_id):
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        print(f'[权限-DEBUG] 获取角色{role_id}的权限...')
        cursor.execute('''
            SELECT p.id, p.name, p.code, p.description
            FROM permissions p
            JOIN role_permissions rp ON p.id = rp.permission_id
            WHERE rp.role_id = %s
        ''', (role_id,))
        permissions = cursor.fetchall()
        print(f'[权限-DEBUG] 角色{role_id}有{len(permissions)}个权限: {[p["code"] for p in permissions]}')
        return jsonify({'success': True, 'permissions': permissions})
    except Exception as e:
        print(f'[权限-ERROR] 获取角色权限失败: {e}')
        import traceback
        print(f'[权限-ERROR] 堆栈:\n{traceback.format_exc()}')
        return jsonify({'success': False, 'message': '数据库错误'})
    finally:
        cursor.close()
        conn.close()

# 分配权限给角色
@role_bp.route('/api/roles/<int:role_id>/permissions', methods=['POST'])
def assign_role_permission(role_id):
    data = request.get_json()
    permission_id = data.get('permission_id')
    
    if not permission_id:
        return jsonify({'success': False, 'message': '权限ID不能为空'})
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('INSERT IGNORE INTO role_permissions (role_id, permission_id) VALUES (%s, %s)', (role_id, permission_id))
        conn.commit()
        return jsonify({'success': True, 'message': '权限分配成功'})
    except Exception as e:
        print(f'数据库错误: {e}')
        conn.rollback()
        return jsonify({'success': False, 'message': '数据库错误'})
    finally:
        cursor.close()
        conn.close()

# 保存角色（添加/编辑）
@role_bp.route('/api/roles', methods=['POST'])
def save_role():
    data = request.get_json()
    role_id = data.get('id')
    name = data.get('name')
    description = data.get('description')
    
    if not name:
        return jsonify({'success': False, 'message': '角色名称不能为空'})
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if role_id:
            # 编辑角色
            cursor.execute('UPDATE roles SET name = %s, description = %s WHERE id = %s', (name, description, role_id))
        else:
            # 添加角色
            cursor.execute('INSERT INTO roles (name, description) VALUES (%s, %s)', (name, description))
        conn.commit()
        return jsonify({'success': True, 'message': '角色保存成功'})
    except Exception as e:
        print(f'数据库错误: {e}')
        conn.rollback()
        return jsonify({'success': False, 'message': '数据库错误'})
    finally:
        cursor.close()
        conn.close()

# 删除角色
@role_bp.route('/api/roles/<int:role_id>', methods=['DELETE'])
def delete_role(role_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 先删除角色关联的权限
        cursor.execute('DELETE FROM role_permissions WHERE role_id = %s', (role_id,))
        # 再删除角色
        cursor.execute('DELETE FROM roles WHERE id = %s', (role_id,))
        conn.commit()
        return jsonify({'success': True, 'message': '角色删除成功'})
    except Exception as e:
        print(f'数据库错误: {e}')
        conn.rollback()
        return jsonify({'success': False, 'message': '数据库错误'})
    finally:
        cursor.close()
        conn.close()

# 批量保存角色权限
@role_bp.route('/api/roles/<int:role_id>/permissions/batch', methods=['POST'])
def batch_assign_role_permissions(role_id):
    data = request.get_json()
    permission_ids = data.get('permission_ids', [])
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 先删除角色现有的所有权限
        cursor.execute('DELETE FROM role_permissions WHERE role_id = %s', (role_id,))
        
        # 批量添加新权限
        for perm_id in permission_ids:
            cursor.execute('INSERT INTO role_permissions (role_id, permission_id) VALUES (%s, %s)', (role_id, perm_id))
        
        conn.commit()
        return jsonify({'success': True, 'message': '权限分配成功'})
    except Exception as e:
        print(f'数据库错误: {e}')
        conn.rollback()
        return jsonify({'success': False, 'message': '数据库错误'})
    finally:
        cursor.close()
        conn.close()