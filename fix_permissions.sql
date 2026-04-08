-- ============================================================
-- 权限数据完整修复脚本
-- 在 Railway MySQL Query 中执行此脚本
-- ============================================================

-- 1. 先查看当前权限数量（应该显示37）
SELECT COUNT(*) as current_count FROM permissions;

-- 2. 补全所有37个权限（INSERT IGNORE 会跳过已存在的）
INSERT IGNORE INTO permissions (name, code, description) VALUES 
('运力总览', 'rider_overview', '骑手运力总览'),
('入职审批', 'rider_onboarding', '骑手入职审批'),
('骑手花名册', 'rider_roster', '骑手信息花名册'),
('入离职汇总表', 'rider_turnover', '骑手入离职汇总'),
('兼职骑手列表', 'part_time_riders', '兼职骑手管理'),
('入职记录', 'onboarding_records', '骑手入职记录'),
('离职记录', 'resignation_records', '骑手离职记录'),
('待离职统计', 'pending_resignation', '待离职骑手统计'),
('KPI达成', 'kpi_achievement', 'KPI达成情况'),
('月累计划达成', 'monthly_plan', '月度计划达成'),
('日实时达成', 'daily_achievement', '日实时达成情况'),
('出勤管理', 'attendance_manage', '骑手出勤管理'),
('有效出勤达成率', 'effective_attendance', '有效出勤达成率'),
('时段出勤达成率', 'time_attendance', '时段出勤达成率'),
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
('组织架构', 'organization', '组织架构管理'),
('管理人员花名册', 'staff_roster', '管理人员花名册'),
('账号管理', 'user_manage', '用户账号管理'),
('权限管理', 'permission_manage', '权限管理'),
('角色管理', 'role_manage', '角色管理'),
('工作流配置', 'workflow_config', '工作流配置'),
('招聘政策配置', 'recruitment_policy', '招聘政策配置'),
('薪资方案配置', 'salary_plan', '薪资方案配置'),
('内部绩效考核方案配置', 'internal_kpi_config', '内部绩效考核方案配置'),
('固定费用配置', 'fixed_cost_config', '固定费用配置'),
('合同配置台', 'contract_config', '合同模板与签署管理'),
('城市切换', 'city_switch', '切换城市权限');

-- 3. 验证总数应为37
SELECT COUNT(*) as total_after_fix FROM permissions;

-- 4. 查看缺失的权限（如果有的话，下面会列出哪些code不存在）
SELECT p.code, p.name 
FROM (
    SELECT 'rider_overview' as code UNION SELECT 'rider_onboarding' UNION SELECT 'rider_roster'
    UNION SELECT 'rider_turnover' UNION SELECT 'part_time_riders' UNION SELECT 'onboarding_records'
    UNION SELECT 'resignation_records' UNION SELECT 'pending_resignation' UNION SELECT 'kpi_achievement'
    UNION SELECT 'monthly_plan' UNION SELECT 'daily_achievement' UNION SELECT 'attendance_manage'
    UNION SELECT 'effective_attendance' UNION SELECT 'time_attendance' UNION SELECT 'recruitment_cost'
    UNION SELECT 'rider_cost' UNION SELECT 'full_time_cost' UNION SELECT 'rider_salary'
    UNION SELECT 'part_time_cost' UNION SELECT 'system_fines' UNION SELECT 'management_cost'
    UNION SELECT 'management_salary' UNION SELECT 'performance_review' UNION SELECT 'cost_estimation'
    UNION SELECT 'profit_estimation' UNION SELECT 'organization' UNION SELECT 'staff_roster'
    UNION SELECT 'user_manage' UNION SELECT 'permission_manage' UNION SELECT 'role_manage'
    UNION SELECT 'workflow_config' UNION SELECT 'recruitment_policy' UNION SELECT 'salary_plan'
    UNION SELECT 'internal_kpi_config' UNION SELECT 'fixed_cost_config' UNION SELECT 'contract_config'
    UNION SELECT 'city_switch'
) expected
LEFT JOIN permissions p ON expected.code = p.code
WHERE p.id IS NULL;

-- 5. 给超级管理员(role_id=1)分配全部权限（包括新增的）
INSERT IGNORE INTO role_permissions (role_id, permission_id)
SELECT 1, id FROM permissions;

-- 6. 验证超级管理员权限数量
SELECT COUNT(*) as admin_permission_count 
FROM role_permissions WHERE role_id = 1;
