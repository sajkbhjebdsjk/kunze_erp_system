import os
import pymysql
from dotenv import load_dotenv
from dbutils.pooled_db import PooledDB

load_dotenv()

# 打印所有数据库相关的环境变量（调试用）
print('[DB-CONFIG-DEBUG] ===== 数据库环境变量 =====')
print(f'[DB-CONFIG-DEBUG] DB_HOST = "{os.environ.get("DB_HOST", "未设置")}"')
print(f'[DB-CONFIG-DEBUG] DB_PORT = "{os.environ.get("DB_PORT", "未设置")}"')
print(f'[DB-CONFIG-DEBUG] DB_USER = "{os.environ.get("DB_USER", "未设置")}"')
print(f'[DB-CONFIG-DEBUG] DB_PASSWORD = {"***已设置***" if os.environ.get("DB_PASSWORD") else "未设置"}')
print(f'[DB-CONFIG-DEBUG] DB_NAME = "{os.environ.get("DB_NAME", "未设置")}"')
print(f'[DB-CONFIG-DEBUG] =============================')

DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': int(os.environ.get('DB_PORT', 3306)),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', '123456'),
    'database': os.environ.get('DB_NAME', 'erp_system'),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
    'autocommit': False
}

pool = None

def init_db_pool():
    global pool

    # 打印数据库连接配置（调试用）
    print(f'[DB-POOL-DEBUG] 初始化数据库连接池...')
    print(f'[DB-POOL-DEBUG] DB_HOST: {DB_CONFIG["host"]}')
    print(f'[DB-POOL-DEBUG] DB_USER: {DB_CONFIG["user"]}')
    print(f'[DB-POOL-DEBUG] DB_NAME: {DB_CONFIG["database"]}')
    print(f'[DB-POOL-DEBUG] DB_PORT: 未在配置中显示，默认3306')

    pool = PooledDB(
        creator=pymysql,
        maxconnections=10,
        mincached=2,
        maxcached=5,
        maxshared=3,
        blocking=True,
        maxusage=None,
        setsession=[],
        ping=1,
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_CONFIG['database'],
        charset=DB_CONFIG['charset'],
        cursorclass=DB_CONFIG['cursorclass']
    )
    print('[DB-POOL-DEBUG] 数据库连接池初始化完成！')

def get_db_connection():
    global pool
    if pool is None:
        init_db_pool()
    return pool.connection()

def close_pool():
    global pool
    if pool:
        pool.close()
        pool = None
