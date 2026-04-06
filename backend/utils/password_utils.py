import re
import secrets
import string
from werkzeug.security import generate_password_hash, check_password_hash

class PasswordPolicy:
    """密码策略类"""
    
    MIN_LENGTH = 8
    MAX_LENGTH = 128
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGIT = True
    REQUIRE_SPECIAL = False
    
    @classmethod
    def validate_password(cls, password):
        """验证密码是否符合策略"""
        errors = []
        
        if not password:
            errors.append('密码不能为空')
            return False, errors
        
        if len(password) < cls.MIN_LENGTH:
            errors.append(f'密码长度至少需要{cls.MIN_LENGTH}个字符')
        
        if len(password) > cls.MAX_LENGTH:
            errors.append(f'密码长度不能超过{cls.MAX_LENGTH}个字符')
        
        if cls.REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            errors.append('密码必须包含至少一个大写字母')
        
        if cls.REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            errors.append('密码必须包含至少一个小写字母')
        
        if cls.REQUIRE_DIGIT and not re.search(r'\d', password):
            errors.append('密码必须包含至少一个数字')
        
        if cls.REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append('密码必须包含至少一个特殊字符')
        
        # 检查常见弱密码
        common_passwords = ['123456', 'password', 'admin123', 'qwerty', 'abc123']
        if password.lower() in [p.lower() for p in common_passwords]:
            errors.append('不能使用常见弱密码')
        
        return len(errors) == 0, errors
    
    @classmethod
    def generate_strong_password(cls, length=16):
        """生成强密码"""
        alphabet = string.ascii_letters + string.digits + '!@#$%^&*'
        while True:
            password = ''.join(secrets.choice(alphabet) for _ in range(length))
            is_valid, _ = cls.validate_password(password)
            if is_valid:
                return password

def hash_password(password):
    """对密码进行哈希加密（使用PBKDF2-SHA256）"""
    # 使用werkzeug的安全哈希函数（默认使用PBKDF2-SHA256）
    return generate_password_hash(
        password,
        method='pbkdf2:sha256:260000',
        salt_length=16
    )

def verify_password(password, hashed_password):
    """验证密码是否匹配"""
    try:
        return check_password_hash(hashed_password, password)
    except Exception:
        return False

def check_password_strength(password):
    """检查密码强度并返回强度等级"""
    score = 0
    
    # 长度评分
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if len(password) >= 16:
        score += 1
    
    # 字符种类评分
    if re.search(r'[a-z]', password):
        score += 1
    if re.search(r'[A-Z]', password):
        score += 1
    if re.search(r'\d', password):
        score += 1
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 1
    
    # 根据分数返回强度等级
    if score <= 3:
        return 'weak', '弱'
    elif score <= 5:
        return 'medium', '中等'
    elif score <= 7:
        return 'strong', '强'
    else:
        return 'very_strong', '非常强'
