import pymysql
from flask import Blueprint, jsonify, request
from models.user import User
from config.db_pool import get_db_connection
from utils.logger import log_user_action
from utils.auth import generate_token
from utils.password_utils import PasswordPolicy, check_password_strength
from utils.rate_limiter import rate_limit

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/login', methods=['POST'])
@rate_limit
def login():
    """用户登录（增强版 - 集成JWT和密码策略）"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        ip_address = request.remote_addr
        
        # 输入验证
        if not username or not password:
            log_user_action(0, username, '登录失败', '原因: 用户名或密码为空', ip_address)
            return jsonify({
                'success': False,
                'message': '用户名和密码不能为空'
            }), 400
        
        # 用户名长度验证
        if len(username) < 3 or len(username) > 50:
            return jsonify({
                'success': False,
                'message': '用户名长度必须在3-50个字符之间'
            }), 400
        
        # 密码长度基本验证（不检查强度，只检查是否为空）
        if len(password) < 1:
            return jsonify({
                'success': False,
                'message': '密码不能为空'
            }), 400
        
        # 验证用户
        user, message = User.verify_user(username, password)
        if not user:
            log_user_action(0, username, '登录失败', f'原因: {message}', ip_address)
            
            # 安全提示：不要明确告知是用户名错误还是密码错误
            return jsonify({
                'success': False,
                'message': '用户名或密码错误'
            }), 401
        
        log_user_action(user['id'], username, '登录成功', f'IP: {ip_address}', ip_address)
        
        # 获取用户角色
        roles = User.get_user_roles(user['id'])
        
        # 获取用户权限
        permissions = User.get_user_permissions(user['id'])
        
        # 获取部门名称、岗位名称和城市名称
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('''
            SELECT d.department_name, p.position_name, c.city_name 
            FROM departments d 
            JOIN positions p ON p.position_id = %s 
            JOIN cities c ON c.city_code = %s 
            WHERE d.department_id = %s
        ''', (user['position_id'], user['city_code'], user['department_id']))
        dept_pos_city_info = cursor.fetchone()
        cursor.close()
        conn.close()
        
        # 生成JWT Token
        roles_list = [{'id': role['id'], 'name': role['name']} for role in roles]
        token = generate_token(
            user_id=user['id'],
            username=username,
            roles=roles_list
        )
        
        # 构建用户信息字典
        user_info = {
            'id': user['id'],
            'username': user['username'],
            'name': user['name'],
            'position': dept_pos_city_info['position_name'] if dept_pos_city_info else '',
            'position_id': user['position_id'],
            'department_id': user['department_id'],
            'department_name': dept_pos_city_info['department_name'] if dept_pos_city_info else '',
            'city_code': user['city_code'],
            'city_name': dept_pos_city_info['city_name'] if dept_pos_city_info else '',
            'roles': [{'id': role['id'], 'name': role['name'], 'description': role['description']} for role in roles],
            'permissions': [{'id': perm['id'], 'name': perm['name'], 'code': perm['code'], 'description': perm['description']} for perm in permissions]
        }
        
        # 返回用户信息和Token
        response = jsonify({
            'success': True,
            'message': '登录成功',
            'token': token,
            'user': user_info,
            'token_type': 'Bearer',
            'expires_in': 86400  # 24小时（秒）
        })
        
        return response
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'服务器内部错误: {str(e)}'
        }), 500

@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    """用户登出"""
    return jsonify({
        'success': True,
        'message': '登出成功'
    })

@auth_bp.route('/api/check-password-strength', methods=['POST'])
def check_password_strength_endpoint():
    """检查密码强度接口"""
    data = request.get_json()
    password = data.get('password', '')
    
    strength_level, strength_text = check_password_strength(password)
    
    is_valid, errors = PasswordPolicy.validate_password(password)
    
    return jsonify({
        'success': True,
        'strength': {
            'level': strength_level,
            'text': strength_text
        },
        'is_valid': is_valid,
        'errors': errors if not is_valid else []
    })

@auth_bp.route('/api/change-password', methods=['POST'])
def change_password():
    """修改密码"""
    from utils.auth import token_required
    from flask import g
    
    @token_required
    def _change_password():
        data = request.get_json()
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        
        if not old_password or not new_password:
            return jsonify({
                'success': False,
                'message': '旧密码和新密码不能为空'
            }), 400
        
        # 验证新密码强度
        is_valid, errors = PasswordPolicy.validate_password(new_password)
        if not is_valid:
            return jsonify({
                'success': False,
                'message': '新密码不符合安全要求',
                'errors': errors
            }), 400
        
        # 验证旧密码
        user = User.get_user_by_id(g.current_user_id)
        if not User.verify_user(user['username'], old_password)[0]:
            return jsonify({
                'success': False,
                'message': '旧密码错误'
            }), 401
        
        # 更新密码
        success, message = User.update_password(g.current_user_id, new_password)
        if not success:
            return jsonify({
                'success': False,
                'message': message
            }), 500
        
        return jsonify({
            'success': True,
            'message': '密码修改成功，请重新登录'
        })
    
    return _change_password()
