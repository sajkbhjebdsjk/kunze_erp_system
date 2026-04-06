import pymysql
from config.db_pool import get_db_connection
from utils.password_utils import hash_password, verify_password

class User:
    @staticmethod
    def get_user_by_username(username):
        """根据用户名获取用户信息"""
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
            user = cursor.fetchone()
            return user
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def get_user_by_id(user_id):
        """根据用户ID获取用户信息"""
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
            user = cursor.fetchone()
            return user
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def get_user_roles(user_id):
        """获取用户的角色"""
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
            return roles
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def get_user_permissions(user_id):
        """获取用户的权限"""
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute('''
                SELECT p.id, p.name, p.code, p.description 
                FROM permissions p 
                JOIN role_permissions rp ON p.id = rp.permission_id 
                JOIN user_roles ur ON rp.role_id = ur.role_id 
                WHERE ur.user_id = %s
            ''', (user_id,))
            permissions = cursor.fetchall()
            return permissions
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def verify_user(username, password):
        """验证用户登录（安全增强版）"""
        user = User.get_user_by_username(username)
        if not user:
            # 安全提示：不要明确告知是用户不存在还是密码错误
            return None, "用户名或密码错误"

        if not verify_password(password, user['password']):
            return None, "用户名或密码错误"

        return user, "验证成功"
    
    @staticmethod
    def create_user(username, password, city_code, department_id, position_id, name):
        """创建新用户"""
        from utils.password_utils import PasswordPolicy
        
        # 验证密码强度
        is_valid, errors = PasswordPolicy.validate_password(password)
        if not is_valid:
            return None, f"密码不符合要求: {', '.join(errors)}"
        
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            hashed_password = hash_password(password)
            cursor.execute('''
                INSERT INTO users (username, password, city_code, department_id, position_id, name)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (username, hashed_password, city_code, department_id, position_id, name))
            user_id = cursor.lastrowid
            conn.commit()
            return user_id, "用户创建成功"
        except Exception as e:
            conn.rollback()
            return None, f"创建用户失败: {str(e)}"
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def update_password(user_id, new_password):
        """更新用户密码"""
        from utils.password_utils import PasswordPolicy
        
        # 验证密码强度
        is_valid, errors = PasswordPolicy.validate_password(new_password)
        if not is_valid:
            return False, f"密码不符合要求: {', '.join(errors)}"
        
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            hashed_password = hash_password(new_password)
            cursor.execute('UPDATE users SET password = %s WHERE id = %s', (hashed_password, user_id))
            
            if cursor.rowcount == 0:
                return False, "用户不存在"
            
            conn.commit()
            return True, "密码更新成功"
        except Exception as e:
            conn.rollback()
            return False, f"密码更新失败: {str(e)}"
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def get_user_with_details(user_id):
        """获取用户详细信息，包括部门和岗位名称"""
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute('''
                SELECT u.*, d.department_name, p.position_name, c.city_name 
                FROM users u 
                LEFT JOIN departments d ON u.department_id = d.department_id 
                LEFT JOIN positions p ON u.position_id = p.position_id 
                LEFT JOIN cities c ON u.city_code = c.city_code 
                WHERE u.id = %s
            ''', (user_id,))
            user = cursor.fetchone()
            return user
        finally:
            cursor.close()
            conn.close()
