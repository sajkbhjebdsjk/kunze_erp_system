import pymysql
from flask import Blueprint, jsonify, request
from config.database import get_db_connection

log_bp = Blueprint('log', __name__)

@log_bp.route('/api/logs', methods=['GET'])
def get_logs():
    """获取系统日志"""
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        action = request.args.get('action')
        username = request.args.get('username')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        query = "SELECT * FROM system_logs WHERE 1=1"
        params = []

        if action:
            query += " AND action LIKE %s"
            params.append(f'%{action}%')

        if username:
            query += " AND username LIKE %s"
            params.append(f'%{username}%')

        if start_date:
            query += " AND created_at >= %s"
            params.append(start_date)

        if end_date:
            query += " AND created_at <= %s"
            params.append(end_date)

        query += " ORDER BY created_at DESC"

        offset = (page - 1) * per_page
        query += f" LIMIT {per_page} OFFSET {offset}"

        cursor.execute(query, params)
        logs = cursor.fetchall()

        count_query = "SELECT COUNT(*) as total FROM system_logs WHERE 1=1"
        count_params = []

        if action:
            count_query += " AND action LIKE %s"
            count_params.append(f'%{action}%')

        if username:
            count_query += " AND username LIKE %s"
            count_params.append(f'%{username}%')

        if start_date:
            count_query += " AND created_at >= %s"
            count_params.append(start_date)

        if end_date:
            count_query += " AND created_at <= %s"
            count_params.append(end_date)

        cursor.execute(count_query, count_params)
        total = cursor.fetchone()['total']

        return jsonify({
            'success': True,
            'logs': logs,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cursor.close()
        conn.close()
