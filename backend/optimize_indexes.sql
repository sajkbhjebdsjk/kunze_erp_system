-- =====================================================
-- 数据库索引优化脚本
-- 用于提升ERP系统查询性能
-- 执行时间: 2026-04-03
-- =====================================================

-- 1. 骑手表索引优化
CREATE INDEX IF NOT EXISTS idx_riders_station_name ON riders(station_name);
CREATE INDEX IF NOT EXISTS idx_riders_position_status ON riders(position_status);
CREATE INDEX IF NOT EXISTS idx_riders_work_nature ON riders(work_nature);
CREATE INDEX IF NOT EXISTS idx_riders_entry_date ON riders(entry_date);
CREATE INDEX IF NOT EXISTS idx_riders_exit_date ON riders(exit_date);
CREATE INDEX IF NOT EXISTS idx_riders_leave_date ON riders(leave_date);
CREATE INDEX IF NOT EXISTS idx_riders_recruitment_channel ON riders(recruitment_channel);
CREATE INDEX IF NOT EXISTS idx_riders_id_card ON riders(id_card);
CREATE INDEX IF NOT EXISTS idx_rider_id ON riders(rider_id);

-- 2. 复合索引优化（用于常见组合查询）
CREATE INDEX IF NOT EXISTS idx_riders_station_status ON riders(station_name, position_status);
CREATE INDEX IF NOT EXISTS idx_riders_station_work_nature ON riders(station_name, work_nature);
CREATE INDEX IF NOT EXISTS idx_riders_entry_exit_dates ON riders(entry_date, exit_date, leave_date);

-- 3. 合同签署表索引
CREATE INDEX IF NOT EXISTS idx_contract_signatures_id_card ON contract_signatures(id_card);
CREATE INDEX IF NOT EXISTS idx_contract_signatures_contract_id ON contract_signatures(contract_id);
CREATE INDEX IF NOT EXISTS idx_contract_signatures_signed_at ON contract_signatures(signed_at);

-- 4. 骑手考勤表索引优化（已有部分索引，补充复合索引）
CREATE INDEX IF NOT EXISTS idx_attendance_station_date ON rider_attendance(station_name, attendance_date);
CREATE INDEX IF NOT EXISTS idx_attendance_rider_date ON rider_attendance(rider_id, attendance_date);
CREATE INDEX IF NOT EXISTS idx_attestation_station_order ON rider_attendance(station_name, order_count);

-- 5. 实时考勤表索引
CREATE INDEX IF NOT EXISTS idx_realtime_station_name ON realtime_attendance(`站点名称`);
CREATE INDEX IF NOT EXISTS idx_realtime_rider_id ON realtime_attendance(`骑手id`);
CREATE INDEX IF NOT EXISTS idx_realtime_order_count ON realtime_attendance(`全天完单量`);

-- 6. 站点规模表索引
CREATE INDEX IF NOT EXISTS idx_station_scales_city_station ON station_scales(city_code, station_name);

-- 7. 骑手入职记录表索引
CREATE INDEX IF NOT EXISTS idx_entry_records_rider_date ON rider_entry_records(rider_id, entry_date);
CREATE INDEX IF NOT EXISTS idx_entry_records_station_date ON rider_entry_records(station_name, entry_date);

-- 8. 骑手离职记录表索引
CREATE INDEX IF NOT EXISTS idx_exit_records_rider_date ON rider_exit_records(rider_id, exit_date);
CREATE INDEX IF NOT EXISTS idx_exit_records_station_date ON rider_exit_records(station_name, exit_date);

-- 9. 用户表索引优化
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_city_code ON users(city_code);

-- 10. 流程相关表索引
CREATE INDEX IF NOT EXISTS idx_flows_initiator ON flows(initiator_id);
CREATE INDEX IF NOT EXISTS idx_flows_type_status ON flows(type_id, status);
CREATE INDEX IF NOT EXISTS idx_flows_created_at ON flows(created_at);
CREATE INDEX IF NOT EXISTS idx_flow_steps_flow ON flow_steps(flow_id);
CREATE INDEX IF NOT EXISTS idx_flow_steps_approver ON flow_steps(approver_id);

-- 11. 管理员花名册索引优化（已有部分索引）
CREATE INDEX IF NOT EXISTS idx_admin_roster_department ON admin_roster(department);
CREATE INDEX IF NOT EXISTS idx_admin_roster_position ON admin_roster(position);
CREATE INDEX IF NOT EXISTS idx_admin_roster_entry_date ON admin_roster(entry_date);

-- 12. 通知表索引
CREATE INDEX IF NOT EXISTS idx_notifications_user_read ON notifications(user_id, is_read);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at);

-- 13. 系统日志表复合索引
CREATE INDEX IF NOT EXISTS idx_logs_user_action_time ON system_logs(user_id, action, created_at);

-- 查看索引创建结果
SHOW INDEX FROM riders;
SHOW INDEX FROM rider_attendance;
SHOW INDEX FROM admin_roster;
