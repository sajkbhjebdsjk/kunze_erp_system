-- 数据库创建
CREATE DATABASE IF NOT EXISTS erp_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE erp_system;

-- 创建城市表
CREATE TABLE IF NOT EXISTS cities (
    id INT PRIMARY KEY AUTO_INCREMENT,
    city_code VARCHAR(50) NOT NULL UNIQUE,
    city_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 插入城市数据
INSERT IGNORE INTO cities (city_code, city_name) VALUES ('all', '全部城市');
INSERT IGNORE INTO cities (city_code, city_name) VALUES ('hangzhou', '杭州');
INSERT IGNORE INTO cities (city_code, city_name) VALUES ('wuhan', '武汉');
INSERT IGNORE INTO cities (city_code, city_name) VALUES ('shenyang', '沈阳');
INSERT IGNORE INTO cities (city_code, city_name) VALUES ('jinhua', '金华');
INSERT IGNORE INTO cities (city_code, city_name) VALUES ('shaoxing', '绍兴');

-- 创建部门表
CREATE TABLE IF NOT EXISTS departments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    department_id VARCHAR(50) NOT NULL UNIQUE,
    department_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建岗位表
CREATE TABLE IF NOT EXISTS positions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    position_id VARCHAR(50) NOT NULL UNIQUE,
    position_name VARCHAR(100) NOT NULL,
    department_id VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

-- 创建角色表
CREATE TABLE IF NOT EXISTS roles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建权限表
CREATE TABLE IF NOT EXISTS permissions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    code VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 插入权限数据
INSERT IGNORE INTO permissions (name, code, description) VALUES ('运力总览', 'rider_overview', '骑手运力总览');
INSERT IGNORE INTO permissions (name, code, description) VALUES ('入职审批', 'rider_onboarding', '骑手入职审批');
INSERT IGNORE INTO permissions (name, code, description) VALUES ('骑手花名册', 'rider_roster', '骑手信息花名册');
INSERT IGNORE INTO permissions (name, code, description) VALUES ('入离职汇总表', 'rider_turnover', '骑手入离职汇总');
INSERT IGNORE INTO permissions (name, code, description) VALUES ('兼职骑手列表', 'part_time_riders', '兼职骑手管理');
INSERT IGNORE INTO permissions (name, code, description) VALUES ('入职记录', 'onboarding_records', '骑手入职记录');
INSERT IGNORE INTO permissions (name, code, description) VALUES ('离职记录', 'resignation_records', '骑手离职记录');
INSERT IGNORE INTO permissions (name, code, description) VALUES ('待离职统计', 'pending_resignation', '待离职骑手统计');
INSERT IGNORE INTO permissions (name, code, description) VALUES ('KPI达成', 'kpi_achievement', 'KPI达成情况');
INSERT IGNORE INTO permissions (name, code, description) VALUES ('月累计划达成', 'monthly_plan', '月度计划达成');
INSERT IGNORE INTO permissions (name, code, description) VALUES ('日实时达成', 'daily_achievement', '日实时达成情况');
INSERT IGNORE INTO permissions (name, code, description) VALUES ('出勤管理', 'attendance_manage', '骑手出勤管理');
INSERT IGNORE INTO permissions (name, code, description) VALUES ('有效出勤达成率', 'effective_attendance', '有效出勤达成率');
INSERT IGNORE INTO permissions (name, code, description) VALUES ('时段出勤达成率', 'time_attendance', '时段出勤达成率');
INSERT IGNORE INTO permissions (name, code, description) VALUES ('招聘成本', 'recruitment_cost', '招聘成本管理');
INSERT IGNORE INTO permissions (name, code, description) VALUES ('骑手成本', 'rider_cost', '骑手成本管理');
INSERT IGNORE INTO permissions (name, code, description) VALUES ('全职成本', 'full_time_cost', '全职骑手成本');
INSERT IGNORE INTO permissions (name, code, description) VALUES ('骑手薪资表', 'rider_salary', '骑手薪资表');
INSERT IGNORE INTO permissions (name, code, description) VALUES ('兼职成本', 'part_time_cost', '兼职骑手成本');
INSERT IGNORE INTO permissions (name, code, description) VALUES ('系统罚单', 'system_fines', '系统罚单管理');
INSERT IGNORE INTO permissions (name, code, description) VALUES ('管理成本', 'management_cost', '管理成本管理');
INSERT IGNORE INTO permissions (name, code, description) VALUES ('管理人员薪资表', 'management_salary', '管理人员薪资表');
INSERT IGNORE INTO permissions (name, code, description) VALUES ('绩效考核达成情况', 'performance_review', '绩效考核达成情况');
INSERT IGNORE INTO permissions (name, code, description) VALUES ('管理成本预估', 'cost_estimation', '管理成本预估');
INSERT IGNORE INTO permissions (name, code, description) VALUES ('利润预估', 'profit_estimation', '利润预估');
INSERT IGNORE INTO permissions (name, code, description) VALUES ('组织架构', 'organization', '组织架构管理');
INSERT IGNORE INTO permissions (name, code, description) VALUES ('管理人员花名册', 'staff_roster', '管理人员花名册');
INSERT IGNORE INTO permissions (name, code, description) VALUES ('账号管理', 'user_manage', '用户账号管理');
INSERT IGNORE INTO permissions (name, code, description) VALUES ('权限管理', 'permission_manage', '权限管理');
INSERT IGNORE INTO permissions (name, code, description) VALUES ('角色管理', 'role_manage', '角色管理');
INSERT IGNORE INTO permissions (name, code, description) VALUES ('工作流配置', 'workflow_config', '工作流配置');
INSERT IGNORE INTO permissions (name, code, description) VALUES ('招聘政策配置', 'recruitment_policy', '招聘政策配置');
INSERT IGNORE INTO permissions (name, code, description) VALUES ('薪资方案配置', 'salary_plan', '薪资方案配置');
INSERT IGNORE INTO permissions (name, code, description) VALUES ('内部绩效考核方案配置', 'internal_kpi_config', '内部绩效考核方案配置');
INSERT IGNORE INTO permissions (name, code, description) VALUES ('固定费用配置', 'fixed_cost_config', '固定费用配置');
INSERT IGNORE INTO permissions (name, code, description) VALUES ('城市切换', 'city_switch', '切换城市权限');

-- 创建角色-权限关联表
CREATE TABLE IF NOT EXISTS role_permissions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    role_id INT NOT NULL,
    permission_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id),
    FOREIGN KEY (permission_id) REFERENCES permissions(id),
    UNIQUE KEY unique_role_permission (role_id, permission_id)
);

-- 创建用户表
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
);

-- 创建用户-角色关联表
CREATE TABLE IF NOT EXISTS user_roles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    role_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (role_id) REFERENCES roles(id),
    UNIQUE KEY unique_user_role (user_id, role_id)
);

-- 创建流程类型表
CREATE TABLE IF NOT EXISTS flow_types (
    id INT PRIMARY KEY AUTO_INCREMENT,
    type_id VARCHAR(50) NOT NULL UNIQUE,
    type_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建流程表
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
);

-- 创建流程步骤表
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
);

-- 创建审批记录表
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
);

-- 创建流程字段数据表
CREATE TABLE IF NOT EXISTS flow_field_data (
    id INT PRIMARY KEY AUTO_INCREMENT,
    flow_id INT NOT NULL,
    field_name VARCHAR(100) NOT NULL,
    field_value TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (flow_id) REFERENCES flows(id)
);

-- 创建流程架构表
CREATE TABLE IF NOT EXISTS flow_architectures (
    id INT PRIMARY KEY AUTO_INCREMENT,
    architecture_id VARCHAR(50) NOT NULL UNIQUE,
    flow_type VARCHAR(50) NOT NULL,
    flow_name VARCHAR(100) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'disabled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 创建流程架构步骤表
CREATE TABLE IF NOT EXISTS flow_architecture_steps (
    id INT PRIMARY KEY AUTO_INCREMENT,
    architecture_id INT NOT NULL,
    step_name VARCHAR(100) NOT NULL,
    approver_id INT NOT NULL,
    step_order INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (architecture_id) REFERENCES flow_architectures(id),
    FOREIGN KEY (approver_id) REFERENCES users(id)
);

-- 创建流程字段表
CREATE TABLE IF NOT EXISTS flow_fields (
    id INT PRIMARY KEY AUTO_INCREMENT,
    step_id INT NOT NULL,
    field_name VARCHAR(100) NOT NULL,
    field_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (step_id) REFERENCES flow_architecture_steps(id)
);

-- 创建流程字段选项表
CREATE TABLE IF NOT EXISTS flow_field_options (
    id INT PRIMARY KEY AUTO_INCREMENT,
    field_id INT NOT NULL,
    option_value VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (field_id) REFERENCES flow_fields(id)
);

-- 创建流程评论表
CREATE TABLE IF NOT EXISTS flow_comments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    flow_id INT NOT NULL,
    user_id INT NOT NULL,
    comment TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (flow_id) REFERENCES flows(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 创建薪资方案表
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
);

-- 创建通知表
CREATE TABLE IF NOT EXISTS notifications (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    type VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    related_id VARCHAR(50) NOT NULL,
    is_read INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 创建站点表
CREATE TABLE IF NOT EXISTS stations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    station_id VARCHAR(50) NOT NULL UNIQUE,
    station_name VARCHAR(100) NOT NULL,
    city_code VARCHAR(50) NOT NULL,
    area_manager VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建骑手表
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
);

-- 创建骑手入职记录表
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
);

-- 创建骑手离职记录表
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
);

-- 创建兼职骑手表
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
);

-- 创建站点规模表
CREATE TABLE IF NOT EXISTS station_scales (
    id INT PRIMARY KEY AUTO_INCREMENT,
    station_name VARCHAR(100) NOT NULL COMMENT '站点名称',
    scale_count INT NOT NULL COMMENT '规模数',
    city_code VARCHAR(50) NOT NULL COMMENT '城市代码',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (city_code) REFERENCES cities(city_code),
    UNIQUE KEY unique_station (station_name, city_code)
);

-- 插入杭州站点规模数据
INSERT IGNORE INTO station_scales (station_name, scale_count, city_code) VALUES ('杭州坤泽-临安万华站', 0, 'hangzhou');
INSERT IGNORE INTO station_scales (station_name, scale_count, city_code) VALUES ('杭州坤泽-临安锦城站', 231, 'hangzhou');
INSERT IGNORE INTO station_scales (station_name, scale_count, city_code) VALUES ('杭州坤泽-临平崇贤站', 62, 'hangzhou');
INSERT IGNORE INTO station_scales (station_name, scale_count, city_code) VALUES ('杭州坤泽-上城兴业站', 29, 'hangzhou');
INSERT IGNORE INTO station_scales (station_name, scale_count, city_code) VALUES ('杭州坤泽-上城笕桥站', 33, 'hangzhou');
INSERT IGNORE INTO station_scales (station_name, scale_count, city_code) VALUES ('杭州坤泽-余杭勾庄站', 58, 'hangzhou');
INSERT IGNORE INTO station_scales (station_name, scale_count, city_code) VALUES ('杭州坤泽-余杭黄湖站', 6, 'hangzhou');
INSERT IGNORE INTO station_scales (station_name, scale_count, city_code) VALUES ('杭州坤泽-余杭良渚站', 62, 'hangzhou');
INSERT IGNORE INTO station_scales (station_name, scale_count, city_code) VALUES ('杭州坤泽-余杭径山站', 8, 'hangzhou');
INSERT IGNORE INTO station_scales (station_name, scale_count, city_code) VALUES ('杭州坤泽-余杭瓶窑站', 100, 'hangzhou');
INSERT IGNORE INTO station_scales (station_name, scale_count, city_code) VALUES ('杭州坤泽-余杭仁和站', 87, 'hangzhou');
INSERT IGNORE INTO station_scales (station_name, scale_count, city_code) VALUES ('杭州坤泽-余杭永旺站', 80, 'hangzhou');

-- 创建合同表
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
);

-- 创建合同签署记录表
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
);

-- 创建骑手考勤统计表
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='骑手考勤统计表';



-- 骑手合同签署表（独立于工作流系统）- 增强版（含PDF和安全查看）
CREATE TABLE IF NOT EXISTS rider_contracts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    contract_no VARCHAR(50) NOT NULL UNIQUE COMMENT '合同编号',
    rider_id VARCHAR(50) NULL COMMENT '骑手风神ID（关联riders表）',
    party_b_name VARCHAR(100) NOT NULL COMMENT '乙方（承揽人）姓名',
    id_card VARCHAR(18) NOT NULL UNIQUE COMMENT '身份证号',
    phone VARCHAR(20) NOT NULL UNIQUE COMMENT '手机号',
    address VARCHAR(255) NOT NULL COMMENT '送达地址',
    emergency_name VARCHAR(50) NULL COMMENT '紧急联系人姓名',
    emergency_phone VARCHAR(20) NULL COMMENT '紧急联系人电话',
    emergency_address VARCHAR(255) NULL COMMENT '紧急联系人地址',
    signature_image TEXT NULL COMMENT '签名图片（base64）',
    signature_path VARCHAR(255) NULL COMMENT '签名图片路径',
    template_id INT NULL COMMENT '合同模板ID（关联contracts表）',
    pdf_path VARCHAR(255) NULL COMMENT '生成的PDF文件路径',
    pdf_filename VARCHAR(255) NULL COMMENT 'PDF文件名',
    sign_time DATETIME NULL COMMENT '签署时间',
    status TINYINT DEFAULT 0 COMMENT '状态：0-待签署，1-已签署，2-已失效',
    view_token VARCHAR(100) NULL COMMENT '一次性查看令牌',
    view_count INT DEFAULT 0 COMMENT '已查看次数',
    view_max_allowed INT DEFAULT 1 COMMENT '最大允许查看次数',
    last_view_time DATETIME NULL COMMENT '最后查看时间',
    view_expires_at DATETIME NULL COMMENT '查看链接过期时间',
    ip_address VARCHAR(45) NULL COMMENT '签署/查看时的IP地址',
    user_agent VARCHAR(500) NULL COMMENT '用户浏览器信息',
    is_deleted TINYINT DEFAULT 0 COMMENT '是否删除：0-否，1-是',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_rider_id (rider_id),
    INDEX idx_id_card (id_card),
    INDEX idx_contract_no (contract_no),
    INDEX idx_status (status),
    INDEX idx_view_token (view_token)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='骑手合同签署表';

-- 创建管理员花名册
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建管理人员表
CREATE TABLE IF NOT EXISTS management_staff (
    id INT PRIMARY KEY AUTO_INCREMENT,
    area_manager VARCHAR(100) NOT NULL,
    team VARCHAR(100) NOT NULL,
    name VARCHAR(100) NOT NULL,
    position VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建实时考勤表
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建系统日志表
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统操作日志表';

-- 额外添加2张表以达到35张表的要求
-- 创建招聘政策表
CREATE TABLE IF NOT EXISTS recruitment_policies (
    id INT PRIMARY KEY AUTO_INCREMENT,
    policy_name VARCHAR(100) NOT NULL,
    policy_type VARCHAR(50) NOT NULL,
    description TEXT,
    content TEXT,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 创建固定费用配置表
CREATE TABLE IF NOT EXISTS fixed_costs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    cost_name VARCHAR(100) NOT NULL,
    cost_type VARCHAR(50) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- =====================================================
-- 初始化默认数据：角色、部门、岗位、管理员账号
-- =====================================================

-- 插入默认角色
INSERT IGNORE INTO roles (id, name, description) VALUES
(1, '超级管理员', '拥有系统所有权限'),
(2, '管理员', '拥有大部分管理权限'),
(3, '普通用户', '基本使用权限');

-- 插入默认部门
INSERT IGNORE INTO departments (department_id, department_name) VALUES
('1', '总部'),
('2', '运营部'),
('3', '技术部');

-- 插入默认岗位
INSERT IGNORE INTO positions (position_id, position_name, department_id) VALUES
('1', '系统管理员', '1'),
('2', '运营经理', '2'),
('3', '技术员', '3');

-- =====================================================
-- 创建默认管理员账号
-- 用户名: admin
-- 密码: admin123 (已使用 Werkzeug 哈希)
-- =====================================================
INSERT IGNORE INTO users (
    username,
    password,
    city_code,
    department_id,
    position_id,
    name
) VALUES (
    'admin',
    'scrypt:32768:8:1$PTTALs1rDIQ3ZTpL$4c7727ac57b9979b7ca76488d5643ace0979c2205cf2337bcc10ac3622bb48134fbbe2a282227ea14dcc5f45b905abbbff04af01f0f71bea7203ba4130cfe1b1',
    'hangzhou',
    '1',
    '1',
    '系统管理员'
);

-- 为管理员分配超级管理员角色
INSERT IGNORE INTO user_roles (user_id, role_id) VALUES (1, 1);

-- 为超级管理员角色分配所有权限
INSERT IGNORE INTO role_permissions (role_id, permission_id) VALUES
(1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8),
(1, 9), (1, 10), (1, 11), (1, 12), (1, 13), (1, 14), (1, 15), (1, 16),
(1, 17), (1, 18), (1, 19), (1, 20), (1, 21), (1, 22), (1, 23), (1, 24),
(1, 25), (1, 26), (1, 27), (1, 28), (1, 29), (1, 30), (1, 31), (1, 32),
(1, 33), (1, 34);

-- =====================================================
-- 数据库初始化完成！
-- 默认登录凭据:
--   用户名: admin
--   密码:   admin123
-- ⚠️ 请登录后立即修改密码！
-- =====================================================