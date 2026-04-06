import logging
import os
from datetime import datetime
from flask import request

def setup_logger():
    """配置系统日志"""
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, f'system_{datetime.now().strftime("%Y%m%d")}.log')

    logger = logging.getLogger('kunze_erp')
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

logger = setup_logger()

def log_request():
    """记录HTTP请求日志"""
    try:
        method = request.method
        path = request.path
        ip_address = request.remote_addr
        user_agent = request.user_agent.string if request.user_agent else 'Unknown'
        
        # 记录请求信息（不记录敏感数据）
        logger.info(f'请求: {method} {path} - IP: {ip_address} - User-Agent: {user_agent[:100]}')
        
        # 记录可疑请求
        suspicious_patterns = ['<script', '../', 'UNION', 'SELECT', 'DROP', '--', ';']
        for pattern in suspicious_patterns:
            if pattern.lower() in str(request.data).lower() or pattern.lower() in str(request.args).lower():
                logger.warning(f'可疑请求检测: {method} {path} - IP: {ip_address} - 包含模式: {pattern}')
                break
                
    except Exception as e:
        logger.error(f'记录请求日志失败: {str(e)}')

def log_user_action(user_id, username, action, details=None, ip_address=None, module='system'):
    """记录用户操作日志"""
    try:
        from config.db_pool import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("DESCRIBE system_logs")
        columns = [col[0] for col in cursor.fetchall()]
        
        field_list = ['user_id', 'username', 'action', 'created_at']
        value_list = [user_id, username, action, 'NOW()']
        
        if 'module' in columns:
            field_list.append('module')
            value_list.append(module)
        if 'details' in columns:
            field_list.append('details')
            value_list.append(details)
        if 'ip_address' in columns:
            field_list.append('ip_address')
            value_list.append(ip_address)
        if 'description' in columns:
            field_list.append('description')
            value_list.append(details)
        if 'user_agent' in columns:
            field_list.append('user_agent')
            value_list.append(None)
        
        fields_str = ', '.join(field_list)
        values_str = ', '.join(['%s' if v != 'NOW()' else 'NOW()' for v in value_list])
        sql_values = [v for v in value_list if v != 'NOW()']
        
        sql = f"INSERT INTO system_logs ({fields_str}) VALUES ({values_str})"
        
        cursor.execute(sql, sql_values)
        conn.commit()
        cursor.close()
        conn.close()

        logger.info(f'用户操作: {username} - {action} - {details}')
    except Exception as e:
        logger.error(f'记录用户操作日志失败: {str(e)}')

def log_system_error(error_type, error_message, stack_trace=None):
    """记录系统错误日志"""
    try:
        from config.db_pool import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("DESCRIBE system_logs")
        columns = [col[0] for col in cursor.fetchall()]
        
        field_list = ['user_id', 'username', 'action', 'created_at']
        value_list = [0, 'SYSTEM', f'{error_type}: {error_message}', 'NOW()']
        
        if 'module' in columns:
            field_list.append('module')
            value_list.append('system')
        if 'details' in columns:
            field_list.append('details')
            value_list.append(stack_trace)
        if 'description' in columns:
            field_list.append('description')
            value_list.append(stack_trace)
        if 'ip_address' in columns:
            field_list.append('ip_address')
            value_list.append(None)
        if 'user_agent' in columns:
            field_list.append('user_agent')
            value_list.append(None)
        
        fields_str = ', '.join(field_list)
        values_str = ', '.join(['%s' if v != 'NOW()' else 'NOW()' for v in value_list])
        sql_values = [v for v in value_list if v != 'NOW()']
        
        sql = f"INSERT INTO system_logs ({fields_str}) VALUES ({values_str})"
        
        cursor.execute(sql, sql_values)
        conn.commit()
        cursor.close()
        conn.close()

        logger.error(f'系统错误: {error_type} - {error_message}')
    except Exception as e:
        logger.error(f'记录系统错误日志失败: {str(e)}')
