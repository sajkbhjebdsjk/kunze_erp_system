from flask import Flask, jsonify
from config.database import init_database
from config.db_pool import init_db_pool
from config.security import setup_security_headers, setup_cors, SecurityConfig
from routes.auth import auth_bp
from routes.role import role_bp
from routes.user import user_bp
from routes.department import department_bp
from routes.flows import flows_bp
from routes.salary_plans import salary_plans_bp
from routes.rider import rider_bp
from routes.contracts import contracts_bp
from routes.rider_contract_sign import rider_contract_bp
from routes.admin import admin_bp
from routes.log import log_bp
import os

app = Flask(__name__)

# 安全配置
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', SecurityConfig.JWT_SECRET_KEY)
app.config['MAX_CONTENT_LENGTH'] = SecurityConfig.MAX_CONTENT_LENGTH
app.config['SESSION_COOKIE_HTTPONLY'] = SecurityConfig.SESSION_COOKIE_HTTPONLY
app.config['SESSION_COOKIE_SECURE'] = SecurityConfig.SESSION_COOKIE_SECURE
app.config['PERMANENT_SESSION_LIFETIME'] = SecurityConfig.PERMANENT_SESSION_LIFETIME
app.config['JSON_AS_ASCII'] = False  # 支持中文响应

# 配置安全的CORS（替代原来的CORS(app)）
setup_cors(app)

# 配置上传目录
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 注册路由蓝图
app.register_blueprint(auth_bp)
app.register_blueprint(role_bp)
app.register_blueprint(user_bp)
app.register_blueprint(department_bp)
app.register_blueprint(flows_bp)
app.register_blueprint(salary_plans_bp)
app.register_blueprint(rider_bp)
app.register_blueprint(contracts_bp)
app.register_blueprint(rider_contract_bp)
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(log_bp)

# 设置安全响应头
setup_security_headers(app)

# 提供前端静态文件服务
from flask import send_from_directory

def _get_mimetype(filename):
    """根据文件扩展名返回正确的 MIME 类型"""
    if filename.endswith('.html'):
        return 'text/html; charset=utf-8'
    elif filename.endswith('.css'):
        return 'text/css; charset=utf-8'
    elif filename.endswith('.js'):
        return 'application/javascript; charset=utf-8'
    elif filename.endswith('.json'):
        return 'application/json; charset=utf-8'
    elif filename.endswith('.png'):
        return 'image/png'
    elif filename.endswith('.jpg') or filename.endswith('.jpeg'):
        return 'image/jpeg'
    elif filename.endswith('.gif'):
        return 'image/gif'
    elif filename.endswith('.svg'):
        return 'image/svg+xml'
    elif filename.endswith('.ico'):
        return 'image/x-icon'
    else:
        return 'application/octet-stream'

@app.route('/uploads/<path:filename>')
def uploads(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# 排除API路由和已知路径，避免catch-all路由拦截API请求
_EXCLUDED_PREFIXES = ('/api/', '/uploads/', '/favicon.ico', '/static/')

@app.route('/<path:filename>')
def frontend_files(filename):
    # 排除API路径和其他非静态请求
    for prefix in _EXCLUDED_PREFIXES:
        if filename.startswith(prefix.lstrip('/')):
            from flask import abort
            abort(404)

    # 先尝试从项目根目录查找（如 rider-contract-sign.html）
    root_dir = os.path.dirname(os.path.dirname(__file__))
    root_file = os.path.join(root_dir, filename)
    if os.path.isfile(root_file) and (filename.endswith('.html') or filename.endswith('.js') or filename.endswith('.css')):
        resp = send_from_directory(root_dir, filename, mimetype=_get_mimetype(filename))
        resp.headers['Cache-Control'] = 'no-cache, must-revalidate'
        return resp

    # 再尝试从 frontend 目录查找
    frontend_dir = os.path.join(root_dir, 'frontend')
    frontend_file = os.path.join(frontend_dir, filename)
    if os.path.isfile(frontend_file):
        resp = send_from_directory(frontend_dir, filename, mimetype=_get_mimetype(filename))
        resp.headers['Cache-Control'] = 'no-cache, must-revalidate'
        return resp

    # 如果都找不到，返回404
    from flask import abort
    abort(404)

# 根路径重定向到登录页面
@app.route('/')
def index():
    resp = send_from_directory(
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend'),
        'login.html',
        mimetype='text/html; charset=utf-8'
    )
    return resp

# 处理favicon.ico请求（消除404错误）
@app.route('/favicon.ico')
def favicon():
    return '', 204  # 返回空内容，状态码204表示无内容

# 全局错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'message': '请求的资源不存在'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'message': '服务器内部错误'
    }), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({
        'success': False,
        'message': f'上传文件过大，最大允许{SecurityConfig.MAX_CONTENT_LENGTH // (1024*1024)}MB'
    }), 413

# 全局请求日志中间件
@app.before_request
def log_request_info():
    from utils.logger import log_request
    log_request()

if __name__ == '__main__':
    # 初始化数据库连接池
    init_db_pool()
    
    # 初始化数据库表结构
    init_database()
    
    # 生产环境应使用WSGI服务器运行
    # 开发环境使用debug模式
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print("=" * 60)
    print("ERP系统启动中...")
    print("   安全配置已加载")
    print("   数据库连接池已初始化")
    print("   JWT认证已启用")
    print("   请求限流已启用")
    print("=" * 60)
    
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
