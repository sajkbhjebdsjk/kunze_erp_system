import os
import pymysql
from dotenv import load_dotenv
from dbutils.pooled_db import PooledDB

load_dotenv()

DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
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
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_CONFIG['database'],
        charset=DB_CONFIG['charset'],
        cursorclass=DB_CONFIG['cursorclass']
    )

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
