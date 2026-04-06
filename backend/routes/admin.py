from flask import Blueprint, jsonify, request
import pymysql
from datetime import datetime
from config.db_pool import get_db_connection

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/roster', methods=['GET'])
def get_admin_roster():
    try:
        print("开始获取管理员花名册数据")
        conn = get_db_connection()
        print("数据库连接成功")
        
        # 获取分页参数
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))
        offset = (page - 1) * page_size
        search = request.args.get('search', '')
        city = request.args.get('city', '')
        print(f"分页参数: page={page}, page_size={page_size}, offset={offset}, search={search}, city={city}")
        
        with conn.cursor() as cursor:
            # 构建查询条件
            where_clause = ""
            params = []
            
            # 构建条件列表
            conditions = []
            
            # 添加搜索条件
            if search:
                conditions.append("(name LIKE %s OR employee_id LIKE %s OR department LIKE %s)")
                search_param = f"%{search}%"
                params.extend([search_param, search_param, search_param])
            
            # 添加城市条件
            if city:
                conditions.append("city = %s")
                params.append(city)
            
            # 构建WHERE子句
            if conditions:
                where_clause = "WHERE " + " AND ".join(conditions)
            
            # 查询总记录数
            count_sql = f'SELECT COUNT(*) as total FROM admin_roster {where_clause}'
            cursor.execute(count_sql, params)
            total_result = cursor.fetchone()
            total = total_result['total']
            print(f"总记录数: {total}")
            
            # 查询分页数据
            data_sql = f'SELECT * FROM admin_roster {where_clause} LIMIT %s OFFSET %s'
            cursor.execute(data_sql, params + [page_size, offset])
            print("SQL执行成功")
            roster_data = cursor.fetchall()
            print(f"查询到 {len(roster_data)} 条数据")
        conn.close()
        print("数据库连接关闭")
        
        # 计算在职年限
        print("开始计算在职年限")
        for item in roster_data:
            if item.get('entry_date'):
                entry_date = item['entry_date']
                print(f"处理数据: {item['name']}, entry_date: {entry_date}, 类型: {type(entry_date)}")
                if isinstance(entry_date, str):
                    entry_date = datetime.strptime(entry_date, '%Y-%m-%d').date()
                today = datetime.now().date()  # 转换为date对象
                years = (today - entry_date).days / 365.25
                item['working_years'] = round(years, 1)
                print(f"在职年限: {item['working_years']}")
        print("在职年限计算完成")
        
        print("准备返回数据")
        return jsonify({
            'success': True,
            'data': roster_data,
            'total': total
        })
    except Exception as e:
        print(f"Error fetching admin roster: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': '获取管理员花名册数据失败'
        }), 500

@admin_bp.route('/roster/<int:id>', methods=['GET'])
def get_admin_by_id(id):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM admin_roster WHERE id = %s', (id,))
            admin = cursor.fetchone()
        conn.close()
        
        if not admin:
            return jsonify({
                'success': False,
                'message': '管理员不存在'
            }), 404
        
        # 计算在职年限
        if admin.get('entry_date'):
            entry_date = admin['entry_date']
            if isinstance(entry_date, str):
                entry_date = datetime.strptime(entry_date, '%Y-%m-%d').date()
            today = datetime.now().date()  # 转换为date对象
            years = (today - entry_date).days / 365.25
            admin['working_years'] = round(years, 1)
        
        return jsonify({
            'success': True,
            'data': admin
        })
    except Exception as e:
        print(f"Error fetching admin: {e}")
        return jsonify({
            'success': False,
            'message': '获取管理员数据失败'
        }), 500

@admin_bp.route('/roster', methods=['POST'])
def add_admin():
    try:
        data = request.json
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute('''
                INSERT INTO admin_roster (
                    name, employee_id, department, station_name, position, gender, 
                    contact_phone, ethnicity, marital_status, has_relationship, 
                    relationship_type, relative_name, relative_dept_position, education, 
                    political_status, id_card, household_address, entry_date, 
                    emergency_contact_name, emergency_relationship, emergency_contact_phone, 
                    current_address, contract_status, id_front_photo, id_back_photo
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            ''', (
                data.get('name'),
                data.get('employee_id'),
                data.get('department'),
                data.get('station_name'),
                data.get('position'),
                data.get('gender'),
                data.get('contact_phone'),
                data.get('ethnicity'),
                data.get('marital_status'),
                data.get('has_relationship'),
                data.get('relationship_type'),
                data.get('relative_name'),
                data.get('relative_dept_position'),
                data.get('education'),
                data.get('political_status'),
                data.get('id_card'),
                data.get('household_address'),
                data.get('entry_date'),
                data.get('emergency_contact_name'),
                data.get('emergency_relationship'),
                data.get('emergency_contact_phone'),
                data.get('current_address'),
                data.get('contract_status'),
                data.get('id_front_photo'),
                data.get('id_back_photo')
            ))
            conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '管理员添加成功'
        })
    except Exception as e:
        print(f"Error adding admin: {e}")
        return jsonify({
            'success': False,
            'message': '添加管理员失败'
        }), 500

@admin_bp.route('/roster/<int:id>', methods=['PUT'])
def update_admin(id):
    try:
        data = request.json
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 检查管理员是否存在
            cursor.execute('SELECT id FROM admin_roster WHERE id = %s', (id,))
            if not cursor.fetchone():
                conn.close()
                return jsonify({
                    'success': False,
                    'message': '管理员不存在'
                }), 404
            
            # 更新管理员信息
            cursor.execute('''
                UPDATE admin_roster SET 
                    name = %s, employee_id = %s, department = %s, station_name = %s, position = %s, 
                    gender = %s, contact_phone = %s, ethnicity = %s, marital_status = %s, 
                    has_relationship = %s, relationship_type = %s, relative_name = %s, 
                    relative_dept_position = %s, education = %s, political_status = %s, 
                    id_card = %s, household_address = %s, entry_date = %s, 
                    emergency_contact_name = %s, emergency_relationship = %s, 
                    emergency_contact_phone = %s, current_address = %s, 
                    contract_status = %s, id_front_photo = %s, id_back_photo = %s
                WHERE id = %s
            ''', (
                data.get('name'),
                data.get('employee_id'),
                data.get('department'),
                data.get('station_name'),
                data.get('position'),
                data.get('gender'),
                data.get('contact_phone'),
                data.get('ethnicity'),
                data.get('marital_status'),
                data.get('has_relationship'),
                data.get('relationship_type'),
                data.get('relative_name'),
                data.get('relative_dept_position'),
                data.get('education'),
                data.get('political_status'),
                data.get('id_card'),
                data.get('household_address'),
                data.get('entry_date'),
                data.get('emergency_contact_name'),
                data.get('emergency_relationship'),
                data.get('emergency_contact_phone'),
                data.get('current_address'),
                data.get('contract_status'),
                data.get('id_front_photo'),
                data.get('id_back_photo'),
                id
            ))
            conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '管理员信息更新成功'
        })
    except Exception as e:
        print(f"Error updating admin: {e}")
        return jsonify({
            'success': False,
            'message': '更新管理员信息失败'
        }), 500

@admin_bp.route('/roster/<int:id>', methods=['DELETE'])
def delete_admin(id):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 检查管理员是否存在
            cursor.execute('SELECT id FROM admin_roster WHERE id = %s', (id,))
            if not cursor.fetchone():
                conn.close()
                return jsonify({
                    'success': False,
                    'message': '管理员不存在'
                }), 404
            
            # 删除管理员
            cursor.execute('DELETE FROM admin_roster WHERE id = %s', (id,))
            conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '管理员删除成功'
        })
    except Exception as e:
        print(f"Error deleting admin: {e}")
        return jsonify({
            'success': False,
            'message': '删除管理员失败'
        }), 500

@admin_bp.route('/roster/batch', methods=['POST'])
def batch_add_admin():
    try:
        data = request.json
        staff_list = data.get('staff_list', [])
        
        if not staff_list:
            return jsonify({
                'success': False,
                'message': '没有数据需要导入'
            }), 400
        
        conn = get_db_connection()
        imported = 0
        
        with conn.cursor() as cursor:
            for staff in staff_list:
                try:
                    cursor.execute('''
                        INSERT INTO admin_roster (
                            name, employee_id, department, station_name, position, gender, 
                            contact_phone, ethnicity, marital_status, has_relationship, 
                            relationship_type, relative_name, relative_dept_position, education, 
                            political_status, id_card, household_address, entry_date, 
                            emergency_contact_name, emergency_relationship, emergency_contact_phone, 
                            current_address, contract_status
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                    ''', (
                        staff.get('姓名') or staff.get('name'),
                        staff.get('工号') or staff.get('employee_id'),
                        staff.get('所属部门') or staff.get('department'),
                        staff.get('站点名称') or staff.get('station_name'),
                        staff.get('职务') or staff.get('position'),
                        staff.get('性别') or staff.get('gender'),
                        staff.get('本人联系电话') or staff.get('contact_phone'),
                        staff.get('民族') or staff.get('ethnicity'),
                        staff.get('婚姻状况') or staff.get('marital_status'),
                        staff.get('内联关系') or staff.get('has_relationship'),
                        staff.get('关系类型') or staff.get('relationship_type'),
                        staff.get('关联人姓名') or staff.get('relative_name'),
                        staff.get('关联人部门岗位') or staff.get('relative_dept_position'),
                        staff.get('最高学历') or staff.get('education'),
                        staff.get('政治面貌') or staff.get('political_status'),
                        staff.get('身份证号码') or staff.get('id_card'),
                        staff.get('户籍所在地') or staff.get('household_address'),
                        staff.get('入职时间') or staff.get('entry_date'),
                        staff.get('紧急联系人') or staff.get('emergency_contact_name'),
                        staff.get('联系关系') or staff.get('emergency_relationship'),
                        staff.get('紧急联系电话') or staff.get('emergency_contact_phone'),
                        staff.get('居住地址') or staff.get('current_address'),
                        staff.get('合同情况') or staff.get('contract_status')
                    ))
                    imported += 1
                except Exception as e:
                    print(f"Error adding staff: {e}")
                    continue
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'成功导入 {imported} 条数据',
            'imported': imported
        })
    except Exception as e:
        print(f"Error batch adding admin: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': '批量导入失败'
        }), 500
