import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': int(os.environ.get('DB_PORT', 3306)),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', '123456'),
    'database': os.environ.get('DB_NAME', 'erp_system'),
    'charset': 'utf8mb4',
    'connect_timeout': 10,
    'read_timeout': 30,
    'write_timeout': 30
}

# 初始化数据库
def init_database():
    import pymysql
    
    # 先连接到MySQL服务器，不指定数据库
    conn = pymysql.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password']
    )
    cursor = conn.cursor()
    
    try:
        # 创建数据库
        cursor.execute('CREATE DATABASE IF NOT EXISTS erp_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
        # 使用数据库
        cursor.execute('USE erp_system')
        
        # 创建城市表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cities (
                id INT PRIMARY KEY AUTO_INCREMENT,
                city_code VARCHAR(50) NOT NULL UNIQUE,
                city_name VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 插入城市数据
        cursor.execute('INSERT IGNORE INTO cities (city_code, city_name) VALUES (%s, %s)', ('all', '全部城市'))
        cursor.execute('INSERT IGNORE INTO cities (city_code, city_name) VALUES (%s, %s)', ('hangzhou', '杭州'))
        cursor.execute('INSERT IGNORE INTO cities (city_code, city_name) VALUES (%s, %s)', ('wuhan', '武汉'))
        cursor.execute('INSERT IGNORE INTO cities (city_code, city_name) VALUES (%s, %s)', ('shenyang', '沈阳'))
        cursor.execute('INSERT IGNORE INTO cities (city_code, city_name) VALUES (%s, %s)', ('jinhua', '金华'))
        cursor.execute('INSERT IGNORE INTO cities (city_code, city_name) VALUES (%s, %s)', ('shaoxing', '绍兴'))
        
        # 创建部门表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS departments (
                id INT PRIMARY KEY AUTO_INCREMENT,
                department_id VARCHAR(50) NOT NULL UNIQUE,
                department_name VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建岗位表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                id INT PRIMARY KEY AUTO_INCREMENT,
                position_id VARCHAR(50) NOT NULL UNIQUE,
                position_name VARCHAR(100) NOT NULL,
                department_id VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (department_id) REFERENCES departments(department_id)
            )
        ''')

        # 创建角色表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS roles (
                id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(50) NOT NULL UNIQUE,
                description VARCHAR(200),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        
        # 创建权限表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS permissions (
                id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(50) NOT NULL UNIQUE,
                code VARCHAR(50) NOT NULL UNIQUE,
                description VARCHAR(200),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 插入权限数据
        permissions = [
            # 骑手管理
            ('运力总览', 'rider_overview', '骑手运力总览'),
            ('入职审批', 'rider_onboarding', '骑手入职审批'),
            ('骑手花名册', 'rider_roster', '骑手信息花名册'),
            ('入离职汇总表', 'rider_turnover', '骑手入离职汇总'),
            ('兼职骑手列表', 'part_time_riders', '兼职骑手管理'),
            ('入职记录', 'onboarding_records', '骑手入职记录'),
            ('离职记录', 'resignation_records', '骑手离职记录'),
            ('待离职统计', 'pending_resignation', '待离职骑手统计'),
            
            # KPI管理
            ('KPI达成', 'kpi_achievement', 'KPI达成情况'),
            ('月累计划达成', 'monthly_plan', '月度计划达成'),
            ('日实时达成', 'daily_achievement', '日实时达成情况'),
            ('出勤管理', 'attendance_manage', '骑手出勤管理'),
            ('有效出勤达成率', 'effective_attendance', '有效出勤达成率'),
            ('时段出勤达成率', 'time_attendance', '时段出勤达成率'),
            
            # 经营管理
            ('招聘成本', 'recruitment_cost', '招聘成本管理'),
            ('骑手成本', 'rider_cost', '骑手成本管理'),
            ('全职成本', 'full_time_cost', '全职骑手成本'),
            ('骑手薪资表', 'rider_salary', '骑手薪资表'),
            ('兼职成本', 'part_time_cost', '兼职骑手成本'),
            ('系统罚单', 'system_fines', '系统罚单管理'),
            ('管理成本', 'management_cost', '管理成本管理'),
            ('管理人员薪资表', 'management_salary', '管理人员薪资表'),
            ('绩效考核达成情况', 'performance_review', '绩效考核达成情况'),
            ('管理成本预估', 'cost_estimation', '管理成本预估'),
            ('利润预估', 'profit_estimation', '利润预估'),
            
            # 人员及权限管理
            ('组织架构', 'organization', '组织架构管理'),
            ('管理人员花名册', 'staff_roster', '管理人员花名册'),
            ('账号管理', 'user_manage', '用户账号管理'),
            ('权限管理', 'permission_manage', '权限管理'),
            ('角色管理', 'role_manage', '角色管理'),
            
            # 配置工具
            ('工作流配置', 'workflow_config', '工作流配置'),
            ('招聘政策配置', 'recruitment_policy', '招聘政策配置'),
            ('薪资方案配置', 'salary_plan', '薪资方案配置'),
            ('内部绩效考核方案配置', 'internal_kpi_config', '内部绩效考核方案配置'),
            ('固定费用配置', 'fixed_cost_config', '固定费用配置'),
            
            # 系统权限
            ('城市切换', 'city_switch', '切换城市权限')
        ]
        for perm in permissions:
            cursor.execute('INSERT IGNORE INTO permissions (name, code, description) VALUES (%s, %s, %s)', perm)
        
        # 创建角色-权限关联表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS role_permissions (
                id INT PRIMARY KEY AUTO_INCREMENT,
                role_id INT NOT NULL,
                permission_id INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (role_id) REFERENCES roles(id),
                FOREIGN KEY (permission_id) REFERENCES permissions(id),
                UNIQUE KEY unique_role_permission (role_id, permission_id)
            )
        ''')
        
        
        # 创建用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT PRIMARY KEY AUTO_INCREMENT,
                username VARCHAR(50) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                city_code VARCHAR(50) NOT NULL,
                department_id VARCHAR(50) NOT NULL,
                position_id VARCHAR(50) NOT NULL,
                name VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (city_code) REFERENCES cities(city_code),
                FOREIGN KEY (department_id) REFERENCES departments(department_id),
                FOREIGN KEY (position_id) REFERENCES positions(position_id)
            )
        ''')
        
        # 创建用户-角色关联表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_roles (
                id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT NOT NULL,
                role_id INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (role_id) REFERENCES roles(id),
                UNIQUE KEY unique_user_role (user_id, role_id)
            )
        ''')
        
        
        # 创建流程类型表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS flow_types (
                id INT PRIMARY KEY AUTO_INCREMENT,
                type_id VARCHAR(50) NOT NULL UNIQUE,
                type_name VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        
        # 创建流程表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS flows (
                id INT PRIMARY KEY AUTO_INCREMENT,
                flow_id VARCHAR(50) NOT NULL UNIQUE,
                type_id VARCHAR(50) NOT NULL,
                employee_name VARCHAR(100) NOT NULL,
                initiator_id INT NOT NULL,
                status VARCHAR(50) NOT NULL DEFAULT 'pending',
                priority VARCHAR(50) NOT NULL DEFAULT 'normal',
                current_node VARCHAR(100) NOT NULL,
                progress INT NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                completed_at DATETIME NULL,
                FOREIGN KEY (type_id) REFERENCES flow_types(type_id),
                FOREIGN KEY (initiator_id) REFERENCES users(id)
            )
        ''')
        
        # 创建流程步骤表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS flow_steps (
                id INT PRIMARY KEY AUTO_INCREMENT,
                flow_id INT NOT NULL,
                step_name VARCHAR(100) NOT NULL,
                approver_id INT NOT NULL,
                status VARCHAR(50) NOT NULL DEFAULT 'pending',
                order_index INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                comment TEXT NULL,
                FOREIGN KEY (flow_id) REFERENCES flows(id),
                FOREIGN KEY (approver_id) REFERENCES users(id)
            )
        ''')
        
        # 创建审批记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS approval_records (
                id INT PRIMARY KEY AUTO_INCREMENT,
                flow_id INT NOT NULL,
                step_id INT NOT NULL,
                approver_id INT NOT NULL,
                action VARCHAR(50) NOT NULL,
                comment TEXT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (flow_id) REFERENCES flows(id),
                FOREIGN KEY (step_id) REFERENCES flow_steps(id),
                FOREIGN KEY (approver_id) REFERENCES users(id)
            )
        ''')
        
        # 创建流程字段数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS flow_field_data (
                id INT PRIMARY KEY AUTO_INCREMENT,
                flow_id INT NOT NULL,
                field_name VARCHAR(100) NOT NULL,
                field_value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (flow_id) REFERENCES flows(id)
            )
        ''')
        
        # 创建流程架构表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS flow_architectures (
                id INT PRIMARY KEY AUTO_INCREMENT,
                architecture_id VARCHAR(50) NOT NULL UNIQUE,
                flow_type VARCHAR(50) NOT NULL,
                flow_name VARCHAR(100) NOT NULL,
                description TEXT,
                status VARCHAR(50) DEFAULT 'disabled',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建流程架构步骤表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS flow_architecture_steps (
                id INT PRIMARY KEY AUTO_INCREMENT,
                architecture_id INT NOT NULL,
                step_name VARCHAR(100) NOT NULL,
                approver_id INT NOT NULL,
                step_order INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (architecture_id) REFERENCES flow_architectures(id),
                FOREIGN KEY (approver_id) REFERENCES users(id)
            )
        ''')
        
        # 创建流程字段表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS flow_fields (
                id INT PRIMARY KEY AUTO_INCREMENT,
                step_id INT NOT NULL,
                field_name VARCHAR(100) NOT NULL,
                field_type VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (step_id) REFERENCES flow_architecture_steps(id)
            )
        ''')
        
        # 创建流程字段选项表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS flow_field_options (
                id INT PRIMARY KEY AUTO_INCREMENT,
                field_id INT NOT NULL,
                option_value VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (field_id) REFERENCES flow_fields(id)
            )
        ''')
        
        # 创建流程评论表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS flow_comments (
                id INT PRIMARY KEY AUTO_INCREMENT,
                flow_id INT NOT NULL,
                user_id INT NOT NULL,
                comment TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (flow_id) REFERENCES flows(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # 创建薪资方案表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS salary_plans (
                id INT PRIMARY KEY AUTO_INCREMENT,
                plan_name VARCHAR(100) NOT NULL,
                plan_type VARCHAR(50) NOT NULL,
                description TEXT,
                content TEXT,
                file_path VARCHAR(255),
                status VARCHAR(50) DEFAULT 'disabled',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建通知表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT NOT NULL,
                type VARCHAR(50) NOT NULL,
                message TEXT NOT NULL,
                related_id VARCHAR(50) NOT NULL,
                is_read INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # 创建站点表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stations (
                id INT PRIMARY KEY AUTO_INCREMENT,
                station_id VARCHAR(50) NOT NULL UNIQUE,
                station_name VARCHAR(100) NOT NULL,
                city_code VARCHAR(50) NOT NULL,
                area_manager VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        
        # 创建骑手表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS riders (
                id INT PRIMARY KEY AUTO_INCREMENT,
                rider_id VARCHAR(50) NOT NULL UNIQUE COMMENT '骑手风神ID',
                name VARCHAR(100) NOT NULL COMMENT '姓名',
                phone VARCHAR(20) NOT NULL COMMENT '手机号',
                station_name VARCHAR(100) NOT NULL COMMENT '站点名称',
                first_run_date DATE COMMENT '首跑日期',
                entry_date DATE NOT NULL COMMENT '入职日期',
                exit_date DATE NOT NULL COMMENT '离职日期',
                leave_date DATE NOT NULL COMMENT '离岗日期',
                work_nature VARCHAR(50) NOT NULL COMMENT '工作性质',
                unit_price DECIMAL(10,2) COMMENT '单价',
                settlement_cycle VARCHAR(50) COMMENT '结算周期',
                id_card VARCHAR(18) NOT NULL COMMENT '身份证号',
                birth_date DATE COMMENT '出生日期',
                recruitment_channel VARCHAR(100) COMMENT '招聘渠道',
                referral_name VARCHAR(100) COMMENT '三方/内推姓名',
                salary_plan_id VARCHAR(50) COMMENT '薪资方案ID',
                emergency_phone VARCHAR(20) COMMENT '紧急联系人电话号码',
                position_status VARCHAR(50) NOT NULL COMMENT '岗位状态',
                tags VARCHAR(255) COMMENT '人员标签',
                remark TEXT COMMENT '备注',
                contract_status VARCHAR(50) COMMENT '合同状态',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建骑手入职记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rider_entry_records (
                id INT PRIMARY KEY AUTO_INCREMENT,
                rider_id VARCHAR(50) NOT NULL COMMENT '骑手风神ID',
                name VARCHAR(100) NOT NULL COMMENT '姓名',
                entry_date DATE NOT NULL COMMENT '入职日期',
                work_nature VARCHAR(50) NOT NULL COMMENT '工作性质',
                station_name VARCHAR(100) NOT NULL COMMENT '站点名称',
                recruitment_channel VARCHAR(100) COMMENT '招聘渠道',
                referrer VARCHAR(100) COMMENT '推荐人',
                status VARCHAR(50) NOT NULL DEFAULT 'active' COMMENT '状态',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (rider_id) REFERENCES riders(rider_id)
            )
        ''')
        
        # 创建骑手离职记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rider_exit_records (
                id INT PRIMARY KEY AUTO_INCREMENT,
                rider_id VARCHAR(50) NOT NULL COMMENT '骑手风神ID',
                name VARCHAR(100) NOT NULL COMMENT '姓名',
                exit_date DATE NOT NULL COMMENT '离职日期',
                exit_reason TEXT COMMENT '离职原因',
                station_name VARCHAR(100) NOT NULL COMMENT '站点名称',
                status VARCHAR(50) NOT NULL DEFAULT 'pending' COMMENT '状态',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (rider_id) REFERENCES riders(rider_id)
            )
        ''')
        
        # 创建兼职骑手表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS part_time_riders (
                id INT PRIMARY KEY AUTO_INCREMENT,
                rider_id VARCHAR(50) NOT NULL UNIQUE COMMENT '骑手风神ID',
                name VARCHAR(100) NOT NULL COMMENT '姓名',
                phone VARCHAR(20) NOT NULL COMMENT '手机号',
                station_name VARCHAR(100) NOT NULL COMMENT '站点名称',
                entry_date DATE NOT NULL COMMENT '入职日期',
                unit_price DECIMAL(10,2) COMMENT '单价',
                settlement_cycle VARCHAR(50) COMMENT '结算周期',
                id_card VARCHAR(18) NOT NULL COMMENT '身份证号',
                recruitment_channel VARCHAR(100) COMMENT '招聘渠道',
                status VARCHAR(50) NOT NULL DEFAULT 'active' COMMENT '状态',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建站点规模表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS station_scales (
                id INT PRIMARY KEY AUTO_INCREMENT,
                station_name VARCHAR(100) NOT NULL COMMENT '站点名称',
                scale_count INT NOT NULL COMMENT '规模数',
                city_code VARCHAR(50) NOT NULL COMMENT '城市代码',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (city_code) REFERENCES cities(city_code),
                UNIQUE KEY unique_station (station_name, city_code)
            )
        ''')
        
        # 插入杭州站点规模数据
        hangzhou_station_scales = [
            ('杭州坤泽-临安万华站', 0, 'hangzhou'),
            ('杭州坤泽-临安锦城站', 231, 'hangzhou'),
            ('杭州坤泽-临平崇贤站', 62, 'hangzhou'),
            ('杭州坤泽-上城兴业站', 29, 'hangzhou'),
            ('杭州坤泽-上城笕桥站', 33, 'hangzhou'),
            ('杭州坤泽-余杭勾庄站', 58, 'hangzhou'),
            ('杭州坤泽-余杭黄湖站', 6, 'hangzhou'),
            ('杭州坤泽-余杭良渚站', 62, 'hangzhou'),
            ('杭州坤泽-余杭径山站', 8, 'hangzhou'),
            ('杭州坤泽-余杭瓶窑站', 100, 'hangzhou'),
            ('杭州坤泽-余杭仁和站', 87, 'hangzhou'),
            ('杭州坤泽-余杭永旺站', 80, 'hangzhou')
        ]
        
        for station_data in hangzhou_station_scales:
            cursor.execute('INSERT IGNORE INTO station_scales (station_name, scale_count, city_code) VALUES (%s, %s, %s)', station_data)

        # 创建合同表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contracts (
                id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(255) NOT NULL COMMENT '合同名称',
                filename VARCHAR(255) NOT NULL COMMENT '文件名',
                filepath VARCHAR(255) NOT NULL COMMENT '文件路径',
                size VARCHAR(50) NOT NULL COMMENT '文件大小',
                content TEXT COMMENT '合同内容',
                status ENUM('active', 'inactive') DEFAULT 'active' COMMENT '状态',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        ''')

        # 创建合同签署记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contract_signatures (
                id INT PRIMARY KEY AUTO_INCREMENT,
                contract_id INT NOT NULL COMMENT '合同ID',
                flow_id INT NOT NULL COMMENT '流程ID',
                id_card VARCHAR(18) NOT NULL COMMENT '身份证号码',
                address TEXT NOT NULL COMMENT '送达地址',
                contact VARCHAR(255) NOT NULL COMMENT '联系方式',
                signature TEXT NOT NULL COMMENT '签名图片',
                signed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '签署时间',
                status VARCHAR(50) DEFAULT 'pending' COMMENT '状态',
                signed_filepath VARCHAR(255) COMMENT '签署后的合同文件路径',
                FOREIGN KEY (contract_id) REFERENCES contracts(id)
            )
        ''')

        # 创建骑手考勤统计表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rider_attendance (
                id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
                station_id VARCHAR(50) NOT NULL COMMENT '站点ID',
                station_name VARCHAR(100) NOT NULL COMMENT '站点名称',
                rider_name VARCHAR(50) NOT NULL COMMENT '骑手姓名',
                rider_id VARCHAR(50) NOT NULL COMMENT '骑手ID',
                attendance_date VARCHAR(50) NOT NULL COMMENT '考勤日期',
                time_period VARCHAR(50) DEFAULT NULL COMMENT '时段',
                is_scheduled VARCHAR(50) DEFAULT NULL COMMENT '是否排班',
                is_achieved VARCHAR(50) DEFAULT NULL COMMENT '是否达成',
                target_attendance_score DECIMAL(10,2) DEFAULT '0.00' COMMENT '目标出勤得分',
                attendance_score DECIMAL(10,2) DEFAULT '0.00' COMMENT '出勤得分',
                target_order_count INT DEFAULT '0' COMMENT '目标完单量',
                order_count INT DEFAULT '0' COMMENT '完单量',
                target_online_duration VARCHAR(20) DEFAULT '00小时00分钟' COMMENT '目标在线时长',
                online_duration VARCHAR(20) DEFAULT '00小时00分钟' COMMENT '在线时长',
                valid_online_duration VARCHAR(20) DEFAULT '00小时00分钟' COMMENT '有效在线时长',
                carry_duration VARCHAR(20) DEFAULT '00小时00分钟' COMMENT '背单时长',
                INDEX idx_station_id (station_id),
                INDEX idx_rider_id (rider_id),
                INDEX idx_attendance_date (attendance_date)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='骑手考勤统计表'
        ''')

        # 创建管理员花名册
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_roster (
                id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(100) NOT NULL COMMENT '姓名',
                employee_id VARCHAR(50) NOT NULL COMMENT '工号',
                department VARCHAR(100) NOT NULL COMMENT '所属部门',
                station_name VARCHAR(100) DEFAULT NULL COMMENT '站点名称',
                position VARCHAR(100) NOT NULL COMMENT '职务',
                gender VARCHAR(10) DEFAULT NULL COMMENT '性别',
                contact_phone VARCHAR(20) NOT NULL COMMENT '本人联系电话',
                ethnicity VARCHAR(50) DEFAULT NULL COMMENT '民族',
                marital_status VARCHAR(20) DEFAULT NULL COMMENT '婚姻状况',
                has_relationship VARCHAR(10) DEFAULT '否' COMMENT '在公司是否存在内联关系',
                relationship_type VARCHAR(50) DEFAULT NULL COMMENT '与关联人的关系类型',
                relative_name VARCHAR(100) DEFAULT NULL COMMENT '关联人姓名',
                relative_dept_position VARCHAR(200) DEFAULT NULL COMMENT '关联人部门及岗位',
                education VARCHAR(50) DEFAULT NULL COMMENT '最高学历',
                political_status VARCHAR(50) DEFAULT NULL COMMENT '政治面貌',
                id_card VARCHAR(18) NOT NULL COMMENT '身份证号码',
                household_address VARCHAR(255) DEFAULT NULL COMMENT '户籍所在地',
                entry_date DATE NOT NULL COMMENT '入职时间',
                emergency_contact_name VARCHAR(100) DEFAULT NULL COMMENT '紧急联系人姓名',
                emergency_relationship VARCHAR(50) DEFAULT NULL COMMENT '与紧急联系人关系',
                emergency_contact_phone VARCHAR(20) DEFAULT NULL COMMENT '紧急联系人电话',
                current_address VARCHAR(255) DEFAULT NULL COMMENT '目前居住地址',
                contract_status VARCHAR(50) DEFAULT NULL COMMENT '劳动合同签订情况',
                id_front_photo VARCHAR(255) DEFAULT NULL COMMENT '身份证正面照片路径',
                id_back_photo VARCHAR(255) DEFAULT NULL COMMENT '身份证反面照片路径',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                city VARCHAR(100) NOT NULL DEFAULT 'hangzhou' COMMENT '城市',
                UNIQUE KEY employee_id (employee_id),
                UNIQUE KEY id_card (id_card),
                INDEX idx_employee_id (employee_id),
                INDEX idx_id_card (id_card),
                INDEX idx_department (department),
                INDEX idx_station_name (station_name),
                INDEX idx_city (city)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')

        # 创建管理人员表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS management_staff (
                id INT PRIMARY KEY AUTO_INCREMENT,
                area_manager VARCHAR(100) NOT NULL,
                team VARCHAR(100) NOT NULL,
                name VARCHAR(100) NOT NULL,
                position VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')

        # 创建实时考勤表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS realtime_attendance (
                id BIGINT PRIMARY KEY AUTO_INCREMENT,
                站点id BIGINT DEFAULT NULL,
                站点名称 VARCHAR(50) DEFAULT NULL,
                姓名 VARCHAR(50) DEFAULT NULL,
                骑手id BIGINT DEFAULT NULL,
                排班时段 VARCHAR(50) DEFAULT NULL,
                上线时间 VARCHAR(50) DEFAULT NULL,
                排班状态 VARCHAR(50) DEFAULT NULL,
                工作状态 VARCHAR(50) DEFAULT NULL,
                全天在线时长 VARCHAR(50) DEFAULT NULL,
                全天有效在线时长 VARCHAR(50) DEFAULT NULL,
                全天完单量 BIGINT DEFAULT NULL,
                全天背单时长 VARCHAR(50) DEFAULT NULL,
                配送中单量 BIGINT DEFAULT NULL,
                时段 VARCHAR(50) DEFAULT NULL,
                时段在线时长 VARCHAR(50) DEFAULT NULL,
                时段有效在线时长 VARCHAR(50) DEFAULT NULL,
                时段完单量 DECIMAL(20,4) DEFAULT NULL,
                时段背单时长 VARCHAR(50) DEFAULT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')

        # 创建系统日志表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT DEFAULT 0,
                username VARCHAR(50) DEFAULT '',
                action VARCHAR(100) NOT NULL,
                details TEXT,
                ip_address VARCHAR(50),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_user_id (user_id),
                INDEX idx_action (action),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统操作日志表'
        ''')

        # ========================================
        # 初始化默认管理员账号（如果不存在）
        # ========================================
        try:
            # 检查是否已有用户
            cursor.execute('SELECT COUNT(*) as cnt FROM users')
            user_count = cursor.fetchone()['cnt']
            
            if user_count == 0:
                print('正在创建默认管理员账号...')
                
                # 创建默认角色
                cursor.executescript('''
                    INSERT IGNORE INTO roles (id, name, description, created_at) VALUES
                    (1, '超级管理员', '拥有系统所有权限', NOW()),
                    (2, '管理员', '拥有大部分管理权限', NOW()),
                    (3, '普通用户', '基本使用权限', NOW());
                ''')
                
                # 创建默认部门、岗位、城市
                cursor.executescript('''
                    INSERT IGNORE INTO departments (department_id, department_name) VALUES
                    (1, '总部'), (2, '运营部'), (3, '技术部');
                    
                    INSERT IGNORE INTO positions (position_id, position_name, department_id) VALUES
                    (1, '系统管理员', 1), (2, '运营经理', 2), (3, '技术员', 3);
                    
                    INSERT IGNORE INTO cities (city_code, city_name) VALUES
                    ('hangzhou', '杭州'), ('wuhan', '武汉'), ('shenyang', '沈阳'),
                    ('jinhua', '金华'), ('shaoxing', '绍兴');
                ''')
                
                # 创建默认管理员用户
                from utils.password_utils import hash_password
                password_hash = hash_password('admin123')
                
                cursor.execute('''
                    INSERT INTO users (
                        username, password, name, phone, email,
                        department_id, position_id, city_code,
                        is_active, role_ids, created_at
                    ) VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s,
                        1, '[1]', NOW()
                    )
                ''', (
                    'admin',
                    password_hash,
                    '系统管理员',
                    '13800138000',
                    'admin@kunze.com',
                    1, 1, 'hangzhou'
                ))
                
                # 为管理员分配角色
                cursor.execute('''
                    INSERT IGNORE INTO user_roles (user_id, role_id) VALUES (1, 1)
                ''')
                
                print('✓ 默认管理员账号创建成功！')
                print('  用户名: admin')
                print('  密码: admin123')
                print('  ⚠️  请登录后立即修改密码！')
            
        except Exception as role_error:
            print(f'⚠️ 创建默认用户时出错（不影响表结构）: {role_error}')

        conn.commit()
        print('数据库初始化成功')
    except Exception as e:
        print(f'数据库初始化错误: {e}')
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

# 获取数据库连接
def get_db_connection():
    import pymysql
    return pymysql.connect(**DB_CONFIG)

# 主函数
if __name__ == '__main__':
    init_database()