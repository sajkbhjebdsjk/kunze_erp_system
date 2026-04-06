import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, g
import os

SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production-2026')

def generate_token(user_id, username, roles):
    """生成JWT Token"""
    payload = {
        'user_id': user_id,
        'username': username,
        'roles': roles,
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def decode_token(token):
    """解码并验证JWT Token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None, 'Token已过期'
    except jwt.InvalidTokenError:
        return None, '无效的Token'

def token_required(f):
    """Token验证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # 从Header中获取Token
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
        
        if not token:
            return jsonify({
                'success': False,
                'message': '缺少认证Token'
            }), 401
        
        # 验证Token
        payload, error_msg = decode_token(token)
        if not payload:
            return jsonify({
                'success': False,
                'message': error_msg
            }), 401
        
        # 将用户信息存储到g对象中，供后续使用
        g.current_user_id = payload['user_id']
        g.current_username = payload['username']
        g.current_roles = payload.get('roles', [])
        
        return f(*args, **kwargs)
    
    return decorated

def admin_required(f):
    """管理员权限验证装饰器"""
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        if 'admin' not in g.current_roles and '总部运营' not in [r.get('name') for r in g.current_roles]:
            return jsonify({
                'success': False,
                'message': '需要管理员权限'
            }), 403
        return f(*args, **kwargs)
    
    return decorated
