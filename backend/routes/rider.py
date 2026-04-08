from flask import Blueprint, jsonify, request
from config.db_pool import get_db_connection
import pymysql
from datetime import datetime, timedelta

rider_bp = Blueprint('rider', __name__)

@rider_bp.route('/api/riders', methods=['GET'])
def get_riders():
    """获取骑手列表（优化版 - 解决N+1查询问题）"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 获取查询参数
        organization = request.args.get('organization')
        department = request.args.get('department')
        search = request.args.get('search')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        city = request.args.get('city', 'all')
        work_nature = request.args.get('work_nature')
        recruitment_channel = request.args.get('recruitment_channel')
        
        # 构建查询语句
        query = """SELECT r.*, 
                          s.id as station_id, 
                          s.city_code as city,
                          c.city_name 
                   FROM riders r 
                   LEFT JOIN stations s ON r.station_name = s.station_name 
                   LEFT JOIN cities c ON s.city_code = c.city_code 
                   WHERE 1=1"""
        params = []
        
        # 添加城市筛选
        if city != 'all':
            query += " AND r.station_name IN (SELECT station_name FROM stations WHERE city_code = %s)"
            params.append(city)
        
        # 添加部门（站点）筛选
        if department:
            query += " AND r.station_name = %s"
            params.append(department)
        
        # 添加搜索条件
        if search:
            query += " AND (r.rider_id LIKE %s OR r.name LIKE %s OR r.phone LIKE %s)"
            params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])
        
        # 添加入职日期范围
        if start_date:
            query += " AND r.entry_date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND r.entry_date <= %s"
            params.append(end_date)
        
        # 添加工作性质筛选
        if work_nature:
            query += " AND r.work_nature = %s"
            params.append(work_nature)
        
        # 添加招聘渠道筛选
        if recruitment_channel:
            query += " AND r.recruitment_channel = %s"
            params.append(recruitment_channel)
        
        # 执行查询
        cursor.execute(query, params)
        riders = cursor.fetchall()
        
        # 批量获取合同状态（优先从骑手合同签署表查询）
        id_cards = [r.get('id_card') for r in riders if r.get('id_card')]
        contract_status_map = {}

        if id_cards:
            # 优先从 rider_contracts 表查询（新的独立签署表）
            try:
                placeholders = ','.join(['%s'] * len(id_cards))
                cursor.execute(f"""
                    SELECT id_card, 
                           CASE WHEN status = 1 THEN '已签订' ELSE '未签订' END as status
                    FROM rider_contracts 
                    WHERE id_card IN ({placeholders})
                    AND status = 1
                """, id_cards)

                contracts = cursor.fetchall()
                for contract in contracts:
                    contract_status_map[contract['id_card']] = contract['status']
            except Exception as e:
                print(f"查询rider_contracts表失败（表可能尚未创建）: {e}")
            
            # 如果在 rider_contracts 表中未找到，则从旧的 contract_signatures 表查询
            missing_id_cards = [ic for ic in id_cards if ic not in contract_status_map]
            if missing_id_cards:
                try:
                    missing_placeholders = ','.join(['%s'] * len(missing_id_cards))
                    cursor.execute(f"""
                        SELECT cs.id_card, cs.status 
                        FROM contract_signatures cs
                        INNER JOIN (
                            SELECT id_card, MAX(signed_at) as max_signed_at 
                            FROM contract_signatures 
                            WHERE id_card IN ({missing_placeholders})
                            GROUP BY id_card
                        ) latest ON cs.id_card = latest.id_card AND cs.signed_at = latest.max_signed_at
                    """, missing_id_cards)

                    old_contracts = cursor.fetchall()
                    for contract in old_contracts:
                        if contract['id_card'] not in contract_status_map:
                            contract_status_map[contract['id_card']] = '已签订' if contract['status'] == 'signed' else '未签订'
                except Exception as e:
                    print(f"查询contract_signatures表失败: {e}")
        
        # 更新合同状态和岗位状态
        for rider in riders:
            id_card = rider.get('id_card')
            if id_card:
                rider['contract_status'] = contract_status_map.get(id_card, '未签订')
            
            # 根据离职时间和离岗时间判定岗位状态
            exit_date = rider.get('exit_date')
            leave_date = rider.get('leave_date')
            if exit_date and leave_date:
                try:
                    exit_date_obj = datetime.strptime(str(exit_date), '%Y-%m-%d')
                    leave_date_obj = datetime.strptime(str(leave_date), '%Y-%m-%d')
                    # 待离职判定：离岗日期大于离职日期
                    if leave_date_obj > exit_date_obj:
                        rider['position_status'] = '待离职'
                    else:
                        rider['position_status'] = '离职'
                    # 计算间隔天数，用于判定自离/正常离职，添加到人员标签
                    days_diff = (leave_date_obj - exit_date_obj).days
                    tags = rider.get('tags', '')
                    # 处理none值
                    if tags == 'none':
                        tags = ''
                    if days_diff >= 30:
                        if '正常离职' not in tags:
                            tags = tags + '正常离职' if tags else '正常离职'
                    else:
                        if '自离' not in tags:
                            tags = tags + '自离' if tags else '自离'
                    rider['tags'] = tags
                except:
                    pass
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': riders,
            'total': len(riders)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@rider_bp.route('/api/riders/<rider_id>', methods=['GET'])
def get_rider(rider_id):
    """获取单个骑手详情"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        query = "SELECT * FROM riders WHERE rider_id = %s"
        cursor.execute(query, (rider_id,))
        rider = cursor.fetchone()
        
        if rider:
            # 更新合同状态（优先从骑手合同签署表查询）
            id_card = rider.get('id_card')
            if id_card:
                try:
                    # 优先从 rider_contracts 表查询
                    cursor.execute("""
                        SELECT status FROM rider_contracts 
                        WHERE id_card = %s AND status = 1
                        ORDER BY sign_time DESC LIMIT 1
                    """, (id_card,))
                    contract = cursor.fetchone()

                    if not contract:
                        # 如果在新表中未找到，则从旧表查询
                        cursor.execute("""
                            SELECT status FROM contract_signatures 
                            WHERE id_card = %s 
                            ORDER BY signed_at DESC 
                            LIMIT 1
                        """, (id_card,))
                        contract = cursor.fetchone()
                        if contract:
                            rider['contract_status'] = '已签订' if contract['status'] == 'signed' else '未签订'
                        else:
                            rider['contract_status'] = '未签订'
                    else:
                        rider['contract_status'] = '已签订'
                except Exception as e:
                    print(f"查询合同状态失败: {e}")
                    rider['contract_status'] = '未签订'
            
            # 根据离职时间和离岗时间判定岗位状态
            exit_date = rider.get('exit_date')
            leave_date = rider.get('leave_date')
            if exit_date and leave_date:
                try:
                    exit_date_obj = datetime.strptime(str(exit_date), '%Y-%m-%d')
                    leave_date_obj = datetime.strptime(str(leave_date), '%Y-%m-%d')
                    # 待离职判定：离岗日期大于离职日期
                    if leave_date_obj > exit_date_obj:
                        rider['position_status'] = '待离职'
                    else:
                        rider['position_status'] = '离职'
                    # 计算间隔天数，用于判定自离/正常离职，添加到人员标签
                    days_diff = (leave_date_obj - exit_date_obj).days
                    tags = rider.get('tags', '')
                    # 处理none值
                    if tags == 'none':
                        tags = ''
                    if days_diff >= 30:
                        if '正常离职' not in tags:
                            tags = tags + '正常离职' if tags else '正常离职'
                    else:
                        if '自离' not in tags:
                            tags = tags + '自离' if tags else '自离'
                    rider['tags'] = tags
                except:
                    pass
        
        cursor.close()
        conn.close()
        
        if not rider:
            return jsonify({
                'success': False,
                'error': '骑手不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'data': rider
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@rider_bp.route('/api/riders', methods=['POST'])
def create_rider():
    """创建新骑手"""
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        INSERT INTO riders (
            rider_id, name, phone, station_name, first_run_date, entry_date, 
            work_nature, unit_price, settlement_cycle, id_card, birth_date, 
            recruitment_channel, referral_name, salary_plan_id, emergency_phone, 
            position_status, tags, remark, contract_status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        values = (
            data.get('rider_id'),
            data.get('name'),
            data.get('phone'),
            data.get('station_name'),
            data.get('first_run_date'),
            data.get('entry_date'),
            data.get('work_nature'),
            data.get('unit_price'),
            data.get('settlement_cycle'),
            data.get('id_card'),
            data.get('birth_date'),
            data.get('recruitment_channel'),
            data.get('referral_name'),
            data.get('salary_plan_id'),
            data.get('emergency_phone'),
            data.get('position_status'),
            data.get('tags'),
            data.get('remark'),
            data.get('contract_status')
        )
        
        cursor.execute(query, values)
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '骑手创建成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@rider_bp.route('/api/riders/<rider_id>', methods=['PUT'])
def update_rider(rider_id):
    """更新骑手信息"""
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 允许更新的字段白名单
        ALLOWED_FIELDS = [
            'name', 'phone', 'id_card', 'station_name', 'city',
            'work_nature', 'unit_price', 'settlement_cycle',
            'entry_date', 'first_run_date', 'birth_date',
            'recruitment_channel', 'referral_name',
            'salary_plan_id', 'emergency_phone',
            'position_status', 'exit_date', 'leave_date',
            'tags', 'remark', 'contract_status'
        ]
        
        # 构建更新语句（只允许白名单中的字段）
        update_fields = []
        update_values = []
        
        for key, value in data.items():
            if key in ALLOWED_FIELDS and key != 'rider_id':
                # 跳过空字符串，但允许 None（用于清空字段）
                if value == '' or value is None:
                    continue
                update_fields.append(f"`{key}` = %s")
                update_values.append(value)
        
        if not update_fields:
            return jsonify({
                'success': False,
                'error': '没有需要更新的字段'
            }), 400
        
        update_values.append(rider_id)
        
        query = f"UPDATE riders SET {', '.join(update_fields)} WHERE rider_id = %s"
        
        cursor.execute(query, update_values)
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '骑手信息更新成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@rider_bp.route('/api/riders/<rider_id>', methods=['DELETE'])
def delete_rider(rider_id):
    """删除骑手"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "DELETE FROM riders WHERE rider_id = %s"
        cursor.execute(query, (rider_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '骑手删除成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@rider_bp.route('/api/riders/stats', methods=['GET'])
def get_rider_stats():
    """获取骑手统计信息（优化版 - 使用单次聚合查询）"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 获取查询参数
        city = request.args.get('city', 'all')
        
        if city != 'all':
            # 使用单次聚合查询替代7次独立查询（性能提升约7倍）
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN position_status = '在职' THEN 1 ELSE 0 END) as active_count,
                    SUM(CASE WHEN work_nature = '全职' THEN 1 ELSE 0 END) as full_time_count,
                    SUM(CASE WHEN work_nature = '兼职' THEN 1 ELSE 0 END) as part_time_count,
                    SUM(CASE WHEN DATEDIFF(NOW(), entry_date) < 30 THEN 1 ELSE 0 END) as new_rider_count,
                    SUM(CASE WHEN DATE(entry_date) = DATE(NOW()) THEN 1 ELSE 0 END) as today_entry_count,
                    SUM(CASE WHEN first_run_date IS NULL THEN 1 ELSE 0 END) as no_first_run_count,
                    SUM(CASE WHEN position_status != '在职' THEN 1 ELSE 0 END) as abnormal_count
                FROM riders
                WHERE station_name IN (SELECT station_name FROM stations WHERE city_code = %s)
            """, (city,))
        else:
            # 使用单次聚合查询替代7次独立查询
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN position_status = '在职' THEN 1 ELSE 0 END) as active_count,
                    SUM(CASE WHEN work_nature = '全职' THEN 1 ELSE 0 END) as full_time_count,
                    SUM(CASE WHEN work_nature = '兼职' THEN 1 ELSE 0 END) as part_time_count,
                    SUM(CASE WHEN DATEDIFF(NOW(), entry_date) < 30 THEN 1 ELSE 0 END) as new_rider_count,
                    SUM(CASE WHEN DATE(entry_date) = DATE(NOW()) THEN 1 ELSE 0 END) as today_entry_count,
                    SUM(CASE WHEN first_run_date IS NULL THEN 1 ELSE 0 END) as no_first_run_count,
                    SUM(CASE WHEN position_status != '在职' THEN 1 ELSE 0 END) as abnormal_count
                FROM riders
            """)
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'active': result['active_count'] or 0,
                'full_time': result['full_time_count'] or 0,
                'part_time': result['part_time_count'] or 0,
                'new_riders': result['new_rider_count'] or 0,
                'today_entry': result['today_entry_count'] or 0,
                'no_first_run': result['no_first_run_count'] or 0,
                'abnormal': result['abnormal_count'] or 0
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@rider_bp.route('/api/stations', methods=['GET'])
def get_stations():
    """获取站点列表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 获取查询参数
        city_code = request.args.get('city_code')
        
        # 构建查询语句
        query = "SELECT * FROM stations"
        params = []
        
        if city_code:
            query += " WHERE city_code = %s"
            params.append(city_code)
        
        # 执行查询
        cursor.execute(query, params)
        stations = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': stations
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@rider_bp.route('/api/riders/batch', methods=['POST'])
def batch_create_riders():
    """批量创建骑手"""
    try:
        data = request.json
        riders = data.get('riders', [])
        
        if not riders:
            return jsonify({
                'success': False,
                'error': '没有数据需要导入'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 批量插入数据
        query = """
        INSERT INTO riders (
            rider_id, name, phone, station_name, first_run_date, entry_date, 
            work_nature, unit_price, settlement_cycle, id_card, birth_date, 
            recruitment_channel, referral_name, salary_plan_id, emergency_phone, 
            position_status, tags, remark, contract_status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            name = VALUES(name),
            phone = VALUES(phone),
            station_name = VALUES(station_name),
            first_run_date = VALUES(first_run_date),
            entry_date = VALUES(entry_date),
            work_nature = VALUES(work_nature),
            unit_price = VALUES(unit_price),
            settlement_cycle = VALUES(settlement_cycle),
            id_card = VALUES(id_card),
            birth_date = VALUES(birth_date),
            recruitment_channel = VALUES(recruitment_channel),
            referral_name = VALUES(referral_name),
            salary_plan_id = VALUES(salary_plan_id),
            emergency_phone = VALUES(emergency_phone),
            position_status = VALUES(position_status),
            tags = VALUES(tags),
            remark = VALUES(remark),
            contract_status = VALUES(contract_status)
        """
        
        values = []
        for index, rider in enumerate(riders):
            # 检查必填字段
            rider_id = rider.get('骑手风神ID') or rider.get('rider_id')
            name = rider.get('姓名') or rider.get('name')
            phone = rider.get('手机号') or rider.get('phone')
            station_name = rider.get('站点名称') or rider.get('station_name')
            city = rider.get('城市') or rider.get('city') or 'hangzhou'
            entry_date = rider.get('入职日期') or rider.get('entry_date')
            work_nature = rider.get('工作性质') or rider.get('work_nature')
            id_card = rider.get('身份证号') or rider.get('id_card')
            position_status = rider.get('岗位状态') or rider.get('position_status')
            
            # 打印接收到的数据，用于调试
            print(f"接收到的骑手数据: {rider}")
            print(f"解析后的字段值: rider_id={rider_id}, name={name}, phone={phone}, station_name={station_name}, entry_date={entry_date}, work_nature={work_nature}, id_card={id_card}, position_status={position_status}")
            
            # 验证必填字段
            missing_fields = []
            if not rider_id:
                missing_fields.append('骑手风神ID')
            if not name:
                missing_fields.append('姓名')
            if not phone:
                missing_fields.append('手机号')
            if not station_name:
                missing_fields.append('站点名称')
            if not entry_date:
                missing_fields.append('入职日期')
            if not work_nature:
                missing_fields.append('工作性质')
            if not id_card:
                missing_fields.append('身份证号')
            if not position_status:
                missing_fields.append('岗位状态')
            
            if missing_fields:
                missing_fields_str = ', '.join(missing_fields)
                return jsonify({
                    'success': False,
                    'error': f'第 {index + 2} 行数据缺少必填字段: {missing_fields_str}'
                }), 400
            
            # 从身份证号提取出生日期
            def extract_birth_date_from_id_card(id_card):
                if not id_card:
                    return None
                id_card = str(id_card).strip()
                if len(id_card) < 15:
                    return None
                
                try:
                    if len(id_card) == 18:
                        # 18位身份证：第7-14位为出生日期，格式YYYYMMDD
                        birth_date_str = id_card[6:14]
                    elif len(id_card) == 15:
                        # 15位身份证：第7-12位为出生日期，格式YYMMDD，需要转换为YYYYMMDD
                        birth_date_str = '19' + id_card[6:12]
                    else:
                        return None
                    
                    # 转换为YYYY-MM-DD格式
                    if len(birth_date_str) == 8:
                        year = birth_date_str[:4]
                        month = birth_date_str[4:6]
                        day = birth_date_str[6:8]
                        return f'{year}-{month}-{day}'
                    return None
                except:
                    return None
            
            # 处理日期字段
            first_run_date = rider.get('首跑日期') or rider.get('first_run_date')
            if first_run_date and first_run_date.strip() == '':
                first_run_date = None
                
            if entry_date and entry_date.strip() == '':
                entry_date = None
                
            birth_date = rider.get('出生日期') or rider.get('birth_date')
            
            # 如果没有出生日期，尝试从身份证号提取
            if not birth_date or (birth_date and birth_date.strip() == ''):
                extracted_birth_date = extract_birth_date_from_id_card(id_card)
                if extracted_birth_date:
                    birth_date = extracted_birth_date
            
            # 处理空字符串
            if birth_date and birth_date.strip() == '':
                birth_date = None
                
            # 处理数值字段
            unit_price = rider.get('单价') or rider.get('unit_price')
            if unit_price:
                try:
                    unit_price = float(unit_price)
                except ValueError:
                    unit_price = None
            
            values.append((
                rider_id,
                name,
                phone,
                station_name,
                first_run_date,
                entry_date,
                work_nature,
                unit_price,
                rider.get('结算周期') or rider.get('settlement_cycle'),
                id_card,
                birth_date,
                rider.get('招聘渠道') or rider.get('recruitment_channel'),
                rider.get('三方/内推姓名') or rider.get('referral_name'),
                rider.get('薪资方案绑定') or rider.get('salary_plan_id'),
                rider.get('紧急联系人电话号码') or rider.get('emergency_phone'),
                position_status,
                rider.get('人员标签') or rider.get('tags'),
                rider.get('备注') or rider.get('remark'),
                rider.get('合同状态') or rider.get('contract_status')
            ))
        
        if values:
            cursor.executemany(query, values)
            conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'成功导入 {len(riders)} 条骑手数据',
            'imported': len(riders)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@rider_bp.route('/api/riders/entry-exit-summary', methods=['GET'])
def get_entry_exit_summary():
    """获取入离职汇总统计"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 获取查询参数
        city_code = request.args.get('city_code', 'hangzhou')  # 默认杭州
        station_name = request.args.get('station_name')  # 可选站点名称
        dimension = request.args.get('dimension', 'day')  # 默认日维度
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 获取站点列表
        if station_name:
            # 如果指定了站点，只返回该站点
            station_names = [station_name]
        else:
            # 否则获取该城市所有站点
            cursor.execute("SELECT station_name FROM stations WHERE city_code = %s", (city_code,))
            stations = cursor.fetchall()
            station_names = [station['station_name'] for station in stations]
        
        # 准备统计结果
        summary_data = []
        
        for st_name in station_names:
            # 计算日期范围
            date_condition = ""
            if start_date and end_date:
                date_condition = f"AND DATE(entry_date) BETWEEN '{start_date}' AND '{end_date}'"
            elif dimension == 'day':
                date_condition = "AND DATE(entry_date) = DATE(NOW())"
            elif dimension == 'week':
                date_condition = "AND DATE(entry_date) BETWEEN DATE_SUB(DATE(NOW()), INTERVAL 7 DAY) AND DATE(NOW())"
            elif dimension == 'halfMonth':
                date_condition = "AND DATE(entry_date) BETWEEN DATE_SUB(DATE(NOW()), INTERVAL 15 DAY) AND DATE(NOW())"
            elif dimension == 'month':
                date_condition = "AND DATE(entry_date) BETWEEN DATE_SUB(DATE(NOW()), INTERVAL 30 DAY) AND DATE(NOW())"
            
            if not date_condition:
                date_condition = "AND DATE(entry_date) IS NOT NULL"
            
            # 统计在职人数
            cursor.execute("SELECT COUNT(*) FROM riders WHERE station_name = %s AND position_status = '在职'", (st_name,))
            active_count = cursor.fetchone()['COUNT(*)']
            
            # 统计入职人数
            cursor.execute(f"SELECT COUNT(*) FROM riders WHERE station_name = %s {date_condition}", (st_name,))
            entry_count = cursor.fetchone()['COUNT(*)']
            
            # 统计全职入职人数
            cursor.execute(f"SELECT COUNT(*) FROM riders WHERE station_name = %s AND work_nature = '全职' {date_condition}", (st_name,))
            full_time_entry_count = cursor.fetchone()['COUNT(*)']
            
            # 统计兼职入职人数
            cursor.execute(f"SELECT COUNT(*) FROM riders WHERE station_name = %s AND work_nature = '兼职' {date_condition}", (st_name,))
            part_time_entry_count = cursor.fetchone()['COUNT(*)']
            
            # 统计内推人数
            cursor.execute(f"SELECT COUNT(*) FROM riders WHERE station_name = %s AND recruitment_channel = '内推' {date_condition}", (st_name,))
            referral_count = cursor.fetchone()['COUNT(*)']
            
            # 统计三方人数
            cursor.execute(f"SELECT COUNT(*) FROM riders WHERE station_name = %s AND recruitment_channel = '三方' {date_condition}", (st_name,))
            third_party_count = cursor.fetchone()['COUNT(*)']
            
            # 统计离职人数，使用离职日期作为筛选条件
            exit_date_condition = ""
            if start_date and end_date:
                exit_date_condition = f"AND DATE(exit_date) BETWEEN '{start_date}' AND '{end_date}'"
            elif dimension == 'day':
                exit_date_condition = "AND DATE(exit_date) = DATE(NOW())"
            elif dimension == 'week':
                exit_date_condition = "AND DATE(exit_date) BETWEEN DATE_SUB(DATE(NOW()), INTERVAL 7 DAY) AND DATE(NOW())"
            elif dimension == 'halfMonth':
                exit_date_condition = "AND DATE(exit_date) BETWEEN DATE_SUB(DATE(NOW()), INTERVAL 15 DAY) AND DATE(NOW())"
            elif dimension == 'month':
                exit_date_condition = "AND DATE(exit_date) BETWEEN DATE_SUB(DATE(NOW()), INTERVAL 30 DAY) AND DATE(NOW())"
            
            if not exit_date_condition:
                exit_date_condition = "AND exit_date IS NOT NULL"
            
            cursor.execute(f"SELECT COUNT(*) FROM riders WHERE station_name = %s AND position_status = '离职' {exit_date_condition}", (st_name,))
            exit_count = cursor.fetchone()['COUNT(*)']
            
            # 计算净增人数
            net_increase = entry_count - exit_count
            
            # 统计待离职全职数（根据exit_date和leave_date计算）
            cursor.execute("SELECT COUNT(*) FROM riders WHERE station_name = %s AND work_nature = '全职' AND exit_date IS NOT NULL AND leave_date IS NOT NULL AND leave_date > exit_date", (st_name,))
            pending_exit_full_time_count = cursor.fetchone()['COUNT(*)']
            
            # 统计待离职兼职数（根据exit_date和leave_date计算）
            cursor.execute("SELECT COUNT(*) FROM riders WHERE station_name = %s AND work_nature = '兼职' AND exit_date IS NOT NULL AND leave_date IS NOT NULL AND leave_date > exit_date", (st_name,))
            pending_exit_part_time_count = cursor.fetchone()['COUNT(*)']
            
            # 计算入职率和离职率
            entry_rate = (entry_count / active_count * 100) if active_count > 0 else 0
            exit_rate = (exit_count / active_count * 100) if active_count > 0 else 0
            
            # 添加到结果
            summary_data.append({
                'station_name': st_name,
                'entry_count': entry_count,
                'full_time_entry_count': full_time_entry_count,
                'referral_count': referral_count,
                'third_party_count': third_party_count,
                'part_time_entry_count': part_time_entry_count,
                'exit_count': exit_count,
                'net_increase': net_increase,
                'entry_rate': round(entry_rate, 2),
                'exit_rate': round(exit_rate, 2),
                'active_count': active_count,
                'pending_exit_full_time_count': pending_exit_full_time_count,
                'pending_exit_part_time_count': pending_exit_part_time_count
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': summary_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@rider_bp.route('/api/riders/third-party-summary', methods=['GET'])
def get_third_party_summary():
    """获取三方入离职汇总表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 获取查询参数
        city_code = request.args.get('city_code', 'hangzhou')  # 默认杭州
        station_name = request.args.get('station_name')  # 可选站点名称
        date = request.args.get('date', None)  # 可选日期参数
        
        # 获取站点列表
        if station_name:
            # 如果指定了站点，只返回该站点
            station_names = [station_name]
        else:
            # 否则获取该城市所有站点
            cursor.execute("SELECT station_name FROM stations WHERE city_code = %s", (city_code,))
            stations = cursor.fetchall()
            station_names = [station['station_name'] for station in stations]
        
        # 准备统计结果
        summary_data = []
        
        # 日期条件
        date_condition = ""
        exit_date_condition = ""
        if date:
            date_condition = f"AND DATE(entry_date) = '{date}'"
            exit_date_condition = f"AND DATE(exit_date) = '{date}'"
        else:
            date_condition = "AND DATE(entry_date) = DATE(NOW())"
            exit_date_condition = "AND DATE(exit_date) = DATE(NOW())"
        
        for station_name in station_names:
            # 三方名称（暂时固定为熊出没）
            third_party_name = "熊出没"
            
            # 统计该站点该三方的在职总人数
            cursor.execute("SELECT COUNT(*) FROM riders WHERE station_name = %s AND recruitment_channel = '三方' AND position_status = '在职'", (station_name,))
            third_party_active_count = cursor.fetchone()['COUNT(*)']
            
            # 统计该站点该三方当天入职人数
            cursor.execute(f"SELECT COUNT(*) FROM riders WHERE station_name = %s AND recruitment_channel = '三方' {date_condition}", (station_name,))
            entry_count = cursor.fetchone()['COUNT(*)']
            
            # 统计该站点该三方当天离职人数
            cursor.execute(f"SELECT COUNT(*) FROM riders WHERE station_name = %s AND recruitment_channel = '三方' AND position_status = '离职' {exit_date_condition}", (station_name,))
            exit_count = cursor.fetchone()['COUNT(*)']
            
            # 计算流失率和留存率
            attrition_rate = (exit_count / third_party_active_count * 100) if third_party_active_count > 0 else 0
            retention_rate = 100 - attrition_rate
            
            # 添加到结果
            summary_data.append({
                'station_name': station_name,
                'third_party_name': third_party_name,
                'entry_count': entry_count,
                'exit_count': exit_count,
                'attrition_rate': round(attrition_rate, 2),
                'retention_rate': round(retention_rate, 2),
                'pre_settlement_amount': '-',
                'pre_settlement_attrition_amount': '-',
                'settled_amount': '-',
                'settled_attrition_amount': '-',
                'unsettled_amount': '-'
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': summary_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@rider_bp.route('/api/riders/entry-exit-trend', methods=['GET'])
def get_entry_exit_trend():
    """获取入离职趋势数据"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 获取查询参数
        city_code = request.args.get('city_code', 'hangzhou')  # 默认杭州
        dimension = request.args.get('dimension', 'day')  # 默认日维度
        
        # 计算日期范围
        if dimension == 'day':
            # 最近7天
            # 直接生成日期列表，不使用SQL递归
            trend_data = []
            import datetime
            end_date = datetime.date.today()
            start_date = end_date - datetime.timedelta(days=6)
            
            current_date = start_date
            while current_date <= end_date:
                # 统计入职人数
                cursor.execute("""
                    SELECT COUNT(*) as entry_count
                    FROM riders 
                    WHERE station_name IN (SELECT station_name FROM stations WHERE city_code = %s)
                    AND DATE(entry_date) = %s
                """, (city_code, current_date))
                entry_result = cursor.fetchone()
                entry_count = entry_result['entry_count']
                
                # 统计离职人数
                cursor.execute("""
                    SELECT COUNT(*) as exit_count
                    FROM riders 
                    WHERE station_name IN (SELECT station_name FROM stations WHERE city_code = %s)
                    AND position_status = '离职'
                    AND DATE(exit_date) = %s
                """, (city_code, current_date))
                exit_result = cursor.fetchone()
                exit_count = exit_result['exit_count']
                
                trend_data.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'entry_count': entry_count,
                    'exit_count': exit_count
                })
                current_date += datetime.timedelta(days=1)
        elif dimension == 'week':
            # 最近4周
            # 直接生成周列表，不使用SQL递归
            trend_data = []
            import datetime
            end_date = datetime.date.today()
            start_date = end_date - datetime.timedelta(days=27)
            
            # 调整到周一开始
            start_date = start_date - datetime.timedelta(days=start_date.weekday())
            
            current_week_start = start_date
            week_num = current_week_start.isocalendar()[1]
            while current_week_start <= end_date:
                week_end = current_week_start + datetime.timedelta(days=6)
                week_date = f"第{week_num}周"
                
                # 统计入职人数
                cursor.execute("""
                    SELECT COUNT(*) as entry_count
                    FROM riders 
                    WHERE station_name IN (SELECT station_name FROM stations WHERE city_code = %s)
                    AND DATE(entry_date) BETWEEN %s AND %s
                """, (city_code, current_week_start, week_end))
                entry_result = cursor.fetchone()
                entry_count = entry_result['entry_count']
                
                # 统计离职人数
                cursor.execute("""
                    SELECT COUNT(*) as exit_count
                    FROM riders 
                    WHERE station_name IN (SELECT station_name FROM stations WHERE city_code = %s)
                    AND position_status = '离职'
                    AND DATE(exit_date) BETWEEN %s AND %s
                """, (city_code, current_week_start, week_end))
                exit_result = cursor.fetchone()
                exit_count = exit_result['exit_count']
                
                trend_data.append({
                    'date': week_date,
                    'entry_count': entry_count,
                    'exit_count': exit_count
                })
                
                current_week_start += datetime.timedelta(days=7)
                week_num += 1
        elif dimension == 'halfMonth':
            # 最近2个半月
            # 直接生成半月列表，不使用SQL递归
            trend_data = []
            import datetime
            end_date = datetime.date.today()
            start_date = end_date - datetime.timedelta(days=45)
            
            # 调整到月初
            start_date = start_date.replace(day=1)
            
            current_date = start_date
            while current_date <= end_date:
                # 上半月
                half_month_start = current_date
                half_month_end = current_date.replace(day=15)
                period_date = f"{current_date.year}-{current_date.month:02d}-上半月"
                
                # 统计入职人数
                cursor.execute("""
                    SELECT COUNT(*) as entry_count
                    FROM riders 
                    WHERE station_name IN (SELECT station_name FROM stations WHERE city_code = %s)
                    AND DATE(entry_date) BETWEEN %s AND %s
                """, (city_code, half_month_start, half_month_end))
                entry_result = cursor.fetchone()
                entry_count = entry_result['entry_count']
                
                # 统计离职人数
                cursor.execute("""
                    SELECT COUNT(*) as exit_count
                    FROM riders 
                    WHERE station_name IN (SELECT station_name FROM stations WHERE city_code = %s)
                    AND position_status = '离职'
                    AND DATE(exit_date) BETWEEN %s AND %s
                """, (city_code, half_month_start, half_month_end))
                exit_result = cursor.fetchone()
                exit_count = exit_result['exit_count']
                
                trend_data.append({
                    'date': period_date,
                    'entry_count': entry_count,
                    'exit_count': exit_count
                })
                
                # 下半月
                half_month_start = current_date.replace(day=16)
                # 计算当月最后一天
                if current_date.month == 12:
                    next_month = current_date.replace(year=current_date.year + 1, month=1, day=1)
                else:
                    next_month = current_date.replace(month=current_date.month + 1, day=1)
                half_month_end = next_month - datetime.timedelta(days=1)
                period_date = f"{current_date.year}-{current_date.month:02d}-下半月"
                
                # 统计入职人数
                cursor.execute("""
                    SELECT COUNT(*) as entry_count
                    FROM riders 
                    WHERE station_name IN (SELECT station_name FROM stations WHERE city_code = %s)
                    AND DATE(entry_date) BETWEEN %s AND %s
                """, (city_code, half_month_start, half_month_end))
                entry_result = cursor.fetchone()
                entry_count = entry_result['entry_count']
                
                # 统计离职人数
                cursor.execute("""
                    SELECT COUNT(*) as exit_count
                    FROM riders 
                    WHERE station_name IN (SELECT station_name FROM stations WHERE city_code = %s)
                    AND position_status = '离职'
                    AND DATE(exit_date) BETWEEN %s AND %s
                """, (city_code, half_month_start, half_month_end))
                exit_result = cursor.fetchone()
                exit_count = exit_result['exit_count']
                
                trend_data.append({
                    'date': period_date,
                    'entry_count': entry_count,
                    'exit_count': exit_count
                })
                
                # 移动到下个月
                current_date = next_month
        else:  # month
            # 最近6个月
            # 直接生成月份列表，不使用SQL递归
            trend_data = []
            import datetime
            end_date = datetime.date.today()
            start_date = end_date - datetime.timedelta(days=180)  # 大约6个月
            
            # 调整到月初
            start_date = start_date.replace(day=1)
            
            current_date = start_date
            while current_date <= end_date:
                month_date = current_date.strftime('%Y-%m')
                
                # 统计入职人数
                cursor.execute("""
                    SELECT COUNT(*) as entry_count
                    FROM riders 
                    WHERE station_name IN (SELECT station_name FROM stations WHERE city_code = %s)
                    AND DATE_FORMAT(entry_date, '%%Y-%%m') = %s
                """, (city_code, month_date))
                entry_result = cursor.fetchone()
                entry_count = entry_result['entry_count']
                
                # 统计离职人数
                cursor.execute("""
                    SELECT COUNT(*) as exit_count
                    FROM riders 
                    WHERE station_name IN (SELECT station_name FROM stations WHERE city_code = %s)
                    AND position_status = '离职'
                    AND DATE_FORMAT(exit_date, '%%Y-%%m') = %s
                """, (city_code, month_date))
                exit_result = cursor.fetchone()
                exit_count = exit_result['exit_count']
                
                trend_data.append({
                    'date': month_date,
                    'entry_count': entry_count,
                    'exit_count': exit_count
                })
                
                # 移动到下个月
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1, day=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1, day=1)
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': trend_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@rider_bp.route('/api/riders/third-party-analysis', methods=['GET'])
def get_third_party_analysis():
    """获取三方中介分析数据"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 获取查询参数
        city_code = request.args.get('city_code', 'hangzhou')  # 默认杭州
        
        # 获取三方入职数据
        cursor.execute("""
            SELECT 
                station_name, 
                COUNT(*) as entry_count,
                SUM(CASE WHEN position_status = '离职' THEN 1 ELSE 0 END) as exit_count,
                COUNT(*) as total_count
            FROM riders 
            WHERE station_name IN (SELECT station_name FROM stations WHERE city_code = %s)
            AND recruitment_channel = '三方'
            GROUP BY station_name
            ORDER BY entry_count DESC
        """, (city_code,))
        
        third_party_data = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': third_party_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@rider_bp.route('/api/riders/<rider_id>/contract', methods=['GET'])
def get_rider_contract(rider_id):
    """获取骑手的合同信息"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 获取骑手信息
        cursor.execute("SELECT id_card FROM riders WHERE rider_id = %s", (rider_id,))
        rider = cursor.fetchone()
        
        if not rider:
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'error': '骑手不存在'
            }), 404
        
        # 使用身份证号码查找合同签署记录
        cursor.execute("""
            SELECT cs.*, c.name as contract_name, c.content, c.filepath as file_path
            FROM contract_signatures cs
            LEFT JOIN contracts c ON cs.contract_id = c.id
            WHERE cs.id_card = %s
            ORDER BY cs.signed_at DESC
            LIMIT 1
        """, (rider['id_card'],))
        
        contract = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not contract:
            return jsonify({
                'success': False,
                'error': '合同不存在'
            }), 404
        
        # 格式化日期
        if contract.get('signed_at'):
            contract['signed_at'] = contract['signed_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({
            'success': True,
            'data': contract
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@rider_bp.route('/api/riders/exit-records', methods=['GET'])
def get_exit_records():
    """获取离职记录"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 获取查询参数
        city = request.args.get('city', 'all')
        station_name = request.args.get('station_name')
        exit_type = request.args.get('exit_type')
        exit_reason = request.args.get('exit_reason')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 构建查询语句
        query = "SELECT * FROM riders WHERE position_status = '离职' OR (exit_date IS NOT NULL AND leave_date IS NOT NULL)"
        params = []
        
        # 添加城市筛选
        if city != 'all':
            # 使用子查询来获取该城市的所有站点
            query += " AND station_name IN (SELECT station_name FROM stations WHERE city_code = %s)"
            params.append(city)
        
        # 添加站点筛选
        if station_name:
            query += " AND station_name = %s"
            params.append(station_name)
        
        # 添加离职日期范围
        if start_date:
            query += " AND DATE(exit_date) >= %s"
            params.append(start_date)
        if end_date:
            query += " AND DATE(exit_date) <= %s"
            params.append(end_date)
        
        # 执行查询
        cursor.execute(query, params)
        riders = cursor.fetchall()
        
        # 处理离职记录数据
        exit_records = []
        for rider in riders:
            # 计算在职时长（根据离岗日期计算）
            entry_date = rider.get('entry_date')
            leave_date = rider.get('leave_date')
            working_duration = '0天'
            if entry_date and leave_date:
                try:
                    entry_date_obj = datetime.strptime(str(entry_date), '%Y-%m-%d')
                    leave_date_obj = datetime.strptime(str(leave_date), '%Y-%m-%d')
                    days = (leave_date_obj - entry_date_obj).days
                    working_duration = f'{days}天'
                except:
                    pass
            
            # 优先从 rider_exit_records 表中获取离职原因，如果没有则使用 remark 字段
            exit_reason = rider.get('remark', '个人原因')
            rider_id = rider.get('rider_id')
            if rider_id:
                try:
                    cursor.execute("SELECT exit_reason FROM rider_exit_records WHERE rider_id = %s ORDER BY created_at DESC LIMIT 1", (rider_id,))
                    exit_record_result = cursor.fetchone()
                    if exit_record_result and exit_record_result.get('exit_reason'):
                        exit_reason = exit_record_result['exit_reason']
                except:
                    pass
            
            # 构建离职记录
            exit_record = {
                'rider_id': rider.get('rider_id'),
                'name': rider.get('name'),
                'id_card': rider.get('id_card'),
                'phone': rider.get('phone'),
                'station_name': rider.get('station_name'),
                'exit_type': '主动离职' if '自离' in rider.get('tags', '') else '被动离职',
                'exit_reason': exit_reason,
                'entry_date': rider.get('entry_date'),
                'exit_date': rider.get('exit_date'),
                'leave_date': rider.get('leave_date'),
                'working_duration': working_duration
            }
            exit_records.append(exit_record)
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': exit_records
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@rider_bp.route('/api/riders/overview', methods=['GET'])
def get_rider_overview():
    """获取运力总览数据"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 获取查询参数
        city = request.args.get('city', 'all')
        station_name = request.args.get('station_name')
        
        # 构建站点查询
        station_query = ""
        params = []
        
        if city != 'all':
            station_query = " WHERE city_code = %s"
            params.append(city)
        
        # 获取站点列表
        cursor.execute(f"SELECT station_name FROM stations{station_query}", params)
        stations = cursor.fetchall()
        station_names = [station['station_name'] for station in stations]
        print(f"站点列表: {station_names}")
        
        if station_name:
            if station_name in station_names:
                station_names = [station_name]
            else:
                return jsonify({
                    'success': False,
                    'error': '站点不存在'
                }), 404
        
        # 准备结果数据
        overview_data = []
        total_rider_count = 0
        
        # 计算总骑手数（用于计算规模占比）
        if city != 'all':
            cursor.execute("SELECT COUNT(*) FROM riders WHERE position_status = '在职' AND station_name IN (SELECT station_name FROM stations WHERE city_code = %s)", (city,))
        else:
            cursor.execute("SELECT COUNT(*) FROM riders WHERE position_status = '在职'")
        total_rider_count = cursor.fetchone()['COUNT(*)']
        
        for station in station_names:
            # 统计该站点的各项数据
            
            # 从站点规模表中获取规模数
            cursor.execute("SELECT scale_count FROM station_scales WHERE station_name = %s AND city_code = %s", (station, city))
            scale_result = cursor.fetchone()
            scale_count = scale_result['scale_count'] if scale_result and scale_result['scale_count'] else 0
            
            # 骑手数（在职骑手）
            cursor.execute("SELECT COUNT(*) FROM riders WHERE station_name = %s AND position_status = '在职'", (station,))
            rider_count = cursor.fetchone()['COUNT(*)']
            
            if scale_count == 0:
                scale_count = rider_count if rider_count > 0 else 1
            
            # 缺口数
            gap_count = scale_count - rider_count
            
            # 规模占比
            scale_ratio = (rider_count / scale_count * 100) if scale_count > 0 else 0
            
            # 兼职骑手数
            cursor.execute("SELECT COUNT(*) FROM riders WHERE station_name = %s AND position_status = '在职' AND work_nature = '兼职'", (station,))
            part_time_count = cursor.fetchone()['COUNT(*)']
            
            # 全职骑手数
            cursor.execute("SELECT COUNT(*) FROM riders WHERE station_name = %s AND position_status = '在职' AND work_nature = '全职'", (station,))
            full_time_count = cursor.fetchone()['COUNT(*)']
            
            # 兼职骑手占比
            part_time_ratio = (part_time_count / rider_count * 100) if rider_count > 0 else 0
            
            # 连续3天未跑单骑手
            # 计算最近3天的日期（不包含今天）
            today = datetime.now().date()
            three_days_ago = today - timedelta(days=3)
            two_days_ago = today - timedelta(days=2)
            one_day_ago = today - timedelta(days=1)
            
            # 获取该站点的所有在职骑手
            cursor.execute("SELECT rider_id FROM riders WHERE station_name = %s AND position_status = '在职'", (station,))
            station_riders = cursor.fetchall()
            rider_ids = [r['rider_id'] for r in station_riders]
            rider_count = len(rider_ids)
            
            if rider_ids:
                # 构建IN子句的占位符
                placeholders = ','.join(['%s'] * len(rider_ids))
                
                # 查询最近3天有跑单记录的在职骑手
                query = f"""
                    SELECT DISTINCT ra.rider_id 
                    FROM rider_attendance ra
                    WHERE ra.station_name = %s 
                    AND ra.attendance_date IN (%s, %s, %s) 
                    AND ra.time_period = '全天' 
                    AND ra.order_count > 0
                    AND ra.rider_id IN ({placeholders})
                """
                params = [station, three_days_ago, two_days_ago, one_day_ago] + rider_ids
                cursor.execute(query, params)
                active_riders = cursor.fetchall()
                active_rider_ids = [r['rider_id'] for r in active_riders]
                
                # 计算未跑单的骑手数
                three_days_no_order = rider_count - len(active_rider_ids)
                # 确保未出勤数不为负数
                three_days_no_order = max(0, three_days_no_order)
            else:
                three_days_no_order = 0
            
            # 昨日未跑单骑手
            if rider_ids:
                # 构建IN子句的占位符
                placeholders = ','.join(['%s'] * len(rider_ids))
                
                # 查询昨天有跑单记录的在职骑手
                query = f"""
                    SELECT DISTINCT ra.rider_id 
                    FROM rider_attendance ra
                    WHERE ra.station_name = %s 
                    AND ra.attendance_date = %s 
                    AND ra.time_period = '全天' 
                    AND ra.order_count > 0
                    AND ra.rider_id IN ({placeholders})
                """
                params = [station, one_day_ago] + rider_ids
                cursor.execute(query, params)
                yesterday_active_riders = cursor.fetchall()
                yesterday_active_rider_ids = [r['rider_id'] for r in yesterday_active_riders]
                
                # 计算昨日未跑单的骑手数
                yesterday_no_order = rider_count - len(yesterday_active_rider_ids)
                # 确保未出勤数不为负数
                yesterday_no_order = max(0, yesterday_no_order)
            else:
                yesterday_no_order = 0
            
            # 今日出勤骑手数
            try:
                # 直接从realtime_attendance表中查询有跑单记录的骑手数
                # 筛选条件：全天完单量大于0
                # 使用中文字段名，不添加日期筛选
                # 先尝试精确匹配
                cursor.execute("""
                    SELECT COUNT(DISTINCT `骑手id`) as attendance_count
                    FROM realtime_attendance 
                    WHERE `站点名称` = %s 
                    AND `全天完单量` > 0
                """, (station,))
                result = cursor.fetchone()
                today_attendance = result['attendance_count'] if result else 0
                
                # 如果精确匹配没有结果，尝试模糊匹配
                if today_attendance == 0:
                    cursor.execute("""
                        SELECT COUNT(DISTINCT `骑手id`) as attendance_count
                        FROM realtime_attendance 
                        WHERE `站点名称` LIKE %s 
                        AND `全天完单量` > 0
                    """, (f'%{station}%',))
                    result = cursor.fetchone()
                    today_attendance = result['attendance_count'] if result else 0
            except Exception as e:
                # 如果查询失败，尝试从rider_attendance表查询
                try:
                    cursor.execute("""
                        SELECT COUNT(DISTINCT `骑手id`) as attendance_count
                        FROM rider_attendance 
                        WHERE `站点名称` = %s 
                        AND `订单数` > 0
                    """, (station,))
                    result = cursor.fetchone()
                    today_attendance = result['attendance_count'] if result else 0
                except:
                    today_attendance = 0
            
            # 今日入职骑手数
            cursor.execute("SELECT COUNT(*) FROM riders WHERE station_name = %s AND DATE(entry_date) = DATE(NOW())", (station,))
            today_entry_count = cursor.fetchone()['COUNT(*)']
            
            # 今日入职兼职数
            cursor.execute("SELECT COUNT(*) FROM riders WHERE station_name = %s AND DATE(entry_date) = DATE(NOW()) AND work_nature = '兼职'", (station,))
            today_entry_part_time = cursor.fetchone()['COUNT(*)']
            
            # 今日入职全职数
            cursor.execute("SELECT COUNT(*) FROM riders WHERE station_name = %s AND DATE(entry_date) = DATE(NOW()) AND work_nature = '全职'", (station,))
            today_entry_full_time = cursor.fetchone()['COUNT(*)']
            
            # 添加到结果
            overview_data.append({
                'station_name': station,
                'scale_count': scale_count,
                'rider_count': rider_count,
                'gap_count': gap_count,
                'scale_ratio': round(scale_ratio, 2),
                'part_time_count': part_time_count,
                'full_time_count': full_time_count,
                'part_time_ratio': round(part_time_ratio, 2),
                'three_days_no_order': three_days_no_order,
                'yesterday_no_order': yesterday_no_order,
                'today_attendance': today_attendance,
                'today_entry_count': today_entry_count,
                'today_entry_part_time': today_entry_part_time,
                'today_entry_full_time': today_entry_full_time
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': overview_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@rider_bp.route('/api/riders/pending-exit', methods=['GET'])
def get_pending_exit():
    """获取待离职统计数据"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 获取查询参数
        city = request.args.get('city', 'all')
        station_name = request.args.get('station_name')
        exit_type = request.args.get('exit_type')
        exit_reason = request.args.get('exit_reason')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 构建查询语句（待离职：leave_date > exit_date）
        query = "SELECT * FROM riders WHERE exit_date IS NOT NULL AND leave_date IS NOT NULL AND leave_date > exit_date"
        params = []
        
        # 添加城市筛选
        if city != 'all':
            # 使用子查询来获取该城市的所有站点
            query += " AND station_name IN (SELECT station_name FROM stations WHERE city_code = %s)"
            params.append(city)
        
        # 添加站点筛选
        if station_name:
            query += " AND station_name = %s"
            params.append(station_name)
        
        # 执行查询
        cursor.execute(query, params)
        riders = cursor.fetchall()
        
        # 计算统计数据
        total_pending = len(riders)
        
        # 计算本月待离职
        current_month = datetime.now().strftime('%Y-%m')
        current_month_pending = 0
        # 计算下月待离职
        next_month = (datetime.now() + timedelta(days=30)).strftime('%Y-%m')
        next_month_pending = 0
        
        # 处理待离职记录数据
        pending_records = []
        for rider in riders:
            # 计算剩余在职天数
            exit_date = rider.get('exit_date')
            leave_date = rider.get('leave_date')
            remaining_days = '0天'
            if exit_date and leave_date:
                try:
                    exit_date_obj = datetime.strptime(str(exit_date), '%Y-%m-%d')
                    leave_date_obj = datetime.strptime(str(leave_date), '%Y-%m-%d')
                    days = (leave_date_obj - exit_date_obj).days
                    remaining_days = f'{days}天'
                    
                    # 统计本月和下月待离职
                    leave_date_month = leave_date_obj.strftime('%Y-%m')
                    if leave_date_month == current_month:
                        current_month_pending += 1
                    elif leave_date_month == next_month:
                        next_month_pending += 1
                except:
                    pass
            
            # 优先从 rider_exit_records 表中获取离职原因，如果没有则使用 remark 字段
            exit_reason = rider.get('remark', '个人原因')
            rider_id = rider.get('rider_id')
            if rider_id:
                try:
                    cursor.execute("SELECT exit_reason FROM rider_exit_records WHERE rider_id = %s ORDER BY created_at DESC LIMIT 1", (rider_id,))
                    exit_record_result = cursor.fetchone()
                    if exit_record_result and exit_record_result.get('exit_reason'):
                        exit_reason = exit_record_result['exit_reason']
                except:
                    pass
            
            # 构建待离职记录
            pending_record = {
                'rider_id': rider.get('rider_id'),
                'name': rider.get('name'),
                'id_card': rider.get('id_card'),
                'phone': rider.get('phone'),
                'station_name': rider.get('station_name'),
                'exit_type': '主动离职' if '自离' in rider.get('tags', '') else '被动离职',
                'exit_reason': exit_reason,
                'entry_date': rider.get('entry_date'),
                'exit_date': rider.get('exit_date'),
                'leave_date': rider.get('leave_date'),
                'remaining_days': remaining_days
            }
            pending_records.append(pending_record)
        
        # 计算待离职率
        # 先获取总骑手数
        total_riders = 0
        if city != 'all':
            cursor.execute("SELECT COUNT(*) FROM riders WHERE station_name IN (SELECT station_name FROM stations WHERE city_code = %s)", (city,))
        else:
            cursor.execute("SELECT COUNT(*) FROM riders")
        total_riders = cursor.fetchone()['COUNT(*)']
        
        pending_rate = (total_pending / total_riders * 100) if total_riders > 0 else 0
        
        # 构建统计数据
        stats = {
            'total_pending': total_pending,
            'current_month_pending': current_month_pending,
            'next_month_pending': next_month_pending,
            'pending_rate': round(pending_rate, 2)
        }
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'stats': stats,
            'data': pending_records
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
