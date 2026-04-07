import pymysql
from flask import Blueprint, jsonify, request
from config.database import get_db_connection

department_bp = Blueprint('department', __name__)

@department_bp.route('/api/departments', methods=['GET'])
def get_departments():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        cursor.execute('SELECT * FROM departments')
        departments = cursor.fetchall()
        return jsonify({'success': True, 'departments': departments})
    except Exception as e:
        print(f'数据库错误: {e}')
        return jsonify({'success': False, 'message': '数据库错误'})
    finally:
        cursor.close()
        conn.close()

@department_bp.route('/api/cities', methods=['GET'])
def get_cities():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 查询所有城市
        cursor.execute('SELECT city_code, city_name FROM cities')
        cities = cursor.fetchall()
        return jsonify({'success': True, 'cities': cities})
    except Exception as e:
        print(f'数据库错误: {e}')
        return jsonify({'success': False, 'message': '数据库错误'})
    finally:
        cursor.close()
        conn.close()

@department_bp.route('/api/positions', methods=['GET'])
def get_positions():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        cursor.execute('SELECT * FROM positions')
        positions = cursor.fetchall()
        return jsonify({'success': True, 'positions': positions})
    except Exception as e:
        print(f'数据库错误: {e}')
        return jsonify({'success': False, 'message': '数据库错误'})
    finally:
        cursor.close()
        conn.close()

@department_bp.route('/api/stations', methods=['GET'])
def get_stations():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 获取城市参数
        city_code = request.args.get('city_code')
        
        # 构建查询条件
        city_condition = ''
        params = []
        
        if city_code and city_code != 'all':
            city_condition = ' WHERE s.city_code = %s'
            params.append(city_code)
        
        # 统计总公司人数
        if city_code and city_code != 'all':
            cursor.execute('''
                SELECT COUNT(*) as total_count 
                FROM management_staff ms 
                JOIN stations s ON ms.team = s.station_name 
                WHERE s.city_code = %s
            ''', (city_code,))
        else:
            cursor.execute('SELECT COUNT(*) as total_count FROM management_staff')
        total_count = cursor.fetchone()['total_count']
        
        # 统计每个区域的人数
        if city_code and city_code != 'all':
            cursor.execute('''
                SELECT ms.area_manager, COUNT(*) as count 
                FROM management_staff ms 
                JOIN stations s ON ms.team = s.station_name 
                WHERE s.city_code = %s
                GROUP BY ms.area_manager 
                ORDER BY ms.area_manager
            ''', (city_code,))
        else:
            cursor.execute('SELECT area_manager, COUNT(*) as count FROM management_staff GROUP BY area_manager ORDER BY area_manager')
        area_counts = cursor.fetchall()
        area_count_map = {}
        for item in area_counts:
            area_count_map[item['area_manager']] = item['count']
        
        # 统计每个站点的人数
        if city_code and city_code != 'all':
            cursor.execute('''
                SELECT ms.team, COUNT(*) as count 
                FROM management_staff ms 
                JOIN stations s ON ms.team = s.station_name 
                WHERE s.city_code = %s
                GROUP BY ms.team 
                ORDER BY ms.team
            ''', (city_code,))
        else:
            cursor.execute('SELECT team, COUNT(*) as count FROM management_staff GROUP BY team ORDER BY team')
        station_counts = cursor.fetchall()
        station_count_map = {}
        for item in station_counts:
            station_count_map[item['team']] = item['count']
        
        # 从management_staff表中获取唯一的区域经理（区域）
        if city_code and city_code != 'all':
            cursor.execute('''
                SELECT DISTINCT ms.area_manager 
                FROM management_staff ms 
                JOIN stations s ON ms.team = s.station_name 
                WHERE s.city_code = %s
                ORDER BY ms.area_manager
            ''', (city_code,))
        else:
            cursor.execute('SELECT DISTINCT area_manager FROM management_staff ORDER BY area_manager')
        areas = cursor.fetchall()
        
        # 从stations表中获取站点数据
        if city_code and city_code != 'all':
            query = '''SELECT station_id, station_name, area_manager 
                       FROM stations WHERE city_code = %s 
                       GROUP BY station_id, station_name, area_manager 
                       ORDER BY station_name'''
            cursor.execute(query, (city_code,))
        else:
            query = '''SELECT station_id, station_name, area_manager 
                       FROM stations 
                       GROUP BY station_id, station_name, area_manager 
                       ORDER BY station_name'''
            cursor.execute(query)
        stations = cursor.fetchall()
        
        # 构建完整的层次结构数据
        result = []
        
        # 添加总公司
        result.append({
            'department_id': '1',
            'department_name': '杭州坤泽物流有限公司',
            'parent_id': '0',
            'level': 1,
            'staff_count': total_count
        })
        
        # 区域ID从2开始
        area_id = 2
        station_id = 100  # 站点ID从100开始
        
        # 添加区域
        for area in areas:
            area_name = area['area_manager']
            area_count = area_count_map.get(area_name, 0)
            result.append({
                'department_id': str(area_id),
                'department_name': area_name,
                'parent_id': '1',
                'level': 2,
                'staff_count': area_count
            })
            
            # 为每个区域添加对应的站点
            for station in stations:
                if station['area_manager'] == area_name:
                    station_count = station_count_map.get(station['station_name'], 0)
                    result.append({
                        'department_id': str(station_id),
                        'department_name': station['station_name'],
                        'parent_id': str(area_id),
                        'level': 3,
                        'staff_count': station_count
                    })
                    station_id += 1
            
            area_id += 1
        
        return jsonify({'success': True, 'stations': result})
    except Exception as e:
        print(f'数据库错误: {e}')
        return jsonify({'success': False, 'message': '数据库错误'})
    finally:
        cursor.close()
        conn.close()

@department_bp.route('/api/departments/<department_id>', methods=['GET'])
def get_department_details(department_id):
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 从完整的部门树数据中获取部门信息
        # 首先获取所有区域和站点
        cursor.execute('SELECT DISTINCT area_manager FROM management_staff ORDER BY area_manager')
        areas = cursor.fetchall()
        
        cursor.execute('SELECT DISTINCT station_name, area_manager FROM stations ORDER BY station_name')
        stations = cursor.fetchall()
        
        # 构建部门映射
        dept_map = {}
        dept_map['1'] = {'name': '杭州坤泽物流有限公司', 'type': '总部'}
        
        # 区域ID从2开始
        area_id = 2
        station_id = 100
        
        # 添加区域到映射
        for area in areas:
            area_name = area['area_manager']
            dept_map[str(area_id)] = {'name': area_name, 'type': '区域'}
            
            # 添加站点到映射
            for station in stations:
                if station['area_manager'] == area_name:
                    dept_map[str(station_id)] = {'name': station['station_name'], 'type': '配送部门'}
                    station_id += 1
            area_id += 1
        
        # 检查部门是否存在
        if department_id not in dept_map:
            return jsonify({'success': False, 'message': '部门不存在'})
        
        dept_info = dept_map[department_id]
        
        # 构建返回数据
        data = {
            'name': dept_info['name'],
            'type': dept_info['type'],
            'managers': [],
            'delivery_staff': []
        }
        
        # 如果是站点，获取管理人员
        if dept_info['type'] == '配送部门':
            cursor.execute('SELECT id, name, position FROM management_staff WHERE team = %s ORDER BY position', (dept_info['name'],))
            management_staff = cursor.fetchall()
            
            for staff in management_staff:
                data['managers'].append({
                    'id': staff['id'],
                    'name': staff['name'],
                    'phone': '',  # 数据库中没有手机号字段
                    'position': staff['position'],
                    'work_nature': '全职',  # 默认为全职
                    'status': 'approved'  # 默认为已审批
                })
        
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        print(f'数据库错误: {e}')
        return jsonify({'success': False, 'message': '数据库错误'})
    finally:
        cursor.close()
        conn.close()

@department_bp.route('/api/stations', methods=['POST'])
def add_station():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        data = request.json
        station_name = data.get('station_name')
        area_manager = data.get('area_manager')
        
        if not station_name or not area_manager:
            return jsonify({'success': False, 'message': '站点名称和区域经理不能为空'})
        
        # 生成站点ID
        cursor.execute('SELECT MAX(station_id) as max_id FROM stations')
        max_id = cursor.fetchone()['max_id']
        if max_id:
            new_id = f"ST{str(int(max_id[2:]) + 1).zfill(3)}"
        else:
            new_id = "ST001"
        
        # 插入站点数据
        try:
            cursor.execute('INSERT INTO stations (station_id, station_name, area_manager, city_code) VALUES (%s, %s, %s, %s)', 
                          (new_id, station_name, area_manager, 'hangzhou'))
            conn.commit()
            print(f'站点添加成功: {station_name}, ID: {new_id}')
            return jsonify({'success': True, 'message': '站点添加成功'})
        except pymysql.IntegrityError as e:
            print(f'数据库错误: {e}')
            conn.rollback()
            return jsonify({'success': False, 'message': '站点名称已存在'})
    except Exception as e:
        print(f'数据库错误: {e}')
        conn.rollback()
        return jsonify({'success': False, 'message': '数据库错误'})
    finally:
        cursor.close()
        conn.close()

@department_bp.route('/api/stations/<station_id>', methods=['PUT'])
def update_station(station_id):
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        data = request.json
        station_name = data.get('station_name')
        area_manager = data.get('area_manager')
        
        if not station_name or not area_manager:
            return jsonify({'success': False, 'message': '站点名称和区域经理不能为空'})
        
        # 更新站点数据
        cursor.execute('UPDATE stations SET station_name = %s, area_manager = %s WHERE station_id = %s', 
                      (station_name, area_manager, station_id))
        conn.commit()
        
        if cursor.rowcount == 0:
            return jsonify({'success': False, 'message': '站点不存在'})
        
        return jsonify({'success': True, 'message': '站点更新成功'})
    except Exception as e:
        print(f'数据库错误: {e}')
        conn.rollback()
        return jsonify({'success': False, 'message': '数据库错误'})
    finally:
        cursor.close()
        conn.close()

@department_bp.route('/api/stations/<station_id>', methods=['DELETE'])
def delete_station(station_id):
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 检查站点是否存在
        cursor.execute('SELECT * FROM stations WHERE station_id = %s', (station_id,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': '站点不存在'})
        
        # 删除站点
        cursor.execute('DELETE FROM stations WHERE station_id = %s', (station_id,))
        conn.commit()
        
        return jsonify({'success': True, 'message': '站点删除成功'})
    except Exception as e:
        print(f'数据库错误: {e}')
        conn.rollback()
        return jsonify({'success': False, 'message': '数据库错误'})
    finally:
        cursor.close()
        conn.close()

@department_bp.route('/api/management-staff', methods=['POST'])
def add_management_staff():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        data = request.json
        area_manager = data.get('area_manager')
        team = data.get('team')
        name = data.get('name')
        position = data.get('position')
        
        if not area_manager or not team or not name or not position:
            return jsonify({'success': False, 'message': '所有字段不能为空'})
        
        # 插入管理人员数据
        cursor.execute('INSERT INTO management_staff (area_manager, team, name, position) VALUES (%s, %s, %s, %s)', 
                      (area_manager, team, name, position))
        conn.commit()
        
        return jsonify({'success': True, 'message': '管理人员添加成功'})
    except Exception as e:
        print(f'数据库错误: {e}')
        conn.rollback()
        return jsonify({'success': False, 'message': '数据库错误'})
    finally:
        cursor.close()
        conn.close()

@department_bp.route('/api/management-staff/<staff_id>', methods=['PUT'])
def update_management_staff(staff_id):
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        data = request.json
        area_manager = data.get('area_manager')
        team = data.get('team')
        name = data.get('name')
        position = data.get('position')
        
        if not area_manager or not team or not name or not position:
            return jsonify({'success': False, 'message': '所有字段不能为空'})
        
        # 更新管理人员数据
        cursor.execute('UPDATE management_staff SET area_manager = %s, team = %s, name = %s, position = %s WHERE id = %s', 
                      (area_manager, team, name, position, staff_id))
        conn.commit()
        
        if cursor.rowcount == 0:
            return jsonify({'success': False, 'message': '管理人员不存在'})
        
        return jsonify({'success': True, 'message': '管理人员更新成功'})
    except Exception as e:
        print(f'数据库错误: {e}')
        conn.rollback()
        return jsonify({'success': False, 'message': '数据库错误'})
    finally:
        cursor.close()
        conn.close()

@department_bp.route('/api/management-staff/<staff_id>', methods=['DELETE'])
def delete_management_staff(staff_id):
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 检查管理人员是否存在
        cursor.execute('SELECT * FROM management_staff WHERE id = %s', (staff_id,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': '管理人员不存在'})
        
        # 删除管理人员
        cursor.execute('DELETE FROM management_staff WHERE id = %s', (staff_id,))
        conn.commit()
        
        return jsonify({'success': True, 'message': '管理人员删除成功'})
    except Exception as e:
        print(f'数据库错误: {e}')
        conn.rollback()
        return jsonify({'success': False, 'message': '数据库错误'})
    finally:
        cursor.close()
        conn.close()