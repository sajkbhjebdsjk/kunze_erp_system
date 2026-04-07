import os
import sys
from flask import Flask, request, jsonify
from datetime import timedelta


class SecurityConfig:
    """安全配置类 - 生产环境安全最佳实践"""

    # ==================== JWT配置 ====================
    # ⚠️ 重要：必须通过环境变量设置，不再提供默认值！
    _jwt_secret = os.environ.get('JWT_SECRET_KEY', '').strip()
    if not _jwt_secret:
        print("⚠️  警告：JWT_SECRET_KEY 未设置！请检查 .env 文件配置")
        print("   使用命令生成: python -c \"import secrets; print(secrets.token_urlsafe(32))\"")
        if os.environ.get('FLASK_ENV', 'development') == 'production':
            print("❌ 生产环境必须设置 JWT_SECRET_KEY，程序将退出")
            sys.exit(1)
        else:
            _jwt_secret = 'dev-secret-key-only-for-testing-2026'
            print(f"   开发环境使用临时密钥（仅用于测试）")

    JWT_SECRET_KEY = _jwt_secret
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.environ.get('JWT_EXPIRATION_HOURS', '24')))
    JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM', 'HS256')

    # ==================== 密码策略 ====================
    PASSWORD_MIN_LENGTH = int(os.environ.get('PASSWORD_MIN_LENGTH', '8'))
    PASSWORD_REQUIRE_UPPERCASE = os.environ.get('PASSWORD_REQUIRE_UPPERCASE', 'True').lower() == 'true'
    PASSWORD_REQUIRE_LOWERCASE = os.environ.get('PASSWORD_REQUIRE_LOWERCASE', 'True').lower() == 'true'
    PASSWORD_REQUIRE_DIGIT = os.environ.get('PASSWORD_REQUIRE_DIGIT', 'True').lower() == 'true'
    PASSWORD_REQUIRE_SPECIAL = os.environ.get('PASSWORD_REQUIRE_SPECIAL', 'False').lower() == 'true'

    # ==================== 会话配置（动态适应环境）====================
    SESSION_COOKIE_HTTPONLY = True  # 始终启用，防止JavaScript访问cookie
    
    # 根据环境自动设置 Secure 标志
    _flask_env = os.environ.get('FLASK_ENV', 'development').lower()
    if _flask_env == 'production':
        SESSION_COOKIE_SECURE = True  # 生产环境必须使用HTTPS
        print("✓ 生产环境模式：SESSION_COOKIE_SECURE=True (需要HTTPS)")
    else:
        SESSION_COOKIE_SECURE = False  # 开发环境允许HTTP
        print("✓ 开发环境模式：SESSION_COOKIE_SECURE=False (允许HTTP)")
    
    SESSION_COOKIE_SAMESITE = 'Lax'  # 防止CSRF攻击
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

    # ==================== CORS配置 ====================
    # 从环境变量读取，生产环境应限制为特定域名
    _cors_origins = os.environ.get('CORS_ORIGINS', '').strip()
    if not _cors_origins:
        if _flask_env == 'production':
            CORS_ORIGINS = []  # 生产环境不允许通配符
            print("⚠️  警告：CORS_ORIGINS 未设置，跨域请求将被拒绝")
        else:
            CORS_ORIGINS = ['*']  # 开发环境允许所有来源
            print("✓ 开发环境模式：CORS 允许所有来源 (*)")
    else:
        CORS_ORIGINS = [origin.strip() for origin in _cors_origins.split(',') if origin.strip()]
        print(f"✓ CORS 已配置允许的来源: {CORS_ORIGINS}")

    CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization', 'X-Requested-With']

    # ==================== 安全响应头 ====================
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        
        # HSTS - 强制使用HTTPS（仅在Secure模式下生效）
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
        
        # Content Security Policy - 防止XSS和数据注入攻击
        # 生产环境允许连接到 Railway 域名，开发环境允许 localhost
        'Content-Security-Policy': (
            "default-src 'self'; "
            "connect-src 'self' "
            + ("http://localhost:5000 http://127.0.0.1:5000 " if _flask_env == 'development' else "")
            + "https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://unpkg.com; "
            "https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://unpkg.com; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' "
            "https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://cdn.tailwindcss.com https://unpkg.com; "
            "style-src 'self' 'unsafe-inline' "
            "https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
            "font-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.gstatic.com; "
            "img-src 'self' data: blob: https:; "
            "frame-ancestors 'none'"
        ),
        
        # Referrer策略 - 控制Referer头信息泄露
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        
        # 权限策略 - 禁用敏感API访问
        'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
    }

    # ==================== 文件上传限制 ====================
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH_MB', '16')) * 1024 * 1024
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'uploads')

    @classmethod
    def validate_security_config(cls):
        """验证安全配置是否正确"""
        issues = []
        
        if cls._flask_env == 'production':
            if not os.environ.get('JWT_SECRET_KEY'):
                issues.append("JWT_SECRET_KEY 未设置")
            
            if not os.environ.get('CORS_ORIGINS'):
                issues.append("CORS_ORIGINS 未设置（建议限制为特定域名）")
            
            if not cls.SESSION_COOKIE_SECURE:
                issues.append("SESSION_COOKIE_SECURE 应为 True（需要HTTPS）")
        
        return issues


def setup_security_headers(app):
    """设置安全响应头中间件"""
    @app.after_request
    def add_security_headers(response):
        # 关键修复：确保 HTML 响应有正确的 Content-Type
        if not response.headers.get('Content-Type') or 'text/html' not in response.headers.get('Content-Type', ''):
            # 检查是否是 HTML 内容（通过 URL 或内容判断）
            from flask import request
            if (request.path.endswith('.html') or 
                request.path == '/' or 
                (response.data and b'<html' in response.data[:200].lower())):
                response.headers['Content-Type'] = 'text/html; charset=utf-8'
        
        for header, value in SecurityConfig.SECURITY_HEADERS.items():
            response.headers[header] = value
        return response


def setup_cors(app):
    """配置CORS跨域资源共享"""
    from flask_cors import CORS
    
    if not SecurityConfig.CORS_ORIGINS:
        print("⚠️  CORS未配置，跳过CORS初始化")
        return
    
    cors_config = {
        'origins': SecurityConfig.CORS_ORIGINS,
        'methods': SecurityConfig.CORS_METHODS,
        'allow_headers': SecurityConfig.CORS_ALLOW_HEADERS,
        'supports_credentials': True,
        'max_age': 600
    }
    
    try:
        CORS(app, **cors_config)
        print(f"✓ CORS已成功配置，允许 {len(SecurityConfig.CORS_ORIGINS)} 个来源")
    except Exception as e:
        print(f"❌ CORS配置失败: {e}")


def validate_file_upload(filename):
    """验证上传文件的安全性和类型"""
    if not filename or '.' not in filename:
        return False, '文件缺少扩展名或文件名为空'
    
    ext = filename.rsplit('.', 1)[1].lower()
    if ext not in SecurityConfig.ALLOWED_EXTENSIONS:
        return False, f'不允许的文件类型: .{ext}（允许的类型: {", ".join(SecurityConfig.ALLOWED_EXTENSIONS)}）'
    
    # 检查文件名安全性（防止路径遍历攻击）
    if '..' in filename or '/' in filename or '\\' in filename:
        return False, '文件名包含非法字符'
    
    return True, None


def sanitize_input(text):
    """清理用户输入，防止XSS和注入攻击"""
    if not text:
        return text
    
    import re
    
    # 移除潜在的HTML标签
    clean_text = re.sub(r'<[^>]*>', '', str(text))
    
    # 移除JavaScript事件处理器
    clean_text = re.sub(r'on\w+\s*=', '', clean_text)
    
    # 移除javascript:协议
    clean_text = re.sub(r'javascript:', '', clean_text, flags=re.IGNORECASE)
    
    # 移除data:URI（可能用于注入）
    clean_text = re.sub(r'data\s*:', '', clean_text, flags=re.IGNORECASE)
    
    # 限制长度防止DoS攻击
    max_length = 10000
    if len(clean_text) > max_length:
        clean_text = clean_text[:max_length]
    
    return clean_text.strip()


def generate_secure_token(length=32):
    """生成安全的随机令牌"""
    import secrets
    return secrets.token_urlsafe(length)


def check_production_readiness():
    """检查生产环境准备情况"""
    if os.environ.get('FLASK_ENV', 'development').lower() != 'production':
        return True, "开发环境模式"
    
    issues = SecurityConfig.validate_security_config()
    
    if issues:
        return False, f"生产环境安全问题:\n  - " + "\n  - ".join(issues)
    
    return True, "✓ 生产环境安全配置检查通过"
