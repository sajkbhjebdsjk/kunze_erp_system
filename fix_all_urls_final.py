import os
import re

frontend_dir = 'frontend'

# 错误模式1: 模板字面量中 window.API_BASE_URL 没有 ${} 包裹
# `window.API_BASE_URL/api/xxx -> `${window.API_BASE_URL}/api/xxx`

# 错误模式2: $1 残留
# `${window.API_BASE_URL}$1` -> 需要推断正确路径

# 根据文件和行号上下文的 $1 -> 正确API路径 映射
# 格式: (filename, line_number_prefix): correct_path
CONTEXT_MAP = {
    # organization.html
    ('organization.html', 819): '/api/stations',
    ('organization.html', 1032): '/api/management-staff',
    # workflow-config.html
    ('workflow-config.html', 720): '/api/flows',
    ('workflow-config.html', 757): '/api/flows',
    ('workflow-config.html', 1186): '/api/users',
    ('workflow-config.html', 1203): '/api/salary-plans?status=enabled',
    ('workflow-config.html', 1233): '/api/contracts',
    # user-management.html
    ('user-management.html', 514): '/api/users',
    ('user-management.html', 535): '/api/departments',
    ('user-management.html', 578): '/api/cities',
    ('user-management.html', 621): '/api/positions',
    ('user-management.html', 700): '/api/users',
    ('user-management.html', 752): '/api/users/${id}',  # 注意: 这里有变量
    ('user-management.html', 799): '/api/users',
    # salary-plan-config.html
    ('salary-plan-config.html', 433): '/api/salary-plans',
    ('salary-plan-config.html', 470): '/api/salary-plans',
    # staff-roster.html
    ('staff-roster.html', 1185): '/api/admin/roster/batch',
    ('staff-roster.html', 1209): '/api/admin/roster?page=1&page_size=1000',
    ('staff-roster.html', 1302): '/api/admin/roster',
    # role-management.html
    ('role-management.html', 713): '/api/roles',
    ('role-management.html', 731): '/api/permissions',
    ('role-management.html', 809): '/api/roles',
    ('role-management.html', 851): '/api/permissions',
    ('role-management.html', 930): '/api/roles',
    # permission-management.html
    ('permission-management.html', 635): '/api/permissions',
    # mobile pages
    ('mobile-rider-contract.html', 557): '/api/rider-contracts/sign',
    ('mobile-flow-apply.html', 129): '/api/salary-plans?status=enabled',
    ('mobile-flow-apply.html', 161): '/api/contracts',
    ('mobile-flow-apply.html', 591): '/api/flows',
    ('mobile-login.html', 125): '/api/login',
    ('mobile-approval.html', 164): '/api/flows?status=enabled',
    ('mobile-contract-sign.html', 398): '/api/contracts/sign',
    ('mobile-approval-page.html', 374): '/api/flows?tab=',
    # contract-config.html
    ('contract-config.html', 645): '/api/contracts/upload',
    ('contract-config.html', 666): '/api/contracts',
    ('contract-config.html', 882): '/api/contracts',
    ('contract-config.html', 953): '/api/rider-contracts/stats',
    ('contract-config.html', 1139): '/api/rider-contracts/admin-view/',
}

fixed_count = 0

for root, dirs, files in os.walk(frontend_dir):
    for file in files:
        if not file.endswith(('.html', '.js')):
            continue
        
        file_path = os.path.join(root, file)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        lines = content.split('\n')
        new_lines = []
        
        for line_num, line in enumerate(lines, 1):
            # 修复模式1: `window.API_BASE_URL/api/xxx -> `${window.API_BASE_URL}/api/xxx`
            if '`window.API_BASE_URL/' in line and '${window.API_BASE_URL}' not in line:
                line = line.replace('`window.API_BASE_URL/', '`${window.API_BASE_URL}/')
                fixed_count += 1
            
            # 修复模式2: ${window.API_BASE_URL}$1
            if '${window.API_BASE_URL}$1' in line or "${window.API_BASE_URL}$1" in line:
                key = (file, line_num)
                if key in CONTEXT_MAP:
                    correct_path = CONTEXT_MAP[key]
                    line = line.replace('${window.API_BASE_URL}$1', f'${{window.API_BASE_URL}}{correct_path}')
                    line = line.replace('${window.API_BASE_URL}$1', f'${{window.API_BASE_URL}}{correct_path}')
                    fixed_count += 1
                else:
                    print(f"  [WARN] 无法自动修复 {file}:{line_num}: {line.strip()[:80]}")
            
            new_lines.append(line)
        
        content = '\n'.join(new_lines)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'已修复: {file_path}')

print(f'\n共修复 {fixed_count} 处错误')
print('完成！')
