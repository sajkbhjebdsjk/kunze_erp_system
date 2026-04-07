document.addEventListener('DOMContentLoaded', function() {
    const usernameElement = document.getElementById('username');
    const logoutBtn = document.getElementById('logout-btn');
    const navItems = document.querySelectorAll('.nav-item');
    const companyInfoElement = document.getElementById('company-info');
    const cityDropdown = document.getElementById('city-dropdown');
    const cityDropdownItems = document.querySelectorAll('.dropdown-content a');

    // 检查用户登录状态
    checkLoginStatus();

    // 城市下拉菜单点击事件
    companyInfoElement.addEventListener('click', function() {
        this.classList.toggle('active');
        cityDropdown.classList.toggle('show');
    });

    // 城市切换事件
    cityDropdownItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const city = this.getAttribute('data-city');
            // 更新公司名称
            companyInfoElement.textContent = this.textContent;
            // 隐藏下拉菜单
            companyInfoElement.classList.remove('active');
            cityDropdown.classList.remove('show');
            // 更新数据 - 后续将通过API获取
            updateCityData(city);
        });
    });

    // 点击其他区域关闭下拉菜单
    document.addEventListener('click', function(e) {
        if (!companyInfoElement.contains(e.target) && !cityDropdown.contains(e.target)) {
            companyInfoElement.classList.remove('active');
            cityDropdown.classList.remove('show');
        }
    });

    // 退出登录事件
    logoutBtn.addEventListener('click', function() {
        localStorage.removeItem('user');
        window.location.href = 'login.html';
    });

    // 左侧导航事件
    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            // 处理子菜单展开/收起
            if (this.classList.contains('with-submenu') && e.target === this) {
                e.preventDefault();
                const subMenu = this.nextElementSibling;
                if (subMenu && subMenu.classList.contains('sub-menu')) {
                    subMenu.classList.toggle('show');
                }
            }
        });
    });

    // 初始化运力总览页面
    if (window.location.pathname.includes('rider-overview.html')) {
        initRiderOverviewPage();
    }

    function checkLoginStatus() {
        const user = localStorage.getItem('user');
        if (!user) {
            // 未登录，跳转到登录页面
            window.location.href = 'login.html';
            return;
        }
        
        const userData = JSON.parse(user);
        // 显示用户名和岗位
            const usernameElement = document.getElementById('username');
            const userPositionElement = document.getElementById('user-position-display');
            const userAvatarElement = document.getElementById('user-avatar');
            
            if (usernameElement) {
                usernameElement.textContent = userData.name;
            }
            
            if (userPositionElement) {
                userPositionElement.textContent = userData.position;
            }
        
        if (userAvatarElement) {
            // 显示用户头像的首字母
            userAvatarElement.textContent = userData.name.charAt(0);
        }
        
        // 调试：打印用户权限
        console.log('用户权限:', userData.permissions);
        
        // 获取之前选择的城市
        const selectedCity = localStorage.getItem('selectedCity') || userData.city_code;
        
        // 控制城市子商筛选器的显示
        setTimeout(() => {
            const cityFilter = document.getElementById('city-filter');
            if (cityFilter) {
                if (userData.city_code === 'all') {
                    // 总商显示城市子商筛选器
                    cityFilter.style.display = 'flex';
                } else {
                    // 城市用户隐藏城市子商筛选器
                    cityFilter.style.display = 'none';
                }
            }
        }, 100);
        
        // 控制城市下拉菜单的显示
        if (companyInfoElement && cityDropdown) {
            if (userData.city_code === 'all') {
                // 总商显示城市下拉菜单
                companyInfoElement.style.display = 'inline-block';
                companyInfoElement.style.pointerEvents = 'auto';
                companyInfoElement.style.cursor = 'pointer';
                companyInfoElement.style.opacity = '1';
            } else {
                // 城市用户隐藏城市下拉菜单
                companyInfoElement.style.display = 'inline-block';
                companyInfoElement.style.pointerEvents = 'none';
                companyInfoElement.style.cursor = 'default';
                companyInfoElement.style.opacity = '0.7';
                companyInfoElement.classList.remove('active');
                cityDropdown.classList.remove('show');
            }
        }
        
        // 根据用户城市权限设置公司名称
        if (userData.city_code === 'all') {
            // 更新公司名称为当前选择的城市
            let cityText = '杭州坤泽物流有限公司-总商';
            for (let i = 0; i < cityDropdownItems.length; i++) {
                if (cityDropdownItems[i].getAttribute('data-city') === selectedCity) {
                    cityText = cityDropdownItems[i].textContent;
                    break;
                }
            }
            companyInfoElement.textContent = cityText;
            // 更新数据
            updateCityData(selectedCity);
        } else {
            // 查找对应的城市名称
            let cityText = '杭州坤泽物流有限公司';
            for (let i = 0; i < cityDropdownItems.length; i++) {
                if (cityDropdownItems[i].getAttribute('data-city') === userData.city_code) {
                    cityText = cityDropdownItems[i].textContent;
                    break;
                }
            }
            companyInfoElement.textContent = cityText;
            // 更新数据
            updateCityData(userData.city_code);
        }
        
        // 实现权限控制
        controlPermissions(userData);
    }
    
    function controlPermissions(userData) {
        // 获取用户权限列表
        const userPermissions = userData.permissions || [];
        const permissionCodes = userPermissions.map(perm => perm.code);
        
        // 检查用户是否有KPI相关权限
        let hasKpiPermission = false;
        permissionCodes.forEach(code => {
            if ((code.includes('kpi') && !code.includes('config')) || 
                (code.includes('plan') && !code.includes('salary')) || 
                code.includes('achievement') || 
                code.includes('attendance')) {
                hasKpiPermission = true;
                console.log('导致KPI权限为true的权限:', code);
            }
        });
        
        // 检查用户是否有经营管理相关权限
        const hasBusinessPermission = permissionCodes.some(code => code.includes('cost') || code.includes('profit'));
        
        // 检查用户是否有配置工具相关权限
        const hasConfigPermission = permissionCodes.some(code => code.includes('config'));
        
        // 检查用户是否有人事权限
        const hasPersonnelPermission = permissionCodes.some(code => code.includes('organization') || code.includes('user_manage') || 
                                                      code.includes('permission_manage') || code.includes('role_manage') || 
                                                      code.includes('staff_roster'));
        
        // 调试：打印KPI权限判断结果
        console.log('KPI权限判断结果:', hasKpiPermission);
        console.log('权限列表:', permissionCodes);
        
        // 控制导航菜单显示
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            const text = item.textContent.trim();
            
            // 检查是否需要显示
            let shouldShow = false;
            
            // 首页始终显示
            if (text === '首页') {
                shouldShow = true;
            }
            // 组织架构
            else if (text === '组织架构' && permissionCodes.includes('organization')) {
                shouldShow = true;
            }
            // 角色管理
            else if (text === '角色管理' && permissionCodes.includes('role_manage')) {
                shouldShow = true;
            }
            // 权限管理
            else if (text === '权限管理' && permissionCodes.includes('permission_manage')) {
                shouldShow = true;
            }
            // 账号管理
            else if (text === '账号管理' && permissionCodes.includes('user_manage')) {
                shouldShow = true;
            }
            // 骑手管理
            else if (text === '骑手管理' && permissionCodes.some(code => code.includes('rider'))) {
                shouldShow = true;
            }
            // KPI管理及其子菜单
            else if (hasKpiPermission && (
                text === 'KPI管理' || 
                text === 'KPI达成' || 
                text === '出勤管理' || 
                text === '月累计划达成' || 
                text === '日实时达成' || 
                text === '有效出勤达成率' || 
                text === '时段出勤达成率'
            )) {
                shouldShow = true;
            }
            // 经营管理及其子菜单
            else if (hasBusinessPermission && (
                text === '经营管理' || 
                text === '招聘成本' || 
                text === '骑手成本' || 
                text === '全职成本' || 
                text === '骑手薪资表' || 
                text === '兼职成本' || 
                text === '系统罚单' || 
                text === '管理成本' || 
                text === '管理人员薪资表' || 
                text === '绩效考核达成情况' || 
                text === '管理成本预估' || 
                text === '利润预估'
            )) {
                shouldShow = true;
            }
            // 人员及权限管理
            else if (hasPersonnelPermission && text === '人员及权限管理') {
                shouldShow = true;
            }
            // 管理人员花名册
            else if (text === '管理人员花名册' && permissionCodes.includes('staff_roster')) {
                shouldShow = true;
            }
            // 配置工具及其子菜单
            else if (hasConfigPermission && (
                text === '配置工具' || 
                text === '工作流配置' || 
                text === '招聘政策配置' || 
                text === '薪资方案配置' || 
                text === '内部绩效考核方案配置' || 
                text === '固定费用配置' || 
                text === '合同配置台'
            )) {
                shouldShow = true;
            }
            
            // 调试：打印每个导航项的显示状态
            if (text === 'KPI管理') {
                console.log('KPI管理菜单显示状态:', shouldShow);
            }
            
            if (shouldShow) {
                item.style.display = 'block';
            } else {
                // 默认隐藏导航项
                item.style.display = 'none';
            }
        });
        
        // 控制城市切换权限
        if (userData.city_code === 'all') {
            // 如果用户是总商，始终允许切换城市
            // 总商用户默认具有城市切换权限
            companyInfoElement.style.pointerEvents = 'auto';
            companyInfoElement.style.cursor = 'pointer';
            companyInfoElement.style.opacity = '1';
        }
    }

    function updateCityData(city) {
        // 存储当前选择的城市
        localStorage.setItem('selectedCity', city);
        
        // 后续将通过API获取数据
        console.log('更新城市数据:', city);
        
        // 清空现有数据
        const performanceGrid = document.querySelector('.performance-grid');
        if (performanceGrid) {
            performanceGrid.innerHTML = `
                <div class="performance-card">
                    <h4>加载中...</h4>
                    <p>数据正在获取</p>
                </div>
            `;
        }
        
        const regionTable = document.getElementById('region-table') ? document.getElementById('region-table').querySelector('tbody') : null;
        if (regionTable) {
            regionTable.innerHTML = `
                <tr>
                    <td colspan="15">数据正在获取</td>
                </tr>
            `;
        }
        
        // 加载站点数据到部门下拉框
        loadStationData(city);
        
        // 加载运力总览数据
        if (window.location.pathname.includes('rider-overview.html')) {
            loadRiderOverviewData();
        } else {
            // 加载骑手花名册数据
            loadRiderRosterData({ city });
        }
        
        // 加载入离职汇总数据
        if (window.location.pathname.includes('rider-entry-exit-summary.html')) {
            loadEntryExitSummaryData({ city_code: city });
            loadThirdPartySummaryData({ city_code: city });
            loadEntryExitTrendCharts({ city_code: city, dimension: 'day' });
            loadThirdPartyAnalysisCharts({ city_code: city });
        }
        
        // 加载入职记录数据
        if (window.location.pathname.includes('rider-entry-records.html')) {
            loadEntryRecordsData({ city });
            loadEntryTrendCharts({ city });
        }
        
        // 加载离职记录数据
        if (window.location.pathname.includes('rider-exit-records.html')) {
            loadExitRecordsData({ city });
            loadExitTrendCharts({ city });
        }
        
        // 加载兼职骑手数据
        if (window.location.pathname.includes('rider-part-time.html')) {
            loadPartTimeRiderData({ city });
        }
        
        // 加载待离职统计数据
        if (window.location.pathname.includes('rider-pending-exit.html')) {
            loadPendingExitData({ city });
            loadPendingExitTrendCharts({ city });
        }
        
        // 加载管理人员花名册数据
        if (window.location.pathname.includes('staff-roster.html') && typeof window.updateCityData === 'function') {
            window.updateCityData(city);
        }
        
        // 加载组织架构数据
        if (window.location.pathname.includes('organization.html') && typeof loadDepartments === 'function') {
            loadDepartments(city);
        }
        
        // 加载账号管理数据
        if (window.location.pathname.includes('user-management.html') && typeof loadUsers === 'function') {
            loadUsers(city);
        }
        
        // 加载角色管理数据
        if (window.location.pathname.includes('role-management.html') && typeof loadRoles === 'function') {
            loadRoles(); // 角色管理通常不需要按城市过滤，但保持一致性
        }
    }
    
    // 加载站点数据到部门下拉框
    function loadStationData(city) {
        const departmentSelect = document.getElementById('department-select');
        if (!departmentSelect) return;
        
        // 清空下拉框
        departmentSelect.innerHTML = '<option value="">请选择部门</option>';
        
        // 只有杭州城市需要加载站点数据
        if (city === 'hangzhou') {
            // 从API获取站点数据
            fetch(`${window.API_BASE_URL}/api/stations?city_code=hangzhou`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const stations = data.stations || [];
                        stations.forEach(station => {
                            const option = document.createElement('option');
                            option.value = station.department_name;
                            option.textContent = station.department_name;
                            departmentSelect.appendChild(option);
                        });
                    }
                })
                .catch(error => {
                    console.error('加载站点数据失败:', error);
                });
        }
    }
    
    // 加载骑手花名册数据
    function loadRiderRosterData(filters = {}) {
        const riderTable = document.getElementById('rider-table');
        if (!riderTable) return;
        
        const tbody = riderTable.querySelector('tbody');
        tbody.innerHTML = `
            <tr>
                <td colspan="25" class="loading">
                    <p>加载中...</p>
                </td>
            </tr>
        `;
        
        // 加载统计数据
        loadRiderStats();
        
        // 获取当前选择的城市
        const selectedCity = filters.city || localStorage.getItem('selectedCity') || 'all';
        
        // 构建查询参数
        const queryParams = new URLSearchParams();
        queryParams.append('city', selectedCity);
        if (filters.organization) queryParams.append('organization', filters.organization);
        if (filters.department) queryParams.append('department', filters.department);
        if (filters.search) queryParams.append('search', filters.search);
        if (filters.startDate) queryParams.append('start_date', filters.startDate);
        if (filters.endDate) queryParams.append('end_date', filters.endDate);
        
        const queryString = queryParams.toString();
        const url = `${window.API_BASE_URL}/api/riders${queryString ? `?${queryString}` : ''}`;
        
        // 从API获取骑手数据
        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const riders = data.data;
                    tbody.innerHTML = '';
                    
                    riders.forEach((rider, index) => {
                        const row = document.createElement('tr');
                        
                        // 工作性质颜色显示
                        let workNatureClass = '';
                        let workNatureText = formatValue(rider.work_nature);
                        if (workNatureText === '兼职') {
                            workNatureClass = 'status-badge part-time';
                        } else if (workNatureText === '全职') {
                            workNatureClass = 'status-badge full-time';
                        }
                        
                        // 岗位状态样式
                        let positionStatusClass = '';
                        let positionStatusText = formatValue(rider.position_status);
                        if (positionStatusText === '在职') {
                            positionStatusClass = 'status-badge active';
                        } else if (positionStatusText === '离职') {
                            positionStatusClass = 'status-badge normal-exit';
                        } else if (positionStatusText === '待离职') {
                            positionStatusClass = 'status-badge pending-exit';
                        }
                        
                        // 人员标签样式
                        let tagsText = formatValue(rider.tags);
                        let tagsHtml = tagsText;
                        if (tagsText && tagsText !== '-') {
                            // 将标签拆分为数组并添加样式
                            const tagsArray = tagsText.split(' ');
                            tagsHtml = tagsArray.map(tag => {
                                let tagClass = 'status-badge';
                                if (tag === '正常离职') {
                                    tagClass += ' normal-exit';
                                } else if (tag === '自离') {
                                    tagClass += ' self-exit';
                                } else if (tag === '新人') {
                                    tagClass += ' active';
                                }
                                return `<span class="${tagClass}">${tag}</span>`;
                            }).join(' ');
                        }
                        
                        row.innerHTML = `
                            <td><input type="checkbox" data-rider-id="${rider.rider_id}"></td>
                            <td>${index + 1}</td>
                            <td>${formatValue(rider.city, 'city', rider)}</td>
                            <td>${formatValue(rider.rider_id, 'rider_id', rider)}</td>
                            <td>${formatValue(rider.name, 'name', rider)}</td>
                            <td>${formatValue(rider.phone, 'phone', rider)}</td>
                            <td>${formatValue(rider.station_name, 'station_name', rider)}</td>
                            <td>${formatValue(rider.first_run_date, 'first_run_date', rider)}</td>
                            <td>${formatValue(rider.entry_date, 'entry_date', rider)}</td>
                            <td><span class="${workNatureClass}">${workNatureText}</span></td>
                            <td>${formatValue(rider.unit_price, 'unit_price', rider)}</td>
                            <td>${formatValue(rider.settlement_cycle, 'settlement_cycle', rider)}</td>
                            <td>${formatValue(rider.id_card, 'id_card', rider)}</td>
                            <td>${formatValue(rider.birth_date, 'birth_date', rider)}</td>
                            <td>${formatValue(rider.recruitment_channel, 'recruitment_channel', rider)}</td>
                            <td>${formatValue(rider.referral_name, 'referral_name', rider)}</td>
                            <td>${formatValue(rider.salary_plan_id, 'salary_plan_id', rider)}</td>
                            <td>${formatValue(rider.emergency_phone, 'emergency_phone', rider)}</td>
                            <td><span class="${positionStatusClass}">${positionStatusText}</span></td>
                            <td>${formatValue(rider.exit_date, 'exit_date', rider)}</td>
                            <td>${formatValue(rider.leave_date, 'leave_date', rider)}</td>
                            <td>${tagsHtml}</td>
                            <td>${formatValue(rider.remark, 'remark', rider)}</td>
                            <td>${formatValue(rider.contract_status, 'contract_status', rider)}</td>
                            <td>
                                <a href="#" class="action-link edit-rider" data-rider-id="${rider.rider_id}">编辑</a>
                                <a href="#" class="action-link view-rider" data-rider-id="${rider.rider_id}">详情</a>
                            </td>
                        `;
                        tbody.appendChild(row);
                    });
                    
                    // 绑定编辑和详情事件
                    bindRiderActions();
                } else {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="25">
                            <p>加载失败，请重试</p>
                        </td>
                    </tr>
                `;
            }
        })
        .catch(error => {
            console.error('加载骑手数据失败:', error);
            tbody.innerHTML = `
                <tr>
                    <td colspan="25">
                        <p>网络错误，请稍后重试</p>
                    </td>
                </tr>
            `;
        });
    }
    
    // 绑定骑手操作事件
    function bindRiderActions() {
        // 编辑事件
        document.querySelectorAll('.edit-rider').forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const riderId = this.getAttribute('data-rider-id');
                editRider(riderId);
            });
        });
        
        // 详情事件
        document.querySelectorAll('.view-rider').forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const riderId = this.getAttribute('data-rider-id');
                viewRider(riderId);
            });
        });
        
        // 合同状态按钮点击事件
        document.querySelectorAll('.contract-status-btn').forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                const riderId = this.getAttribute('data-rider-id');
                viewContract(riderId);
            });
        });
    }
    
    // 查看合同
    function viewContract(riderId) {
        // 从API获取骑手的合同信息
        fetch(`${window.API_BASE_URL}/api/riders/${riderId}/contract`) 
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const contract = data.data;
                    openContractModal(contract);
                } else {
                    // 处理API返回的错误
                    if (data.error === '骑手不存在' || data.error === '合同不存在') {
                        alert('该骑手暂无合同信息');
                    } else {
                        alert('获取合同信息失败: ' + (data.error || '未知错误'));
                    }
                }
            })
            .catch(error => {
                console.error('获取合同信息失败:', error);
                alert('网络错误，请稍后重试');
            });
    }
    
    // 打开合同查看模态框
    function openContractModal(contract) {
        // 创建模态框
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        `;
        
        // 创建模态框内容
        const modalContent = document.createElement('div');
        modalContent.className = 'modal-content';
        modalContent.style.cssText = `
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            width: 90%;
            max-width: 800px;
            max-height: 80vh;
            overflow-y: auto;
        `;
        
        // 模态框标题
        const modalTitle = document.createElement('h3');
        modalTitle.textContent = '合同详情';
        modalTitle.style.cssText = 'margin-top: 0; margin-bottom: 20px;';
        modalContent.appendChild(modalTitle);
        
        // 合同内容
        const contractContent = document.createElement('div');
        contractContent.innerHTML = `
            <div style="margin-bottom: 15px;">
                <h4>合同信息</h4>
                <p><strong>合同名称:</strong> ${contract.contract_name || '-'}</p>
                <p><strong>签署时间:</strong> ${contract.signed_at || '-'}</p>
                <p><strong>状态:</strong> ${contract.status || '-'}</p>
            </div>
            <div style="margin-bottom: 15px;">
                <h4>乙方信息</h4>
                <p><strong>身份证号码:</strong> ${contract.id_card || '-'}</p>
                <p><strong>送达地址:</strong> ${contract.address || '-'}</p>
                <p><strong>联系方式:</strong> ${contract.contact || '-'}</p>
            </div>
            <div style="margin-bottom: 15px;">
                <h4>签名</h4>
                ${contract.signature ? `<img src="${contract.signature}" style="max-width: 200px; max-height: 100px;" alt="签名">` : '<p>-</p>'}
            </div>
            <div style="margin-bottom: 15px;">
                <h4>合同内容</h4>
                <div style="border: 1px solid #ddd; padding: 15px; border-radius: 4px; background-color: #f9f9f9; max-height: 300px; overflow-y: auto;">
                    ${contract.content || '<p>合同内容为空</p>'}
                </div>
            </div>
            <div style="margin-top: 20px; display: flex; gap: 10px; justify-content: flex-end;">
                ${contract.file_path ? `<a href="${contract.file_path}" class="btn btn-secondary" target="_blank">下载合同</a>` : ''}
                <button class="btn btn-secondary" onclick="this.closest('.modal').remove();">关闭</button>
            </div>
        `;
        
        modalContent.appendChild(contractContent);
        modal.appendChild(modalContent);
        document.body.appendChild(modal);
        
        // 点击模态框外部关闭
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }
    
    // 编辑骑手
    function editRider(riderId) {
        // 从API获取骑手详情
        fetch(`${window.API_BASE_URL}/api/riders/${riderId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const rider = data.data;
                    openEditModal(rider);
                } else {
                    alert('获取骑手信息失败，请重试');
                }
            })
            .catch(error => {
                console.error('获取骑手信息失败:', error);
                alert('网络错误，请稍后重试');
            });
    }
    
    // 查看骑手详情
    function viewRider(riderId) {
        // 从API获取骑手详情
        fetch(`${window.API_BASE_URL}/api/riders/${riderId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const rider = data.data;
                    openViewModal(rider);
                } else {
                    alert('获取骑手信息失败，请重试');
                }
            })
            .catch(error => {
                console.error('获取骑手信息失败:', error);
                alert('网络错误，请稍后重试');
            });
    }
    
    // 打开编辑模态框
    function openEditModal(rider) {
        // 创建模态框
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        `;
        
        // 创建模态框内容
        const modalContent = document.createElement('div');
        modalContent.className = 'modal-content';
        modalContent.style.cssText = `
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            width: 90%;
            max-width: 600px;
            max-height: 80vh;
            overflow-y: auto;
        `;
        
        // 模态框标题
        const modalTitle = document.createElement('h3');
        modalTitle.textContent = '编辑骑手信息';
        modalTitle.style.cssText = 'margin-top: 0; margin-bottom: 20px;';
        modalContent.appendChild(modalTitle);
        
        // 表单
        const form = document.createElement('form');
        form.innerHTML = `
            <div style="margin-bottom: 15px;">
                <label style="display: block; margin-bottom: 5px;">骑手风神ID</label>
                <input type="text" name="rider_id" value="${rider.rider_id}" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;" readonly>
            </div>
            <div style="margin-bottom: 15px;">
                <label style="display: block; margin-bottom: 5px;">姓名</label>
                <input type="text" name="name" value="${rider.name || ''}" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
            </div>
            <div style="margin-bottom: 15px;">
                <label style="display: block; margin-bottom: 5px;">手机号</label>
                <input type="text" name="phone" value="${rider.phone || ''}" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
            </div>
            <div style="margin-bottom: 15px;">
                <label style="display: block; margin-bottom: 5px;">城市</label>
                <input type="text" name="city" value="${rider.city || 'hangzhou'}" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
            </div>
            <div style="margin-bottom: 15px;">
                <label style="display: block; margin-bottom: 5px;">站点名称</label>
                <input type="text" name="station_name" value="${rider.station_name || ''}" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
            </div>
            <div style="margin-bottom: 15px;">
                <label style="display: block; margin-bottom: 5px;">工作性质</label>
                <select name="work_nature" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
                    <option value="全职" ${rider.work_nature === '全职' ? 'selected' : ''}>全职</option>
                    <option value="兼职" ${rider.work_nature === '兼职' ? 'selected' : ''}>兼职</option>
                </select>
            </div>
            <div style="margin-bottom: 15px;">
                <label style="display: block; margin-bottom: 5px;">薪资方案绑定</label>
                <input type="text" name="salary_plan_id" value="${rider.salary_plan_id || ''}" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
            </div>
            <div style="margin-bottom: 15px;">
                <label style="display: block; margin-bottom: 5px;">紧急联系人电话号码</label>
                <input type="text" name="emergency_phone" value="${rider.emergency_phone || ''}" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
            </div>
            <div style="margin-top: 20px; display: flex; gap: 10px; justify-content: flex-end;">
                <button type="button" class="btn btn-secondary" onclick="this.closest('.modal').remove();">取消</button>
                <button type="submit" class="btn btn-primary">保存</button>
            </div>
        `;
        
        // 表单提交事件
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(form);
            const updatedRider = {};
            formData.forEach((value, key) => {
                updatedRider[key] = value;
            });
            
            // 发送更新请求
            fetch(`${window.API_BASE_URL}/api/riders/${rider.rider_id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(updatedRider)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('更新成功');
                    modal.remove();
                    loadRiderRosterData();
                } else {
                    alert('更新失败，请重试');
                }
            })
            .catch(error => {
                console.error('更新失败:', error);
                alert('网络错误，请稍后重试');
            });
        });
        
        modalContent.appendChild(form);
        modal.appendChild(modalContent);
        document.body.appendChild(modal);
        
        // 点击模态框外部关闭
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }
    
    // 打开查看模态框
    function openViewModal(rider) {
        // 创建模态框
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        `;
        
        // 创建模态框内容
        const modalContent = document.createElement('div');
        modalContent.className = 'modal-content';
        modalContent.style.cssText = `
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            width: 90%;
            max-width: 600px;
            max-height: 80vh;
            overflow-y: auto;
        `;
        
        // 模态框标题
        const modalTitle = document.createElement('h3');
        modalTitle.textContent = '骑手详情';
        modalTitle.style.cssText = 'margin-top: 0; margin-bottom: 20px;';
        modalContent.appendChild(modalTitle);
        
        // 详情内容
        const details = document.createElement('div');
        details.innerHTML = `
            <div style="margin-bottom: 10px;"><strong>城市:</strong> ${formatValue(rider.city, 'city', rider)}</div>
            <div style="margin-bottom: 10px;"><strong>骑手风神ID:</strong> ${formatValue(rider.rider_id, 'rider_id', rider)}</div>
            <div style="margin-bottom: 10px;"><strong>姓名:</strong> ${formatValue(rider.name, 'name', rider)}</div>
            <div style="margin-bottom: 10px;"><strong>手机号:</strong> ${formatValue(rider.phone, 'phone', rider)}</div>
            <div style="margin-bottom: 10px;"><strong>站点名称:</strong> ${formatValue(rider.station_name, 'station_name', rider)}</div>
            <div style="margin-bottom: 10px;"><strong>首跑日期:</strong> ${formatValue(rider.first_run_date, 'first_run_date', rider)}</div>
            <div style="margin-bottom: 10px;"><strong>入职日期:</strong> ${formatValue(rider.entry_date, 'entry_date', rider)}</div>
            <div style="margin-bottom: 10px;"><strong>工作性质:</strong> <span class="${rider.work_nature === '兼职' ? 'status-badge part-time' : rider.work_nature === '全职' ? 'status-badge full-time' : ''}">${formatValue(rider.work_nature, 'work_nature', rider)}</span></div>
            <div style="margin-bottom: 10px;"><strong>单价:</strong> ${formatValue(rider.unit_price, 'unit_price', rider)}</div>
            <div style="margin-bottom: 10px;"><strong>结算周期:</strong> ${formatValue(rider.settlement_cycle, 'settlement_cycle', rider)}</div>
            <div style="margin-bottom: 10px;"><strong>身份证号:</strong> ${formatValue(rider.id_card, 'id_card', rider)}</div>
            <div style="margin-bottom: 10px;"><strong>出生日期:</strong> ${formatValue(rider.birth_date, 'birth_date', rider)}</div>
            <div style="margin-bottom: 10px;"><strong>招聘渠道:</strong> ${formatValue(rider.recruitment_channel, 'recruitment_channel', rider)}</div>
            <div style="margin-bottom: 10px;"><strong>三方/内推姓名:</strong> ${formatValue(rider.referral_name, 'referral_name', rider)}</div>
            <div style="margin-bottom: 10px;"><strong>薪资方案绑定:</strong> ${formatValue(rider.salary_plan_id, 'salary_plan_id', rider)}</div>
            <div style="margin-bottom: 10px;"><strong>紧急联系人电话号码:</strong> ${formatValue(rider.emergency_phone, 'emergency_phone', rider)}</div>
            <div style="margin-bottom: 10px;"><strong>岗位状态:</strong> ${formatValue(rider.position_status, 'position_status', rider)}</div>
            <div style="margin-bottom: 10px;"><strong>人员标签:</strong> ${formatValue(rider.tags, 'tags', rider)}</div>
            <div style="margin-bottom: 10px;"><strong>备注:</strong> ${formatValue(rider.remark, 'remark', rider)}</div>
            <div style="margin-bottom: 10px;"><strong>合同状态:</strong> ${formatValue(rider.contract_status, 'contract_status', rider)}</div>
            <div style="margin-top: 20px; text-align: right;">
                <button class="btn btn-secondary" onclick="this.closest('.modal').remove();">关闭</button>
            </div>
        `;
        
        modalContent.appendChild(details);
        modal.appendChild(modalContent);
        document.body.appendChild(modal);
        
        // 点击模态框外部关闭
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }
    
    // 绑定筛选器事件
    function bindFilterEvents() {
        const searchBtn = document.querySelector('.btn-search');
        const resetBtn = document.querySelector('.btn-reset');
        
        if (searchBtn) {
            searchBtn.addEventListener('click', function() {
                const filters = getFilters();
                loadRiderRosterData(filters);
            });
        }
        
        if (resetBtn) {
            resetBtn.addEventListener('click', function() {
                resetFilters();
                loadRiderRosterData();
            });
        }
    }
    
    // 获取筛选条件
    function getFilters() {
        const organization = document.querySelector('input[placeholder="请选择关键字搜索，用英文,隔开"]').value;
        const department = document.querySelector('select').value;
        const search = document.querySelector('input[placeholder="请输入风神ID、姓名、电话号码"]').value;
        const startDate = document.querySelectorAll('input[type="datetime-local"]')[0].value;
        const endDate = document.querySelectorAll('input[type="datetime-local"]')[1].value;
        const city = localStorage.getItem('selectedCity') || 'all';
        
        return {
            city,
            organization,
            department,
            search,
            startDate,
            endDate
        };
    }
    
    // 重置筛选条件
    function resetFilters() {
        document.querySelector('input[placeholder="请选择关键字搜索，用英文,隔开"]').value = '';
        document.querySelector('select').value = '';
        document.querySelector('input[placeholder="请输入风神ID、姓名、电话号码"]').value = '';
        document.querySelectorAll('input[type="datetime-local"]')[0].value = '';
        document.querySelectorAll('input[type="datetime-local"]')[1].value = '';
    }
    
    // 绑定操作按钮事件
    function bindActionButtons() {
        // 导出数据
        const exportBtn = document.querySelector('.rider-actions button:last-child');
        if (exportBtn && exportBtn.textContent.trim() === '导出数据') {
            exportBtn.addEventListener('click', function() {
                exportRiderData();
            });
        } else {
            // 尝试通过其他方式查找导出按钮
            const buttons = document.querySelectorAll('.rider-actions button');
            buttons.forEach(button => {
                if (button.textContent.trim() === '导出数据') {
                    button.addEventListener('click', function() {
                        exportRiderData();
                    });
                }
            });
        }
        
        // 下载导入模板
        const templateBtn = document.querySelector('.rider-actions button');
        if (templateBtn) {
            const buttons = document.querySelectorAll('.rider-actions button');
            buttons.forEach(button => {
                if (button.textContent.trim() === '下载导入模板') {
                    button.addEventListener('click', function() {
                        downloadImportTemplate();
                    });
                }
            });
        }
        
        // 导入骑手信息
        const importBtn = document.querySelector('.rider-actions button');
        if (importBtn) {
            const buttons = document.querySelectorAll('.rider-actions button');
            buttons.forEach(button => {
                if (button.textContent.trim() === '导入骑手信息') {
                    button.addEventListener('click', function() {
                        importRiderData();
                    });
                }
            });
        }
    }
    
    // 导出骑手数据
    function exportRiderData() {
        // 从API获取骑手数据
        fetch('${window.API_BASE_URL}/api/riders')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const riders = data.data;
                    if (riders.length === 0) {
                        alert('没有数据可导出');
                        return;
                    }
                    
                    // 生成CSV内容
                    const headers = [
                        '城市', '骑手风神ID', '姓名', '手机号', '站点名称', '首跑日期', '入职日期',
                        '工作性质', '单价', '结算周期', '身份证号', '出生日期', '招聘渠道',
                        '三方/内推姓名', '薪资方案绑定', '紧急联系人电话号码', '岗位状态',
                        '离职日期', '离岗日期', '人员标签', '备注', '合同状态'
                    ];
                    
                    const csvContent = [
                        headers.join(','),
                        ...riders.map(rider => [
                            rider.city || 'hangzhou',
                            rider.rider_id,
                            rider.name,
                            rider.phone,
                            rider.station_name,
                            rider.first_run_date ? new Date(rider.first_run_date).toLocaleDateString('zh-CN') : '',
                            rider.entry_date ? new Date(rider.entry_date).toLocaleDateString('zh-CN') : '',
                            rider.work_nature,
                            rider.unit_price,
                            rider.settlement_cycle,
                            rider.id_card,
                            rider.birth_date ? new Date(rider.birth_date).toLocaleDateString('zh-CN') : '',
                            rider.recruitment_channel,
                            rider.referral_name,
                            rider.salary_plan_id,
                            rider.emergency_phone,
                            rider.position_status,
                            rider.exit_date ? new Date(rider.exit_date).toLocaleDateString('zh-CN') : '',
                            rider.leave_date ? new Date(rider.leave_date).toLocaleDateString('zh-CN') : '',
                            rider.tags,
                            rider.remark,
                            rider.contract_status
                        ].join(','))
                    ].join('\n');
                    
                    // 创建下载链接
                    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
                    const url = URL.createObjectURL(blob);
                    const link = document.createElement('a');
                    link.setAttribute('href', url);
                    link.setAttribute('download', `骑手花名册_${new Date().toISOString().split('T')[0]}.csv`);
                    link.style.visibility = 'hidden';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                } else {
                    alert('导出失败，请重试');
                }
            })
            .catch(error => {
                console.error('导出数据失败:', error);
                alert('网络错误，请稍后重试');
            });
    }
    
    // 导入骑手信息
    function importRiderData() {
        // 创建文件上传输入框
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.csv';
        input.style.display = 'none';
        document.body.appendChild(input);
        
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (!file) return;
            
            const reader = new FileReader();
            // 尝试使用不同编码读取文件
            const readerUTF8 = new FileReader();
            readerUTF8.onload = function(e) {
                let csvContent = e.target.result;
                console.log('UTF-8 CSV内容:', csvContent);
                
                // 检查是否有乱码（简单检测：是否包含大量�字符）
                const hasGarbled = (csvContent.match(/�/g) || []).length > 5;
                
                if (hasGarbled) {
                    // 尝试使用GBK编码读取
                    const readerGBK = new FileReader();
                    readerGBK.onload = function(e) {
                        const arrayBuffer = e.target.result;
                        const decoder = new TextDecoder('gbk');
                        csvContent = decoder.decode(arrayBuffer);
                        console.log('GBK CSV内容:', csvContent);
                        processCSV(csvContent);
                    };
                    readerGBK.readAsArrayBuffer(file);
                } else {
                    processCSV(csvContent);
                }
            };
            
            function processCSV(csvContent) {
                const riders = parseCSV(csvContent);
                console.log('解析后的数据:', riders);
                
                if (riders.length === 0) {
                    alert('解析失败，文件格式不正确');
                    return;
                }
                
                // 上传数据到服务器
                uploadRiders(riders);
            }
            
            readerUTF8.readAsText(file, 'UTF-8');
            document.body.removeChild(input);
        });
        
        input.click();
    }
    
    // 从身份证号提取出生日期
    function extractBirthDateFromIdCard(idCard) {
        if (!idCard || idCard.length < 15) return '';
        
        let birthDateStr;
        if (idCard.length === 18) {
            // 18位身份证：第7-14位为出生日期，格式YYYYMMDD
            birthDateStr = idCard.substring(6, 14);
        } else if (idCard.length === 15) {
            // 15位身份证：第7-12位为出生日期，格式YYMMDD，需要转换为YYYYMMDD
            const year = '19' + idCard.substring(6, 8);
            const month = idCard.substring(8, 10);
            const day = idCard.substring(10, 12);
            birthDateStr = year + month + day;
        } else {
            return '';
        }
        
        // 转换为YYYY-MM-DD格式
        if (birthDateStr.length === 8) {
            const year = birthDateStr.substring(0, 4);
            const month = birthDateStr.substring(4, 6);
            const day = birthDateStr.substring(6, 8);
            return `${year}-${month}-${day}`;
        }
        
        return '';
    }

    // 加载运力总览数据
    function loadRiderOverviewData(stationName = '') {
        const riderTable = document.getElementById('rider-table');
        if (!riderTable) return;
        
        const tbody = riderTable.querySelector('tbody');
        tbody.innerHTML = `
            <tr>
                <td colspan="16" class="loading">
                    <p>加载中...</p>
                </td>
            </tr>
        `;
        
        // 获取当前选择的城市
        const selectedCity = localStorage.getItem('selectedCity') || 'all';
        
        // 构建查询参数
        const queryParams = new URLSearchParams();
        queryParams.append('city', selectedCity);
        if (stationName) {
            queryParams.append('station_name', stationName);
        }
        
        const queryString = queryParams.toString();
        const url = `${window.API_BASE_URL}/api/riders/overview${queryString ? `?${queryString}` : ''}`;
        
        // 从API获取运力总览数据
        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const overviewData = data.data;
                    tbody.innerHTML = '';
                    
                    overviewData.forEach((item, index) => {
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td><input type="checkbox"></td>
                            <td>${index + 1}</td>
                            <td>${item.station_name || '-'}</td>
                            <td>${item.scale_count || 0}</td>
                            <td>${item.rider_count || 0}</td>
                            <td>${item.gap_count || 0}</td>
                            <td>${item.scale_ratio || 0}%</td>
                            <td>${item.part_time_count || 0}</td>
                            <td>${item.full_time_count || 0}</td>
                            <td>${item.part_time_ratio || 0}%</td>
                            <td>${item.three_days_no_order || 0}</td>
                            <td>${item.yesterday_no_order || 0}</td>
                            <td>${item.today_attendance || 0}</td>
                            <td>${item.today_entry_count || 0}</td>
                            <td>${item.today_entry_part_time || 0}</td>
                            <td>${item.today_entry_full_time || 0}</td>
                        `;
                        tbody.appendChild(row);
                    });
                    
                    // 绘制运力分析图
                    drawRiderAnalysisCharts(overviewData);
                } else {
                    tbody.innerHTML = `
                        <tr>
                            <td colspan="16">
                                <p>加载失败，请重试</p>
                            </td>
                        </tr>
                    `;
                }
            })
            .catch(error => {
                console.error('加载运力总览数据失败:', error);
                tbody.innerHTML = `
                    <tr>
                        <td colspan="16">
                            <p>网络错误，请稍后重试</p>
                        </td>
                    </tr>
                `;
            });
    }
    
    // 存储图表实例
    let charts = {};
    
    // 绘制运力分析图
    function drawRiderAnalysisCharts(overviewData) {
        // 准备数据
        const stationNames = overviewData.map(item => item.station_name);
        const riderCounts = overviewData.map(item => item.rider_count);
        const scaleRatios = overviewData.map(item => item.scale_ratio);
        const partTimeRatios = overviewData.map(item => item.part_time_ratio);
        const attendances = overviewData.map(item => item.today_attendance);
        
        // 销毁旧图表
        if (charts.riderCountChart) {
            charts.riderCountChart.destroy();
        }
        if (charts.scaleRatioChart) {
            charts.scaleRatioChart.destroy();
        }
        if (charts.partTimeRatioChart) {
            charts.partTimeRatioChart.destroy();
        }
        if (charts.attendanceChart) {
            charts.attendanceChart.destroy();
        }
        
        // 骑手数图表
        const riderCountCtx = document.getElementById('riderCountChart').getContext('2d');
        charts.riderCountChart = new Chart(riderCountCtx, {
            type: 'bar',
            data: {
                labels: stationNames,
                datasets: [{
                    label: '骑手数',
                    data: riderCounts,
                    backgroundColor: 'rgba(75, 192, 192, 0.6)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
        
        // 规模占比图表
        const scaleRatioCtx = document.getElementById('scaleRatioChart').getContext('2d');
        charts.scaleRatioChart = new Chart(scaleRatioCtx, {
            type: 'bar',
            data: {
                labels: stationNames,
                datasets: [{
                    label: '规模占比 (%)',
                    data: scaleRatios,
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
        
        // 兼职骑手占比图表
        const partTimeRatioCtx = document.getElementById('partTimeRatioChart').getContext('2d');
        charts.partTimeRatioChart = new Chart(partTimeRatioCtx, {
            type: 'bar',
            data: {
                labels: stationNames,
                datasets: [{
                    label: '兼职骑手占比 (%)',
                    data: partTimeRatios,
                    backgroundColor: 'rgba(255, 206, 86, 0.6)',
                    borderColor: 'rgba(255, 206, 86, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
        
        // 今日出勤骑手数图表
        const attendanceCtx = document.getElementById('attendanceChart').getContext('2d');
        charts.attendanceChart = new Chart(attendanceCtx, {
            type: 'bar',
            data: {
                labels: stationNames,
                datasets: [{
                    label: '今日出勤骑手数',
                    data: attendances,
                    backgroundColor: 'rgba(153, 102, 255, 0.6)',
                    borderColor: 'rgba(153, 102, 255, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
    
    // 绑定筛选器事件
    function bindFilterEvents() {
        const searchBtn = document.querySelector('.btn-search');
        const resetBtn = document.querySelector('.btn-reset');
        const departmentSelect = document.getElementById('department-select');
        
        if (searchBtn) {
            searchBtn.addEventListener('click', function() {
                const stationName = departmentSelect.value;
                loadRiderOverviewData(stationName);
            });
        }
        
        if (resetBtn) {
            resetBtn.addEventListener('click', function() {
                departmentSelect.value = '';
                loadRiderOverviewData();
            });
        }
    }
    
    // 初始化页面
    function initRiderOverviewPage() {
        // 加载站点数据
        const selectedCity = localStorage.getItem('selectedCity') || 'all';
        loadStationData(selectedCity);
        
        // 加载运力总览数据
        loadRiderOverviewData();
        
        // 绑定筛选器事件
        bindFilterEvents();
        
        // 绑定按钮事件
        bindRiderActionEvents();
        
        // 更新数据时间
        updateDataTime();
        
        // 设置自动数据更新（每20分钟）
        setInterval(() => {
            loadRiderOverviewData();
            updateDataTime();
        }, 20 * 60 * 1000);
    }
    
    // 绑定骑手操作按钮事件
    function bindRiderActionEvents() {
        const refreshBtn = document.querySelector('.rider-actions .btn-primary');
        const exportBtn = document.querySelector('.rider-actions .btn-secondary:nth-child(2)');
        const fullscreenBtn = document.querySelector('.rider-actions .btn-secondary:nth-child(3)');
        
        // 数据刷新按钮
        if (refreshBtn) {
            refreshBtn.addEventListener('click', function() {
                loadRiderOverviewData();
                updateDataTime();
            });
        }
        
        // 导出数据按钮
        if (exportBtn) {
            exportBtn.addEventListener('click', function() {
                exportRiderOverviewData();
            });
        }
        
        // 全屏按钮
        if (fullscreenBtn) {
            fullscreenBtn.addEventListener('click', function() {
                toggleFullscreen();
            });
        }
    }
    
    // 更新数据时间
    function updateDataTime() {
        const dataUpdateInfo = document.querySelector('.data-update-info');
        if (dataUpdateInfo) {
            const now = new Date();
            const formattedDate = now.toLocaleString('zh-CN', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
            dataUpdateInfo.textContent = `数据更新时间：${formattedDate} 数据每20分钟自动更新`;
        }
    }
    
    // 导出运力总览数据
    function exportRiderOverviewData() {
        // 获取当前选择的城市
        const selectedCity = localStorage.getItem('selectedCity') || 'all';
        
        // 构建查询参数
        const queryParams = new URLSearchParams();
        queryParams.append('city', selectedCity);
        
        const queryString = queryParams.toString();
        const url = `${window.API_BASE_URL}/api/riders/overview${queryString ? `?${queryString}` : ''}`;
        
        // 从API获取运力总览数据
        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const overviewData = data.data;
                    
                    // 生成CSV内容
                    const headers = [
                        '站点名称', '规模数', '骑手数', '缺口数', '规模占比', 
                        '兼职骑手', '全职骑手数', '兼职骑手占比', '连续3天未跑单骑手', 
                        '昨日未跑单骑手', '今日出勤骑手数', '今日入职骑手数', 
                        '今日入职兼职数', '今日入职全职数'
                    ];
                    
                    const csvContent = [
                        headers.join(','),
                        ...overviewData.map(item => [
                            item.station_name || '',
                            item.scale_count || 0,
                            item.rider_count || 0,
                            item.gap_count || 0,
                            (item.scale_ratio || 0) + '%',
                            item.part_time_count || 0,
                            item.full_time_count || 0,
                            (item.part_time_ratio || 0) + '%',
                            item.three_days_no_order || 0,
                            item.yesterday_no_order || 0,
                            item.today_attendance || 0,
                            item.today_entry_count || 0,
                            item.today_entry_part_time || 0,
                            item.today_entry_full_time || 0
                        ].join(','))
                    ].join('\n');
                    
                    // 创建下载链接
                    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
                    const url = URL.createObjectURL(blob);
                    const link = document.createElement('a');
                    link.setAttribute('href', url);
                    link.setAttribute('download', `运力总览_${new Date().toISOString().split('T')[0]}.csv`);
                    link.style.visibility = 'hidden';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                }
            })
            .catch(error => {
                console.error('导出数据失败:', error);
                alert('导出数据失败，请重试');
            });
    }
    
    // 切换全屏
    function toggleFullscreen() {
        const element = document.documentElement;
        if (!document.fullscreenElement) {
            element.requestFullscreen().catch(err => {
                console.error('无法进入全屏模式:', err);
            });
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            }
        }
    }

    // 解析CSV文件
    function parseCSV(csvContent) {
        const lines = csvContent.split('\n');
        const headers = lines[0].split(',').map(header => header.trim());
        const riders = [];
        
        for (let i = 1; i < lines.length; i++) {
            const line = lines[i].trim();
            if (!line) continue;
            
            const values = line.split(',').map(value => value.trim());
            if (values.length < headers.length) continue;
            
            const rider = {};
            headers.forEach((header, index) => {
                rider[header] = values[index];
            });
            
            // 根据身份证号自动填充出生日期
            const idCard = rider['身份证号'] || rider['id_card'];
            const birthDate = rider['出生日期'] || rider['birth_date'];
            if (idCard && !birthDate) {
                const extractedBirthDate = extractBirthDateFromIdCard(idCard);
                if (extractedBirthDate) {
                    rider['出生日期'] = extractedBirthDate;
                    rider['birth_date'] = extractedBirthDate;
                }
            }
            
            riders.push(rider);
        }
        
        return riders;
    }
    
    // 下载导入模板
    function downloadImportTemplate() {
        // 生成CSV模板内容
        const headers = [
            '城市', '骑手风神ID', '姓名', '手机号', '站点名称', '首跑日期', '入职日期',
            '工作性质', '单价', '结算周期', '身份证号', '出生日期', '招聘渠道',
            '三方/内推姓名', '薪资方案绑定', '紧急联系人电话号码', '岗位状态',
            '离职日期', '离岗日期', '人员标签', '备注', '合同状态'
        ];
        
        // 添加示例数据行
        const exampleData = [
            'hangzhou', '100001', '张三', '13800138001', '杭州西湖站', '2024-01-01', '2024-01-01',
            '全职', '5.00', '周结', '110101199001011234', '1990-01-01', '内推',
            '李四', 'SALARY001', '13900139001', '在职', '', '', '新人', '无', '已签约'
        ];
        
        const csvContent = [
            headers.join(','),
            exampleData.join(',')
        ].join('\n');
        
        // 创建下载链接
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.setAttribute('href', url);
        link.setAttribute('download', `骑手导入模板_${new Date().toISOString().split('T')[0]}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    // 上传骑手数据
    function uploadRiders(riders) {
        // 上传数据到服务器
        fetch('${window.API_BASE_URL}/api/riders/batch', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ riders })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(`成功导入 ${data.imported} 条数据`);
                loadRiderRosterData();
            } else {
                alert('导入失败: ' + data.error);
            }
        })
        .catch(error => {
            console.error('上传失败:', error);
            alert('网络错误，请稍后重试');
        });
    }
    
    // 加载骑手统计数据
    function loadRiderStats() {
        const statCards = document.querySelectorAll('.stat-card');
        if (!statCards.length) return;
        
        // 获取当前选择的城市
        const selectedCity = localStorage.getItem('selectedCity') || 'all';
        
        fetch(`${window.API_BASE_URL}/api/riders/stats?city=${selectedCity}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const stats = data.data;
                    const statValues = [
                        stats.active,
                        stats.full_time,
                        stats.part_time,
                        stats.new_riders,
                        stats.today_entry,
                        stats.no_first_run,
                        stats.abnormal
                    ];
                    
                    statCards.forEach((card, index) => {
                        if (index < statValues.length) {
                            card.classList.remove('loading');
                            card.querySelector('p').textContent = statValues[index];
                        }
                    });
                }
            })
            .catch(error => {
                console.error('加载统计数据失败:', error);
            });
    }
    
    // 城市名称映射
    const cityMap = {
        'hangzhou': '杭州',
        'wuhan': '武汉',
        'shenyang': '沈阳',
        'jinhua': '金华',
        'shaoxing': '绍兴'
    };

    // 格式化值，将'none'转换为'-'
    function formatValue(value, fieldName, rider) {
        if (value === 'none' || value === null || value === undefined) {
            // 如果是出生日期字段且为空，尝试从身份证号提取
            if (fieldName === 'birth_date' || fieldName === '出生日期') {
                const idCard = rider && (rider.id_card || rider['身份证号']);
                if (idCard) {
                    const extractedBirthDate = extractBirthDateFromIdCard(idCard);
                    if (extractedBirthDate) {
                        return extractedBirthDate;
                    }
                }
            }
            // 薪资方案绑定默认显示为'-'
            if (fieldName === 'salary_plan_id' || fieldName === '薪资方案绑定') {
                return '<span class="salary-plan">-</span>';
            }
            // 合同状态默认显示为未签订
            if (fieldName === 'contract_status' || fieldName === '合同状态') {
                return '<span class="contract-status not-signed">未签订</span>';
            }
            return '-';
        }
        // 格式化城市名称
        if (fieldName === 'city' || fieldName === '城市') {
            return cityMap[value] || value;
        }
        // 格式化日期
        if (typeof value === 'string' && value.includes('T') && !isNaN(Date.parse(value))) {
            const date = new Date(value);
            return date.toLocaleDateString('zh-CN');
        }
        // 格式化薪资方案绑定
        if (fieldName === 'salary_plan_id' || fieldName === '薪资方案绑定') {
            return '<span class="salary-plan">' + value + '</span>';
        }
        // 格式化合同状态为按钮
        if (fieldName === 'contract_status' || fieldName === '合同状态') {
            const statusClass = value === 'signed' || value === '已签订' ? 'signed' : 'not-signed';
            const displayValue = value === 'signed' ? '已签订' : value;
            return '<button class="contract-status-btn contract-status ' + statusClass + '" data-rider-id="' + (rider && rider.rider_id) + '">' + displayValue + '</button>';
        }
        return value;
    }
    
    // 加载入离职汇总数据
    function loadEntryExitSummaryData(filters = {}) {
        const summaryTable = document.getElementById('entry-exit-summary-table');
        if (!summaryTable) return;
        
        const tbody = summaryTable.querySelector('tbody');
        tbody.innerHTML = `
            <tr>
                <td colspan="16" class="loading">
                    <p>加载中...</p>
                </td>
            </tr>
        `;
        
        // 获取当前选择的城市
        const selectedCity = filters.city_code || localStorage.getItem('selectedCity') || 'hangzhou';
        
        // 构建查询参数
        const queryParams = new URLSearchParams();
        queryParams.append('city_code', selectedCity);
        if (filters.station_name) queryParams.append('station_name', filters.station_name);
        if (filters.dimension) queryParams.append('dimension', filters.dimension);
        if (filters.start_date) queryParams.append('start_date', filters.start_date);
        if (filters.end_date) queryParams.append('end_date', filters.end_date);
        
        const queryString = queryParams.toString();
        const url = `${window.API_BASE_URL}/api/riders/entry-exit-summary${queryString ? `?${queryString}` : ''}`;
        
        // 从API获取入离职汇总数据
        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const summaryData = data.data;
                    tbody.innerHTML = '';
                    
                    summaryData.forEach((item, index) => {
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td><input type="checkbox"></td>
                            <td>${index + 1}</td>
                            <td>${item.station_name}</td>
                            <td>${item.entry_count}</td>
                            <td>${item.full_time_entry_count}</td>
                            <td>${item.referral_count}</td>
                            <td>${item.third_party_count}</td>
                            <td>${item.part_time_entry_count}</td>
                            <td>${item.exit_count}</td>
                            <td>${item.net_increase}</td>
                            <td>${item.entry_rate}%</td>
                            <td>${item.exit_rate}%</td>
                            <td>${item.active_count}</td>
                            <td>${item.pending_exit_full_time_count || 0}</td>
                            <td>${item.pending_exit_part_time_count || 0}</td>
                            <td>
                                <a href="#" class="action-link">详情</a>
                            </td>
                        `;
                        tbody.appendChild(row);
                    });
                } else {
                    tbody.innerHTML = `
                        <tr>
                            <td colspan="16">
                                <p>加载失败，请重试</p>
                            </td>
                        </tr>
                    `;
                }
            })
            .catch(error => {
                console.error('加载入离职汇总数据失败:', error);
                tbody.innerHTML = `
                    <tr>
                        <td colspan="16">
                            <p>网络错误，请稍后重试</p>
                        </td>
                    </tr>
                `;
            });
    }
    
    // 加载入职记录数据
    function loadEntryRecordsData(filters = {}) {
        const entryRecordsTable = document.getElementById('entry-records-table');
        if (!entryRecordsTable) return;
        
        const tbody = entryRecordsTable.querySelector('tbody');
        tbody.innerHTML = `
            <tr>
                <td colspan="11" class="loading">
                    <p>加载中...</p>
                </td>
            </tr>
        `;
        
        // 获取当前选择的城市
        const selectedCity = filters.city || localStorage.getItem('selectedCity') || 'all';
        
        // 构建查询参数
        const queryParams = new URLSearchParams();
        queryParams.append('city', selectedCity);
        if (filters.department) queryParams.append('department', filters.department);
        if (filters.entryType) queryParams.append('work_nature', filters.entryType);
        if (filters.source) {
            // 来源映射到招聘渠道
            const sourceMap = {
                'internal': '内推',
                'third-party': '三方',
                'direct': '直接招聘'
            };
            queryParams.append('recruitment_channel', sourceMap[filters.source] || filters.source);
        }
        if (filters.startDate) queryParams.append('start_date', filters.startDate);
        if (filters.endDate) queryParams.append('end_date', filters.endDate);
        
        const queryString = queryParams.toString();
        const url = `${window.API_BASE_URL}/api/riders${queryString ? `?${queryString}` : ''}`;
        
        // 从API获取骑手数据
        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const riders = data.data;
                    tbody.innerHTML = '';
                    
                    riders.forEach((rider, index) => {
                        const row = document.createElement('tr');
                        
                        // 入职类型
                        const entryType = rider.work_nature || '-';
                        
                        // 来源
                        let source = '-';
                        if (entryType === '全职' && rider.recruitment_channel) {
                            source = rider.recruitment_channel;
                        }
                        
                        // 状态
                        const status = rider.position_status || '-';
                        
                        row.innerHTML = `
                            <td><input type="checkbox" data-rider-id="${rider.rider_id}"></td>
                            <td>${index + 1}</td>
                            <td>${formatValue(rider.name, 'name', rider)}</td>
                            <td>${formatValue(rider.id_card, 'id_card', rider)}</td>
                            <td>${formatValue(rider.phone, 'phone', rider)}</td>
                            <td>${formatValue(rider.station_name, 'station_name', rider)}</td>
                            <td><span class="${entryType === '兼职' ? 'status-badge part-time' : entryType === '全职' ? 'status-badge full-time' : ''}">${entryType}</span></td>
                            <td>${source}</td>
                            <td>${formatValue(rider.entry_date, 'entry_date', rider)}</td>
                            <td>${status}</td>
                            <td>
                                <a href="#" class="action-link view-rider" data-rider-id="${rider.rider_id}">详情</a>
                            </td>
                        `;
                        tbody.appendChild(row);
                    });
                    
                    // 绑定详情事件
                    document.querySelectorAll('.view-rider').forEach(link => {
                        link.addEventListener('click', function(e) {
                            e.preventDefault();
                            const riderId = this.getAttribute('data-rider-id');
                            viewRider(riderId);
                        });
                    });
                } else {
                    tbody.innerHTML = `
                        <tr>
                            <td colspan="11">
                                <p>加载失败，请重试</p>
                            </td>
                        </tr>
                    `;
                }
            })
            .catch(error => {
                console.error('加载入职记录数据失败:', error);
                tbody.innerHTML = `
                    <tr>
                        <td colspan="11">
                            <p>网络错误，请稍后重试</p>
                        </td>
                    </tr>
                `;
            });
    }
    
    // 加载离职记录数据
    function loadExitRecordsData(filters = {}) {
        const exitRecordsTable = document.getElementById('exit-records-table');
        if (!exitRecordsTable) return;
        
        const tbody = exitRecordsTable.querySelector('tbody');
        tbody.innerHTML = `
            <tr>
                <td colspan="13" class="loading">
                    <p>加载中...</p>
                </td>
            </tr>
        `;
        
        // 获取当前选择的城市
        const selectedCity = filters.city || localStorage.getItem('selectedCity') || 'all';
        
        // 构建查询参数
        const queryParams = new URLSearchParams();
        queryParams.append('city', selectedCity);
        if (filters.department) queryParams.append('station_name', filters.department);
        if (filters.exitType) queryParams.append('exit_type', filters.exitType);
        if (filters.reason) queryParams.append('exit_reason', filters.reason);
        if (filters.startDate) queryParams.append('start_date', filters.startDate);
        if (filters.endDate) queryParams.append('end_date', filters.endDate);
        
        const queryString = queryParams.toString();
        const url = `${window.API_BASE_URL}/api/riders/exit-records${queryString ? `?${queryString}` : ''}`;
        
        // 从API获取离职记录数据
        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const exitRecords = data.data;
                    tbody.innerHTML = '';
                    
                    exitRecords.forEach((record, index) => {
                        const row = document.createElement('tr');
                        
                        row.innerHTML = `
                            <td><input type="checkbox" data-rider-id="${record.rider_id}"></td>
                            <td>${index + 1}</td>
                            <td>${formatValue(record.name, 'name', record)}</td>
                            <td>${formatValue(record.id_card, 'id_card', record)}</td>
                            <td>${formatValue(record.phone, 'phone', record)}</td>
                            <td>${formatValue(record.station_name, 'station_name', record)}</td>
                            <td>${record.exit_type || '-'}</td>
                            <td>${record.exit_reason || '-'}</td>
                            <td>${formatValue(record.entry_date, 'entry_date', record)}</td>
                            <td>${formatValue(record.exit_date, 'exit_date', record)}</td>
                            <td>${formatValue(record.leave_date, 'leave_date', record)}</td>
                            <td>${record.working_duration || '-'}</td>
                            <td>
                                <a href="#" class="action-link view-rider" data-rider-id="${record.rider_id}">详情</a>
                            </td>
                        `;
                        tbody.appendChild(row);
                    });
                    
                    // 绑定详情事件
                    document.querySelectorAll('.view-rider').forEach(link => {
                        link.addEventListener('click', function(e) {
                            e.preventDefault();
                            const riderId = this.getAttribute('data-rider-id');
                            viewRider(riderId);
                        });
                    });
                } else {
                    tbody.innerHTML = `
                        <tr>
                            <td colspan="13">
                                <p>加载失败，请重试</p>
                            </td>
                        </tr>
                    `;
                }
            })
            .catch(error => {
                console.error('加载离职记录数据失败:', error);
                tbody.innerHTML = `
                    <tr>
                        <td colspan="13">
                            <p>网络错误，请稍后重试</p>
                        </td>
                    </tr>
                `;
            });
    }
    
    // 绑定时间维度切换事件
    function bindTimeDimensionEvents() {
        const timeTabs = document.querySelectorAll('.time-tab');
        timeTabs.forEach(tab => {
            tab.addEventListener('click', function() {
                // 移除所有标签的active类
                timeTabs.forEach(t => t.classList.remove('active', 'btn-primary'));
                timeTabs.forEach(t => t.classList.add('btn-secondary'));
                // 添加当前标签的active类
                this.classList.add('active', 'btn-primary');
                this.classList.remove('btn-secondary');
                
                // 获取时间维度
                const dimension = this.getAttribute('data-dimension');
                // 重新加载数据
                loadEntryExitSummaryData({ dimension });
                loadThirdPartySummaryData();
                loadEntryExitTrendCharts({ dimension });
                loadThirdPartyAnalysisCharts();
            });
        });
    }
    
    // 绑定入离职筛选器事件
    function bindEntryExitFilterEvents() {
        const searchBtn = document.querySelector('.btn-search');
        const resetBtn = document.querySelector('.btn-reset');
        
        if (searchBtn) {
            searchBtn.addEventListener('click', function() {
                const filters = getEntryExitFilters();
                loadEntryExitSummaryData(filters);
                loadThirdPartySummaryData(filters);
                loadEntryExitTrendCharts(filters);
                loadThirdPartyAnalysisCharts(filters);
            });
        }
        
        if (resetBtn) {
            resetBtn.addEventListener('click', function() {
                resetEntryExitFilters();
                loadEntryExitSummaryData();
                loadThirdPartySummaryData();
                loadEntryExitTrendCharts();
                loadThirdPartyAnalysisCharts();
            });
        }
    }
    
    // 绑定入职记录筛选器事件
    function bindEntryRecordsFilterEvents() {
        const searchBtn = document.querySelector('.btn-search');
        const resetBtn = document.querySelector('.btn-reset');
        
        if (searchBtn) {
            searchBtn.addEventListener('click', function() {
                const filters = getEntryRecordsFilters();
                loadEntryRecordsData(filters);
                loadEntryTrendCharts(filters);
            });
        }
        
        if (resetBtn) {
            resetBtn.addEventListener('click', function() {
                resetEntryRecordsFilters();
                loadEntryRecordsData();
                loadEntryTrendCharts();
            });
        }
    }
    
    // 获取入职记录筛选条件
    function getEntryRecordsFilters() {
        const city = localStorage.getItem('selectedCity') || 'all';
        const department = document.getElementById('department-select').value;
        const entryType = document.getElementById('entry-type-select').value;
        const source = document.getElementById('source-select').value;
        const startDate = document.getElementById('start-date').value;
        const endDate = document.getElementById('end-date').value;
        
        return {
            city,
            department,
            entryType,
            source,
            startDate,
            endDate
        };
    }
    
    // 重置入职记录筛选条件
    function resetEntryRecordsFilters() {
        document.getElementById('department-select').value = '';
        document.getElementById('entry-type-select').value = '';
        document.getElementById('source-select').value = '';
        document.getElementById('start-date').value = '';
        document.getElementById('end-date').value = '';
    }
    
    // 获取入离职筛选条件
    function getEntryExitFilters() {
        const city_code = document.getElementById('city-select').value || localStorage.getItem('selectedCity') || 'hangzhou';
        const station_name = document.getElementById('department-select').value;
        const dimension = document.querySelector('.time-tab.active').getAttribute('data-dimension');
        const start_date = document.getElementById('start-date').value;
        const end_date = document.getElementById('end-date').value;
        
        return {
            city_code,
            station_name,
            dimension,
            start_date,
            end_date
        };
    }
    
    // 重置入离职筛选条件
    function resetEntryExitFilters() {
        document.getElementById('city-select').value = '';
        document.getElementById('department-select').value = '';
        document.getElementById('start-date').value = '';
        document.getElementById('end-date').value = '';
        // 重置时间维度为日维度
        const timeTabs = document.querySelectorAll('.time-tab');
        timeTabs.forEach(tab => {
            if (tab.getAttribute('data-dimension') === 'day') {
                tab.classList.add('active', 'btn-primary');
                tab.classList.remove('btn-secondary');
            } else {
                tab.classList.remove('active', 'btn-primary');
                tab.classList.add('btn-secondary');
            }
        });
    }
    
    // 页面加载完成后，绑定事件（数据加载已通过checkLoginStatus->updateCityData完成）
    if (window.location.pathname.includes('rider-roster.html')) {
        // 绑定事件
        bindFilterEvents();
        bindActionButtons();
    }
    
    // 加载三方表数据
    function loadThirdPartySummaryData(filters = {}) {
        const thirdPartyTable = document.getElementById('third-party-table');
        if (!thirdPartyTable) return;
        
        const tbody = thirdPartyTable.querySelector('tbody');
        tbody.innerHTML = `
            <tr>
                <td colspan="14" class="loading">
                    <p>加载中...</p>
                </td>
            </tr>
        `;
        
        // 获取当前选择的城市
        const selectedCity = filters.city_code || localStorage.getItem('selectedCity') || 'hangzhou';
        
        // 构建查询参数
        const queryParams = new URLSearchParams();
        queryParams.append('city_code', selectedCity);
        if (filters.station_name) queryParams.append('station_name', filters.station_name);
        if (filters.date) queryParams.append('date', filters.date);
        
        const queryString = queryParams.toString();
        const url = `${window.API_BASE_URL}/api/riders/third-party-summary${queryString ? `?${queryString}` : ''}`;
        
        // 从API获取三方表数据
        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const thirdPartyData = data.data;
                    tbody.innerHTML = '';
                    
                    thirdPartyData.forEach((item, index) => {
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td><input type="checkbox"></td>
                            <td>${index + 1}</td>
                            <td>${item.station_name || '-'}</td>
                            <td>${item.third_party_name || '-'}</td>
                            <td>${item.entry_count || 0}</td>
                            <td>${item.exit_count || 0}</td>
                            <td>${item.attrition_rate || 0}%</td>
                            <td>${item.retention_rate || 0}%</td>
                            <td>${item.pre_settlement_amount || '-'}</td>
                            <td>${item.pre_settlement_attrition_amount || '-'}</td>
                            <td>${item.settled_amount || '-'}</td>
                            <td>${item.settled_attrition_amount || '-'}</td>
                            <td>${item.unsettled_amount || '-'}</td>
                            <td>
                                <button class="btn btn-sm btn-primary">详情</button>
                            </td>
                        `;
                        tbody.appendChild(row);
                    });
                } else {
                    tbody.innerHTML = `
                        <tr>
                            <td colspan="14">
                                <p>数据加载失败: ${data.error || '未知错误'}</p>
                            </td>
                        </tr>
                    `;
                }
            })
            .catch(error => {
                console.error('加载三方表数据失败:', error);
                tbody.innerHTML = `
                    <tr>
                        <td colspan="14">
                            <p>网络错误，请稍后重试</p>
                        </td>
                    </tr>
                `;
            });
    }

    // 加载入离职趋势图表
    function loadEntryExitTrendCharts(filters = {}) {
        // 获取查询参数
        const city_code = filters.city_code || localStorage.getItem('selectedCity') || 'hangzhou';
        const dimension = filters.dimension || document.querySelector('.time-tab.active').getAttribute('data-dimension') || 'day';
        
        // 构建查询参数
        const queryParams = new URLSearchParams();
        queryParams.append('city_code', city_code);
        queryParams.append('dimension', dimension);
        
        const url = `${window.API_BASE_URL}/api/riders/entry-exit-trend?${queryParams.toString()}`;
        
        // 从API获取趋势数据
        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const trendData = data.data;
                    
                    // 准备图表数据
                    const labels = trendData.map(item => item.date);
                    const entryCounts = trendData.map(item => item.entry_count || 0);
                    const exitCounts = trendData.map(item => item.exit_count || 0);
                    
                    // 渲染入离职趋势图
                    const trendChartCtx = document.getElementById('entry-exit-trend-chart').getContext('2d');
                    if (window.entryExitTrendChart) {
                        window.entryExitTrendChart.destroy();
                    }
                    window.entryExitTrendChart = new Chart(trendChartCtx, {
                        type: 'line',
                        data: {
                            labels: labels,
                            datasets: [
                                {
                                    label: '入职人数',
                                    data: entryCounts,
                                    borderColor: '#3b82f6',
                                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                                    borderWidth: 2,
                                    fill: true,
                                    tension: 0.4
                                },
                                {
                                    label: '离职人数',
                                    data: exitCounts,
                                    borderColor: '#ef4444',
                                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                                    borderWidth: 2,
                                    fill: true,
                                    tension: 0.4
                                }
                            ]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                title: {
                                    display: true,
                                    text: '入离职人数趋势',
                                    font: {
                                        size: 16
                                    }
                                },
                                legend: {
                                    position: 'top'
                                }
                            },
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    title: {
                                        display: true,
                                        text: '人数'
                                    }
                                },
                                x: {
                                    title: {
                                        display: true,
                                        text: '日期'
                                    }
                                }
                            }
                        }
                    });
                    
                    // 计算入职率和离职率
                    const totalEntries = entryCounts.reduce((sum, count) => sum + count, 0);
                    const totalExits = exitCounts.reduce((sum, count) => sum + count, 0);
                    const activeCount = totalEntries - totalExits;
                    const entryRate = activeCount > 0 ? (totalEntries / activeCount * 100) : 0;
                    const exitRate = activeCount > 0 ? (totalExits / activeCount * 100) : 0;
                    
                    // 渲染入离职率图表
                    const rateChartCtx = document.getElementById('entry-exit-rate-chart').getContext('2d');
                    if (window.entryExitRateChart) {
                        window.entryExitRateChart.destroy();
                    }
                    window.entryExitRateChart = new Chart(rateChartCtx, {
                        type: 'bar',
                        data: {
                            labels: ['入职率', '离职率'],
                            datasets: [{
                                label: '百分比',
                                data: [entryRate, exitRate],
                                backgroundColor: ['#3b82f6', '#ef4444'],
                                borderColor: ['#3b82f6', '#ef4444'],
                                borderWidth: 1
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                title: {
                                    display: true,
                                    text: '入离职率分析',
                                    font: {
                                        size: 16
                                    }
                                }
                            },
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    max: 100,
                                    title: {
                                        display: true,
                                        text: '百分比 (%)'
                                    }
                                }
                            }
                        }
                    });
                }
            })
            .catch(error => {
                console.error('加载入离职趋势数据失败:', error);
            });
    }
    
    // 加载三方中介分析图表
    function loadThirdPartyAnalysisCharts(filters = {}) {
        // 获取查询参数
        const city_code = filters.city_code || localStorage.getItem('selectedCity') || 'hangzhou';
        
        // 构建查询参数
        const queryParams = new URLSearchParams();
        queryParams.append('city_code', city_code);
        
        const url = `${window.API_BASE_URL}/api/riders/third-party-analysis?${queryParams.toString()}`;
        
        // 从API获取三方分析数据
        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const thirdPartyData = data.data;
                    
                    // 准备图表数据
                    const stationNames = thirdPartyData.map(item => item.station_name);
                    const entryCounts = thirdPartyData.map(item => item.entry_count || 0);
                    const exitCounts = thirdPartyData.map(item => item.exit_count || 0);
                    
                    // 渲染三方入职人数图表
                    const entryChartCtx = document.getElementById('third-party-entry-chart').getContext('2d');
                    if (window.thirdPartyEntryChart) {
                        window.thirdPartyEntryChart.destroy();
                    }
                    window.thirdPartyEntryChart = new Chart(entryChartCtx, {
                        type: 'bar',
                        data: {
                            labels: stationNames,
                            datasets: [{
                                label: '三方入职人数',
                                data: entryCounts,
                                backgroundColor: '#10b981',
                                borderColor: '#10b981',
                                borderWidth: 1
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                title: {
                                    display: true,
                                    text: '各站点三方入职人数',
                                    font: {
                                        size: 16
                                    }
                                }
                            },
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    title: {
                                        display: true,
                                        text: '人数'
                                    }
                                },
                                x: {
                                    title: {
                                        display: true,
                                        text: '站点'
                                    }
                                }
                            }
                        }
                    });
                    
                    // 计算流失率
                    const attritionRates = thirdPartyData.map(item => {
                        const total = item.total_count || 1;
                        return (item.exit_count || 0) / total * 100;
                    });
                    
                    // 渲染三方流失率图表
                    const attritionChartCtx = document.getElementById('third-party-attrition-chart').getContext('2d');
                    if (window.thirdPartyAttritionChart) {
                        window.thirdPartyAttritionChart.destroy();
                    }
                    window.thirdPartyAttritionChart = new Chart(attritionChartCtx, {
                        type: 'bar',
                        data: {
                            labels: stationNames,
                            datasets: [{
                                label: '三方流失率',
                                data: attritionRates,
                                backgroundColor: '#f59e0b',
                                borderColor: '#f59e0b',
                                borderWidth: 1
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                title: {
                                    display: true,
                                    text: '各站点三方流失率',
                                    font: {
                                        size: 16
                                    }
                                }
                            },
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    max: 100,
                                    title: {
                                        display: true,
                                        text: '流失率 (%)'
                                    }
                                },
                                x: {
                                    title: {
                                        display: true,
                                        text: '站点'
                                    }
                                }
                            }
                        }
                    });
                }
            })
            .catch(error => {
                console.error('加载三方中介分析数据失败:', error);
            });
    }

    // 导出入离职汇总数据
    function exportEntryExitSummaryData() {
        const filters = getEntryExitFilters();
        
        // 构建查询参数
        const queryParams = new URLSearchParams();
        queryParams.append('city_code', filters.city_code);
        if (filters.station_name) queryParams.append('station_name', filters.station_name);
        if (filters.dimension) queryParams.append('dimension', filters.dimension);
        if (filters.start_date) queryParams.append('start_date', filters.start_date);
        if (filters.end_date) queryParams.append('end_date', filters.end_date);
        
        const queryString = queryParams.toString();
        const url = `${window.API_BASE_URL}/api/riders/entry-exit-summary${queryString ? `?${queryString}` : ''}`;
        
        // 从API获取数据
        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const summaryData = data.data;
                    if (summaryData.length === 0) {
                        alert('没有数据可导出');
                        return;
                    }
                    
                    // 生成CSV内容
                    const headers = [
                        '站点名称', '入职人数', '全职入职人数', '内推', '三方', '兼职入职人数',
                        '离职人数', '净增人数', '入职率', '离职率', '在职人数'
                    ];
                    
                    const csvContent = [
                        headers.join(','),
                        ...summaryData.map(item => [
                            item.station_name,
                            item.entry_count,
                            item.full_time_entry_count,
                            item.referral_count,
                            item.third_party_count,
                            item.part_time_entry_count,
                            item.exit_count,
                            item.net_increase,
                            item.entry_rate + '%',
                            item.exit_rate + '%',
                            item.active_count
                        ].join(','))
                    ].join('\n');
                    
                    // 创建下载链接
                    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
                    const url = URL.createObjectURL(blob);
                    const link = document.createElement('a');
                    link.setAttribute('href', url);
                    link.setAttribute('download', `入离职汇总表_${new Date().toISOString().split('T')[0]}.csv`);
                    link.style.visibility = 'hidden';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                } else {
                    alert('导出失败，请重试');
                }
            })
            .catch(error => {
                console.error('导出数据失败:', error);
                alert('网络错误，请稍后重试');
            });
    }

    // 绑定入离职页面的操作按钮事件
    function bindEntryExitActionButtons() {
        // 导出数据
        const exportBtn = document.querySelector('.rider-actions button');
        if (exportBtn && exportBtn.textContent.trim() === '导出数据') {
            exportBtn.addEventListener('click', function() {
                exportEntryExitSummaryData();
            });
        } else {
            // 尝试通过其他方式查找导出按钮
            const buttons = document.querySelectorAll('.rider-actions button');
            buttons.forEach(button => {
                if (button.textContent.trim() === '导出数据') {
                    button.addEventListener('click', function() {
                        exportEntryExitSummaryData();
                    });
                }
            });
        }
    }

    // 加载兼职骑手列表数据
    function loadPartTimeRiderData(filters = {}) {
        const partTimeTable = document.getElementById('part-time-rider-table');
        if (!partTimeTable) return;
        
        const tbody = partTimeTable.querySelector('tbody');
        tbody.innerHTML = `
            <tr>
                <td colspan="13" class="loading">
                    <p>加载中...</p>
                </td>
            </tr>
        `;
        
        // 获取当前选择的城市
        const selectedCity = filters.city || localStorage.getItem('selectedCity') || 'hangzhou';
        
        // 构建查询参数
        const queryParams = new URLSearchParams();
        queryParams.append('city', selectedCity);
        queryParams.append('work_nature', '兼职');
        if (filters.station) queryParams.append('department', filters.station);
        if (filters.search) queryParams.append('search', filters.search);
        if (filters.startDate) queryParams.append('start_date', filters.startDate);
        if (filters.endDate) queryParams.append('end_date', filters.endDate);
        
        const queryString = queryParams.toString();
        const url = `${window.API_BASE_URL}/api/riders${queryString ? `?${queryString}` : ''}`;
        
        // 从API获取骑手数据
        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const riders = data.data;
                    tbody.innerHTML = '';
                    
                    riders.forEach((rider, index) => {
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td><input type="checkbox" data-rider-id="${rider.rider_id}"></td>
                            <td>${index + 1}</td>
                            <td>${formatValue(rider.city, 'city', rider)}</td>
                            <td>${formatValue(rider.settlement_cycle, 'settlement_cycle', rider)}</td>
                            <td>-</td>
                            <td>${formatValue(rider.station_name, 'station_name', rider)}</td>
                            <td>${formatValue(rider.rider_id, 'rider_id', rider)}</td>
                            <td>${formatValue(rider.name, 'name', rider)}</td>
                            <td>高价兼职</td>
                            <td>${formatValue(rider.unit_price, 'unit_price', rider)}</td>
                            <td>-</td>
                            <td>${formatValue(rider.salary_plan_id, 'salary_plan_id', rider)}</td>
                            <td>
                                <a href="#" class="action-link edit-rider" data-rider-id="${rider.rider_id}">编辑</a>
                                <a href="#" class="action-link view-rider" data-rider-id="${rider.rider_id}">详情</a>
                            </td>
                        `;
                        tbody.appendChild(row);
                    });
                    
                    // 绑定编辑和详情事件
                    bindPartTimeRiderActions();
                } else {
                    tbody.innerHTML = `
                        <tr>
                            <td colspan="13">
                                <p>加载失败，请重试</p>
                            </td>
                        </tr>
                    `;
                }
            })
            .catch(error => {
                console.error('加载兼职骑手数据失败:', error);
                tbody.innerHTML = `
                    <tr>
                        <td colspan="13">
                            <p>网络错误，请稍后重试</p>
                        </td>
                    </tr>
                `;
            });
    }

    // 绑定兼职骑手操作事件
    function bindPartTimeRiderActions() {
        // 编辑事件
        document.querySelectorAll('.edit-rider').forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const riderId = this.getAttribute('data-rider-id');
                editRider(riderId);
            });
        });
        
        // 详情事件
        document.querySelectorAll('.view-rider').forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const riderId = this.getAttribute('data-rider-id');
                viewRider(riderId);
            });
        });
    }

    // 绑定兼职骑手页面的操作按钮事件
    function bindPartTimeActionButtons() {
        const partTimePage = document.getElementById('rider-part-time-page');
        if (!partTimePage) return;
        
        // 批量设置工作性质
        const batchWorkNatureBtn = document.querySelector('.rider-actions button');
        if (batchWorkNatureBtn) {
            const buttons = document.querySelectorAll('.rider-actions button');
            buttons.forEach(button => {
                if (button.textContent.trim() === '批量设置工作性质') {
                    button.addEventListener('click', function() {
                        alert('批量设置工作性质功能开发中');
                    });
                } else if (button.textContent.trim() === '批量设置首跑日期') {
                    button.addEventListener('click', function() {
                        alert('批量设置首跑日期功能开发中');
                    });
                } else if (button.textContent.trim() === '批量设置招聘渠道') {
                    button.addEventListener('click', function() {
                        alert('批量设置招聘渠道功能开发中');
                    });
                } else if (button.textContent.trim() === '自动更新首跑骑手信息') {
                    button.addEventListener('click', function() {
                        alert('自动更新首跑骑手信息功能开发中');
                    });
                } else if (button.textContent.trim() === '下载导入模板') {
                    button.addEventListener('click', function() {
                        downloadImportTemplate();
                    });
                } else if (button.textContent.trim() === '导入骑手信息') {
                    button.addEventListener('click', function() {
                        importRiderData();
                    });
                } else if (button.textContent.trim() === '导出数据') {
                    button.addEventListener('click', function() {
                        exportPartTimeRiderData();
                    });
                } else if (button.textContent.trim() === '全屏') {
                    button.addEventListener('click', function() {
                        alert('全屏功能开发中');
                    });
                }
            });
        }
    }

    // 导出兼职骑手数据
    function exportPartTimeRiderData() {
        const selectedCity = localStorage.getItem('selectedCity') || 'hangzhou';
        
        // 构建查询参数
        const queryParams = new URLSearchParams();
        queryParams.append('city', selectedCity);
        queryParams.append('work_nature', '兼职');
        
        const queryString = queryParams.toString();
        const url = `${window.API_BASE_URL}/api/riders${queryString ? `?${queryString}` : ''}`;
        
        // 从API获取数据
        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const riders = data.data;
                    if (riders.length === 0) {
                        alert('没有数据可导出');
                        return;
                    }
                    
                    // 生成CSV内容
                    const headers = [
                        '城市', '结算周期', '站点名称', '骑手ID', '骑手姓名', '人员类别', '单价', '结算方案'
                    ];
                    
                    const csvContent = [
                        headers.join(','),
                        ...riders.map(rider => [
                            formatValue(rider.city, 'city', rider),
                            formatValue(rider.settlement_cycle, 'settlement_cycle', rider),
                            formatValue(rider.station_name, 'station_name', rider),
                            rider.rider_id,
                            rider.name,
                            '高价兼职',
                            rider.unit_price || '-',
                            formatValue(rider.salary_plan_id, 'salary_plan_id', rider)
                        ].join(','))
                    ].join('\n');
                    
                    // 创建下载链接
                    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
                    const url = URL.createObjectURL(blob);
                    const link = document.createElement('a');
                    link.setAttribute('href', url);
                    link.setAttribute('download', `兼职骑手列表_${new Date().toISOString().split('T')[0]}.csv`);
                    link.style.visibility = 'hidden';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                } else {
                    alert('导出失败，请重试');
                }
            })
            .catch(error => {
                console.error('导出数据失败:', error);
                alert('网络错误，请稍后重试');
            });
    }

    // 页面加载完成后，绑定事件（数据加载已通过checkLoginStatus->updateCityData完成）
    if (window.location.pathname.includes('rider-entry-exit-summary.html')) {
        // 绑定时间维度切换事件
        bindTimeDimensionEvents();
        // 绑定筛选器事件
        bindEntryExitFilterEvents();
        // 绑定操作按钮事件
        bindEntryExitActionButtons();
    }
    
    // 绑定兼职骑手页面的筛选器事件
    function bindPartTimeFilterEvents() {
        const searchBtn = document.querySelector('.btn-search');
        const resetBtn = document.querySelector('.btn-reset');
        
        if (searchBtn) {
            searchBtn.addEventListener('click', function() {
                const filters = getPartTimeFilters();
                loadPartTimeRiderData(filters);
            });
        }
        
        if (resetBtn) {
            resetBtn.addEventListener('click', function() {
                resetPartTimeFilters();
                loadPartTimeRiderData();
            });
        }
    }
    
    // 获取兼职骑手筛选条件
    function getPartTimeFilters() {
        const organization = document.querySelector('input[placeholder="请选择关键字搜索，用英文,隔开"]').value;
        const station = document.querySelector('select').value;
        const search = document.querySelector('input[placeholder="请输入风神ID、姓名、电话号码"]').value;
        const startDate = document.querySelectorAll('input[type="datetime-local"]')[0].value;
        const endDate = document.querySelectorAll('input[type="datetime-local"]')[1].value;
        const city = localStorage.getItem('selectedCity') || 'hangzhou';
        
        return {
            city,
            organization,
            station,
            search,
            startDate,
            endDate
        };
    }
    
    // 重置兼职骑手筛选条件
    function resetPartTimeFilters() {
        document.querySelector('input[placeholder="请选择关键字搜索，用英文,隔开"]').value = '';
        document.querySelector('select').value = '';
        document.querySelector('input[placeholder="请输入风神ID、姓名、电话号码"]').value = '';
        document.querySelectorAll('input[type="datetime-local"]')[0].value = '';
        document.querySelectorAll('input[type="datetime-local"]')[1].value = '';
    }
    
    // 页面加载完成后，绑定事件（数据加载已通过checkLoginStatus->updateCityData完成）
    if (window.location.pathname.includes('rider-part-time.html')) {
        // 绑定操作按钮事件
        bindPartTimeActionButtons();
        // 绑定筛选器事件
        bindPartTimeFilterEvents();
    }
    
    // 加载入职趋势图表
    function loadEntryTrendCharts(filters = {}) {
        const trendChartCtx = document.getElementById('entry-trend-chart');
        const typeChartCtx = document.getElementById('entry-type-chart');
        
        if (!trendChartCtx || !typeChartCtx) return;
        
        // 获取当前选择的城市
        const selectedCity = filters.city || localStorage.getItem('selectedCity') || 'all';
        
        // 构建查询参数
        const queryParams = new URLSearchParams();
        queryParams.append('city', selectedCity);
        if (filters.startDate) queryParams.append('start_date', filters.startDate);
        if (filters.endDate) queryParams.append('end_date', filters.endDate);
        
        const queryString = queryParams.toString();
        const url = `${window.API_BASE_URL}/api/riders${queryString ? `?${queryString}` : ''}`;
        
        // 从API获取骑手数据
        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const riders = data.data;
                    
                    // 处理入职趋势数据
                    const entryData = {};
                    riders.forEach(rider => {
                        if (rider.entry_date) {
                            const date = rider.entry_date.split('T')[0];
                            if (!entryData[date]) {
                                entryData[date] = {
                                    total: 0,
                                    fullTime: 0,
                                    partTime: 0
                                };
                            }
                            entryData[date].total++;
                            if (rider.work_nature === '全职') {
                                entryData[date].fullTime++;
                            } else if (rider.work_nature === '兼职') {
                                entryData[date].partTime++;
                            }
                        }
                    });
                    
                    // 排序日期
                    const sortedDates = Object.keys(entryData).sort();
                    const dates = sortedDates;
                    const totalEntries = sortedDates.map(date => entryData[date].total);
                    const fullTimeEntries = sortedDates.map(date => entryData[date].fullTime);
                    const partTimeEntries = sortedDates.map(date => entryData[date].partTime);
                    
                    // 渲染入职趋势图表
                    if (window.entryTrendChart) {
                        window.entryTrendChart.destroy();
                    }
                    window.entryTrendChart = new Chart(trendChartCtx, {
                        type: 'line',
                        data: {
                            labels: dates,
                            datasets: [
                                {
                                    label: '总入职数',
                                    data: totalEntries,
                                    borderColor: '#3b82f6',
                                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                                    borderWidth: 2,
                                    fill: true,
                                    tension: 0.4
                                },
                                {
                                    label: '全职入职',
                                    data: fullTimeEntries,
                                    borderColor: '#10b981',
                                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                                    borderWidth: 2,
                                    fill: true,
                                    tension: 0.4
                                },
                                {
                                    label: '兼职入职',
                                    data: partTimeEntries,
                                    borderColor: '#f59e0b',
                                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                                    borderWidth: 2,
                                    fill: true,
                                    tension: 0.4
                                }
                            ]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                title: {
                                    display: true,
                                    text: '入职人数趋势',
                                    font: {
                                        size: 16
                                    }
                                },
                                legend: {
                                    position: 'top'
                                }
                            },
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    title: {
                                        display: true,
                                        text: '人数'
                                    }
                                },
                                x: {
                                    title: {
                                        display: true,
                                        text: '日期'
                                    }
                                }
                            }
                        }
                    });
                    
                    // 处理入职类型分布数据
                    const typeData = {
                        fullTime: 0,
                        partTime: 0
                    };
                    riders.forEach(rider => {
                        if (rider.work_nature === '全职') {
                            typeData.fullTime++;
                        } else if (rider.work_nature === '兼职') {
                            typeData.partTime++;
                        }
                    });
                    
                    // 渲染入职类型分布图表
                    if (window.entryTypeChart) {
                        window.entryTypeChart.destroy();
                    }
                    window.entryTypeChart = new Chart(typeChartCtx, {
                        type: 'pie',
                        data: {
                            labels: ['全职', '兼职'],
                            datasets: [{
                                data: [typeData.fullTime, typeData.partTime],
                                backgroundColor: ['#10b981', '#f59e0b'],
                                borderColor: ['#10b981', '#f59e0b'],
                                borderWidth: 1
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                title: {
                                    display: true,
                                    text: '入职类型分布',
                                    font: {
                                        size: 16
                                    }
                                },
                                legend: {
                                    position: 'bottom'
                                }
                            }
                        }
                    });
                }
            })
            .catch(error => {
                console.error('加载入职趋势数据失败:', error);
            });
    }
    
    // 检查是否是入职记录页面
    if (window.location.pathname.includes('rider-entry-records.html')) {
        // 绑定入职记录筛选器事件
        bindEntryRecordsFilterEvents();
    }
    
    // 绑定离职记录筛选器事件
    function bindExitRecordsFilterEvents() {
        const searchBtn = document.querySelector('.btn-search');
        const resetBtn = document.querySelector('.btn-reset');
        
        if (searchBtn) {
            searchBtn.addEventListener('click', function() {
                const filters = getExitRecordsFilters();
                loadExitRecordsData(filters);
                loadExitTrendCharts(filters);
            });
        }
        
        if (resetBtn) {
            resetBtn.addEventListener('click', function() {
                resetExitRecordsFilters();
                loadExitRecordsData();
                loadExitTrendCharts();
            });
        }
    }
    
    // 获取离职记录筛选条件
    function getExitRecordsFilters() {
        const city = localStorage.getItem('selectedCity') || 'all';
        const department = document.getElementById('department-select').value;
        const exitType = document.getElementById('exit-type-select').value;
        const reason = document.getElementById('reason-select').value;
        const startDate = document.getElementById('start-date').value;
        const endDate = document.getElementById('end-date').value;
        
        return {
            city,
            department,
            exitType,
            reason,
            startDate,
            endDate
        };
    }
    
    // 重置离职记录筛选条件
    function resetExitRecordsFilters() {
        document.getElementById('department-select').value = '';
        document.getElementById('exit-type-select').value = '';
        document.getElementById('reason-select').value = '';
        document.getElementById('start-date').value = '';
        document.getElementById('end-date').value = '';
    }
    
    // 加载离职趋势图表
    function loadExitTrendCharts(filters = {}) {
        const chartContainers = document.querySelectorAll('.chart-wrapper');
        if (chartContainers.length < 2) return;
        
        const trendChartCtx = chartContainers[0].querySelector('canvas');
        if (!trendChartCtx) {
            chartContainers[0].innerHTML = '<canvas id="exit-trend-chart"></canvas>';
        }
        
        const typeChartCtx = chartContainers[1].querySelector('canvas');
        if (!typeChartCtx) {
            chartContainers[1].innerHTML = '<canvas id="exit-type-chart"></canvas>';
        }
        
        const selectedCity = filters.city || localStorage.getItem('selectedCity') || 'all';
        
        // 构建查询参数
        const queryParams = new URLSearchParams();
        queryParams.append('city', selectedCity);
        if (filters.startDate) queryParams.append('start_date', filters.startDate);
        if (filters.endDate) queryParams.append('end_date', filters.endDate);
        
        const queryString = queryParams.toString();
        const url = `${window.API_BASE_URL}/api/riders/exit-records${queryString ? `?${queryString}` : ''}`;
        
        // 从API获取离职记录数据
        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const records = data.data;
                    
                    // 处理离职趋势数据
                    const exitData = {};
                    records.forEach(record => {
                        if (record.exit_date) {
                            const date = record.exit_date.split('T')[0];
                            if (!exitData[date]) {
                                exitData[date] = 0;
                            }
                            exitData[date]++;
                        }
                    });
                    
                    // 排序日期
                    const sortedDates = Object.keys(exitData).sort();
                    const dates = sortedDates;
                    const totalExits = sortedDates.map(date => exitData[date]);
                    
                    // 渲染离职趋势图表
                    const trendCanvas = document.getElementById('exit-trend-chart');
                    if (trendCanvas) {
                        if (window.exitTrendChart) {
                            window.exitTrendChart.destroy();
                        }
                        window.exitTrendChart = new Chart(trendCanvas, {
                            type: 'line',
                            data: {
                                labels: dates,
                                datasets: [{
                                    label: '离职人数',
                                    data: totalExits,
                                    borderColor: '#3b82f6',
                                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                                    tension: 0.4,
                                    fill: true,
                                    borderWidth: 2,
                                    pointBackgroundColor: '#3b82f6',
                                    pointBorderColor: '#ffffff',
                                    pointBorderWidth: 2,
                                    pointRadius: 4,
                                    pointHoverRadius: 6
                                }]
                            },
                            options: {
                                responsive: true,
                                maintainAspectRatio: false,
                                plugins: {
                                    title: {
                                        display: true,
                                        text: '离职趋势分析',
                                        font: {
                                            size: 18,
                                            weight: 'bold',
                                            family: 'Arial, sans-serif'
                                        },
                                        color: '#1e293b'
                                    },
                                    legend: {
                                        display: true,
                                        position: 'top',
                                        labels: {
                                            font: {
                                                size: 12,
                                                family: 'Arial, sans-serif'
                                            },
                                            color: '#475569'
                                        }
                                    }
                                },
                                scales: {
                                    x: {
                                        title: {
                                            display: true,
                                            text: '日期',
                                            font: {
                                                size: 14,
                                                weight: 'bold',
                                                family: 'Arial, sans-serif'
                                            },
                                            color: '#475569'
                                        },
                                        grid: {
                                            color: 'rgba(226, 232, 240, 0.5)'
                                        },
                                        ticks: {
                                            font: {
                                                size: 12,
                                                family: 'Arial, sans-serif'
                                            },
                                            color: '#64748b'
                                        }
                                    },
                                    y: {
                                        title: {
                                            display: true,
                                            text: '人数',
                                            font: {
                                                size: 14,
                                                weight: 'bold',
                                                family: 'Arial, sans-serif'
                                            },
                                            color: '#475569'
                                        },
                                        grid: {
                                            color: 'rgba(226, 232, 240, 0.5)'
                                        },
                                        ticks: {
                                            font: {
                                                size: 12,
                                                family: 'Arial, sans-serif'
                                            },
                                            color: '#64748b'
                                        },
                                        beginAtZero: true
                                    }
                                },
                                interaction: {
                                    intersect: false,
                                    mode: 'index'
                                },
                                elements: {
                                    line: {
                                        tension: 0.4
                                    }
                                }
                            }
                        });
                    }
                    
                    // 处理离职类型分布数据
                    const typeData = {
                        '主动离职': 0,
                        '被动离职': 0
                    };
                    records.forEach(record => {
                        const exitType = record.exit_type || '被动离职';
                        if (typeData.hasOwnProperty(exitType)) {
                            typeData[exitType]++;
                        }
                    });
                    
                    // 渲染离职类型分布图表
                    const typeCanvas = document.getElementById('exit-type-chart');
                    if (typeCanvas) {
                        if (window.exitTypeChart) {
                            window.exitTypeChart.destroy();
                        }
                        window.exitTypeChart = new Chart(typeCanvas, {
                            type: 'pie',
                            data: {
                                labels: ['主动离职', '被动离职'],
                                datasets: [{
                                    data: [typeData['主动离职'], typeData['被动离职']],
                                    backgroundColor: ['#10b981', '#f43f5e'],
                                    borderColor: ['#ffffff', '#ffffff'],
                                    borderWidth: 2,
                                    hoverOffset: 15
                                }]
                            },
                            options: {
                                responsive: true,
                                maintainAspectRatio: false,
                                plugins: {
                                    title: {
                                        display: true,
                                        text: '离职类型分布',
                                        font: {
                                            size: 18,
                                            weight: 'bold',
                                            family: 'Arial, sans-serif'
                                        },
                                        color: '#1e293b'
                                    },
                                    legend: {
                                        display: true,
                                        position: 'bottom',
                                        labels: {
                                            font: {
                                                size: 14,
                                                family: 'Arial, sans-serif'
                                            },
                                            color: '#475569',
                                            padding: 20,
                                            usePointStyle: true,
                                            pointStyle: 'circle'
                                        }
                                    },
                                    tooltip: {
                                        backgroundColor: 'rgba(30, 41, 59, 0.9)',
                                        titleFont: {
                                            size: 14,
                                            weight: 'bold',
                                            family: 'Arial, sans-serif'
                                        },
                                        bodyFont: {
                                            size: 13,
                                            family: 'Arial, sans-serif'
                                        },
                                        padding: 12,
                                        cornerRadius: 8,
                                        displayColors: true,
                                        callbacks: {
                                            label: function(context) {
                                                const label = context.label || '';
                                                const value = context.raw || 0;
                                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                                const percentage = Math.round((value / total) * 100);
                                                return `${label}: ${value} (${percentage}%)`;
                                            }
                                        }
                                    }
                                }
                            }
                        });
                    }
                    
                    // 移除加载状态
                    chartContainers.forEach(container => {
                        container.classList.remove('loading');
                    });
                }
            })
            .catch(error => {
                console.error('加载离职趋势数据失败:', error);
            });
    }
    
    // 导出离职记录数据
    function exportExitRecordsData() {
        const selectedCity = localStorage.getItem('selectedCity') || 'all';
        
        // 构建查询参数
        const queryParams = new URLSearchParams();
        queryParams.append('city', selectedCity);
        
        const queryString = queryParams.toString();
        const url = `${window.API_BASE_URL}/api/riders/exit-records${queryString ? `?${queryString}` : ''}`;
        
        // 从API获取数据
        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const records = data.data;
                    if (records.length === 0) {
                        alert('没有数据可导出');
                        return;
                    }
                    
                    // 生成CSV内容
                    const headers = [
                        '骑手姓名', '身份证号', '联系电话', '站点名称', '离职类型', '离职原因',
                        '入职日期', '离职日期', '离岗日期', '在职时长'
                    ];
                    
                    const csvContent = [
                        headers.join(','),
                        ...records.map(record => [
                            record.name || '-',
                            record.id_card || '-',
                            record.phone || '-',
                            record.station_name || '-',
                            record.exit_type || '-',
                            record.exit_reason || '-',
                            record.entry_date || '-',
                            record.exit_date || '-',
                            record.leave_date || '-',
                            record.working_duration || '-'
                        ].join(','))
                    ].join('\n');
                    
                    // 创建下载链接
                    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
                    const url = URL.createObjectURL(blob);
                    const link = document.createElement('a');
                    link.setAttribute('href', url);
                    link.setAttribute('download', `离职记录_${new Date().toISOString().split('T')[0]}.csv`);
                    link.style.visibility = 'hidden';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                } else {
                    alert('导出失败，请重试');
                }
            })
            .catch(error => {
                console.error('导出数据失败:', error);
                alert('网络错误，请稍后重试');
            });
    }
    
    // 加载待离职统计数据
    function loadPendingExitData(filters = {}) {
        const pendingExitTable = document.getElementById('pending-exit-table');
        if (!pendingExitTable) return;
        
        const tbody = pendingExitTable.querySelector('tbody');
        tbody.innerHTML = `
            <tr>
                <td colspan="12" class="loading">
                    <p>加载中...</p>
                </td>
            </tr>
        `;
        
        // 获取当前选择的城市
        const selectedCity = filters.city || localStorage.getItem('selectedCity') || 'all';
        
        // 构建查询参数
        const queryParams = new URLSearchParams();
        queryParams.append('city', selectedCity);
        if (filters.department) queryParams.append('station_name', filters.department);
        if (filters.exitType) queryParams.append('exit_type', filters.exitType);
        if (filters.reason) queryParams.append('exit_reason', filters.reason);
        if (filters.startDate) queryParams.append('start_date', filters.startDate);
        if (filters.endDate) queryParams.append('end_date', filters.endDate);
        
        const queryString = queryParams.toString();
        const url = `${window.API_BASE_URL}/api/riders/pending-exit${queryString ? `?${queryString}` : ''}`;
        
        // 从API获取待离职统计数据
        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const pendingRecords = data.data;
                    const stats = data.stats;
                    
                    // 更新统计卡片
                    const statCards = document.querySelectorAll('.stat-card');
                    if (statCards.length >= 4) {
                        statCards[0].classList.remove('loading');
                        statCards[0].querySelector('p').textContent = stats.total_pending;
                        
                        statCards[1].classList.remove('loading');
                        statCards[1].querySelector('p').textContent = stats.current_month_pending;
                        
                        statCards[2].classList.remove('loading');
                        statCards[2].querySelector('p').textContent = stats.next_month_pending;
                        
                        statCards[3].classList.remove('loading');
                        statCards[3].querySelector('p').textContent = stats.pending_rate + '%';
                    }
                    
                    // 更新表格数据
                    tbody.innerHTML = '';
                    pendingRecords.forEach((record, index) => {
                        const row = document.createElement('tr');
                        
                        row.innerHTML = `
                            <td><input type="checkbox" data-rider-id="${record.rider_id}"></td>
                            <td>${index + 1}</td>
                            <td>${formatValue(record.name, 'name', record)}</td>
                            <td>${formatValue(record.id_card, 'id_card', record)}</td>
                            <td>${formatValue(record.phone, 'phone', record)}</td>
                            <td>${formatValue(record.station_name, 'station_name', record)}</td>
                            <td>${record.exit_type || '-'}</td>
                            <td>${record.exit_reason || '-'}</td>
                            <td>${formatValue(record.entry_date, 'entry_date', record)}</td>
                            <td>${formatValue(record.leave_date, 'leave_date', record)}</td>
                            <td>${record.remaining_days || '-'}</td>
                            <td>
                                <a href="#" class="action-link view-rider" data-rider-id="${record.rider_id}">详情</a>
                            </td>
                        `;
                        tbody.appendChild(row);
                    });
                    
                    // 绑定详情事件
                    document.querySelectorAll('.view-rider').forEach(link => {
                        link.addEventListener('click', function(e) {
                            e.preventDefault();
                            const riderId = this.getAttribute('data-rider-id');
                            viewRider(riderId);
                        });
                    });
                } else {
                    tbody.innerHTML = `
                        <tr>
                            <td colspan="12">
                                <p>加载失败，请重试</p>
                            </td>
                        </tr>
                    `;
                }
            })
            .catch(error => {
                console.error('加载待离职统计数据失败:', error);
                tbody.innerHTML = `
                    <tr>
                        <td colspan="12">
                            <p>网络错误，请稍后重试</p>
                        </td>
                    </tr>
                `;
            });
    }
    
    // 加载待离职趋势图表
    function loadPendingExitTrendCharts(filters = {}) {
        const chartContainers = document.querySelectorAll('.chart-wrapper');
        if (chartContainers.length < 2) return;
        
        const trendChartCtx = chartContainers[0].querySelector('canvas');
        if (!trendChartCtx) {
            chartContainers[0].innerHTML = '<canvas id="pending-exit-trend-chart"></canvas>';
        }
        
        const typeChartCtx = chartContainers[1].querySelector('canvas');
        if (!typeChartCtx) {
            chartContainers[1].innerHTML = '<canvas id="pending-exit-type-chart"></canvas>';
        }
        
        const selectedCity = filters.city || localStorage.getItem('selectedCity') || 'all';
        
        // 构建查询参数
        const queryParams = new URLSearchParams();
        queryParams.append('city', selectedCity);
        
        const queryString = queryParams.toString();
        const url = `${window.API_BASE_URL}/api/riders/pending-exit${queryString ? `?${queryString}` : ''}`;
        
        // 从API获取待离职统计数据
        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const records = data.data;
                    
                    // 处理待离职趋势数据
                    const pendingData = {};
                    records.forEach(record => {
                        if (record.leave_date) {
                            const date = record.leave_date.split('T')[0];
                            if (!pendingData[date]) {
                                pendingData[date] = 0;
                            }
                            pendingData[date]++;
                        }
                    });
                    
                    // 排序日期
                    const sortedDates = Object.keys(pendingData).sort();
                    const dates = sortedDates;
                    const totalPendings = sortedDates.map(date => pendingData[date]);
                    
                    // 渲染待离职趋势图表
                    const trendCanvas = document.getElementById('pending-exit-trend-chart');
                    if (trendCanvas) {
                        if (window.pendingExitTrendChart) {
                            window.pendingExitTrendChart.destroy();
                        }
                        window.pendingExitTrendChart = new Chart(trendCanvas, {
                            type: 'line',
                            data: {
                                labels: dates,
                                datasets: [{
                                    label: '待离职人数',
                                    data: totalPendings,
                                    borderColor: '#3b82f6',
                                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                                    tension: 0.4,
                                    fill: true,
                                    borderWidth: 2,
                                    pointBackgroundColor: '#3b82f6',
                                    pointBorderColor: '#ffffff',
                                    pointBorderWidth: 2,
                                    pointRadius: 4,
                                    pointHoverRadius: 6
                                }]
                            },
                            options: {
                                responsive: true,
                                maintainAspectRatio: false,
                                plugins: {
                                    title: {
                                        display: true,
                                        text: '待离职趋势分析',
                                        font: {
                                            size: 18,
                                            weight: 'bold',
                                            family: 'Arial, sans-serif'
                                        },
                                        color: '#1e293b'
                                    },
                                    legend: {
                                        display: true,
                                        position: 'top',
                                        labels: {
                                            font: {
                                                size: 12,
                                                family: 'Arial, sans-serif'
                                            },
                                            color: '#475569'
                                        }
                                    }
                                },
                                scales: {
                                    x: {
                                        title: {
                                            display: true,
                                            text: '日期',
                                            font: {
                                                size: 14,
                                                weight: 'bold',
                                                family: 'Arial, sans-serif'
                                            },
                                            color: '#475569'
                                        },
                                        grid: {
                                            color: 'rgba(226, 232, 240, 0.5)'
                                        },
                                        ticks: {
                                            font: {
                                                size: 12,
                                                family: 'Arial, sans-serif'
                                            },
                                            color: '#64748b'
                                        }
                                    },
                                    y: {
                                        title: {
                                            display: true,
                                            text: '人数',
                                            font: {
                                                size: 14,
                                                weight: 'bold',
                                                family: 'Arial, sans-serif'
                                            },
                                            color: '#475569'
                                        },
                                        grid: {
                                            color: 'rgba(226, 232, 240, 0.5)'
                                        },
                                        ticks: {
                                            font: {
                                                size: 12,
                                                family: 'Arial, sans-serif'
                                            },
                                            color: '#64748b'
                                        },
                                        beginAtZero: true
                                    }
                                },
                                interaction: {
                                    intersect: false,
                                    mode: 'index'
                                },
                                elements: {
                                    line: {
                                        tension: 0.4
                                    }
                                }
                            }
                        });
                    }
                    
                    // 处理待离职类型分布数据
                    const typeData = {
                        '主动离职': 0,
                        '被动离职': 0
                    };
                    records.forEach(record => {
                        const exitType = record.exit_type || '被动离职';
                        if (typeData.hasOwnProperty(exitType)) {
                            typeData[exitType]++;
                        }
                    });
                    
                    // 渲染待离职类型分布图表
                    const typeCanvas = document.getElementById('pending-exit-type-chart');
                    if (typeCanvas) {
                        if (window.pendingExitTypeChart) {
                            window.pendingExitTypeChart.destroy();
                        }
                        window.pendingExitTypeChart = new Chart(typeCanvas, {
                            type: 'pie',
                            data: {
                                labels: ['主动离职', '被动离职'],
                                datasets: [{
                                    data: [typeData['主动离职'], typeData['被动离职']],
                                    backgroundColor: ['#10b981', '#f43f5e'],
                                    borderColor: ['#ffffff', '#ffffff'],
                                    borderWidth: 2,
                                    hoverOffset: 15
                                }]
                            },
                            options: {
                                responsive: true,
                                maintainAspectRatio: false,
                                plugins: {
                                    title: {
                                        display: true,
                                        text: '待离职类型分布',
                                        font: {
                                            size: 18,
                                            weight: 'bold',
                                            family: 'Arial, sans-serif'
                                        },
                                        color: '#1e293b'
                                    },
                                    legend: {
                                        display: true,
                                        position: 'bottom',
                                        labels: {
                                            font: {
                                                size: 14,
                                                family: 'Arial, sans-serif'
                                            },
                                            color: '#475569',
                                            padding: 20,
                                            usePointStyle: true,
                                            pointStyle: 'circle'
                                        }
                                    },
                                    tooltip: {
                                        backgroundColor: 'rgba(30, 41, 59, 0.9)',
                                        titleFont: {
                                            size: 14,
                                            weight: 'bold',
                                            family: 'Arial, sans-serif'
                                        },
                                        bodyFont: {
                                            size: 13,
                                            family: 'Arial, sans-serif'
                                        },
                                        padding: 12,
                                        cornerRadius: 8,
                                        displayColors: true,
                                        callbacks: {
                                            label: function(context) {
                                                const label = context.label || '';
                                                const value = context.raw || 0;
                                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                                const percentage = Math.round((value / total) * 100);
                                                return `${label}: ${value} (${percentage}%)`;
                                            }
                                        }
                                    }
                                }
                            }
                        });
                    }
                    
                    // 移除加载状态
                    chartContainers.forEach(container => {
                        container.classList.remove('loading');
                    });
                }
            })
            .catch(error => {
                console.error('加载待离职趋势数据失败:', error);
            });
    }
    
    // 绑定待离职统计筛选器事件
    function bindPendingExitFilterEvents() {
        const searchBtn = document.querySelector('.btn-search');
        const resetBtn = document.querySelector('.btn-reset');
        
        if (searchBtn) {
            searchBtn.addEventListener('click', function() {
                const filters = getPendingExitFilters();
                loadPendingExitData(filters);
                loadPendingExitTrendCharts(filters);
            });
        }
        
        if (resetBtn) {
            resetBtn.addEventListener('click', function() {
                resetPendingExitFilters();
                loadPendingExitData();
                loadPendingExitTrendCharts();
            });
        }
    }
    
    // 获取待离职统计筛选条件
    function getPendingExitFilters() {
        const city = localStorage.getItem('selectedCity') || 'all';
        const department = document.getElementById('department-select').value;
        const exitType = document.getElementById('exit-type-select').value;
        const reason = document.getElementById('reason-select').value;
        const startDate = document.getElementById('start-date').value;
        const endDate = document.getElementById('end-date').value;
        
        return {
            city,
            department,
            exitType,
            reason,
            startDate,
            endDate
        };
    }
    
    // 重置待离职统计筛选条件
    function resetPendingExitFilters() {
        document.getElementById('department-select').value = '';
        document.getElementById('exit-type-select').value = '';
        document.getElementById('reason-select').value = '';
        document.getElementById('start-date').value = '';
        document.getElementById('end-date').value = '';
    }
    
    // 导出待离职统计数据
    function exportPendingExitData() {
        const selectedCity = localStorage.getItem('selectedCity') || 'all';
        
        // 构建查询参数
        const queryParams = new URLSearchParams();
        queryParams.append('city', selectedCity);
        
        const queryString = queryParams.toString();
        const url = `${window.API_BASE_URL}/api/riders/pending-exit${queryString ? `?${queryString}` : ''}`;
        
        // 从API获取数据
        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const records = data.data;
                    if (records.length === 0) {
                        alert('没有数据可导出');
                        return;
                    }
                    
                    // 生成CSV内容
                    const headers = [
                        '骑手姓名', '身份证号', '联系电话', '站点名称', '离职类型', '离职原因',
                        '入职日期', '计划离职日期', '剩余在职天数'
                    ];
                    
                    const csvContent = [
                        headers.join(','),
                        ...records.map(record => [
                            record.name || '-',
                            record.id_card || '-',
                            record.phone || '-',
                            record.station_name || '-',
                            record.exit_type || '-',
                            record.exit_reason || '-',
                            record.entry_date || '-',
                            record.leave_date || '-',
                            record.remaining_days || '-'
                        ].join(','))
                    ].join('\n');
                    
                    // 创建下载链接
                    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
                    const url = URL.createObjectURL(blob);
                    const link = document.createElement('a');
                    link.setAttribute('href', url);
                    link.setAttribute('download', `待离职统计_${new Date().toISOString().split('T')[0]}.csv`);
                    link.style.visibility = 'hidden';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                } else {
                    alert('导出失败，请重试');
                }
            })
            .catch(error => {
                console.error('导出数据失败:', error);
                alert('网络错误，请稍后重试');
            });
    }
    
    // 检查是否是离职记录页面
    if (window.location.pathname.includes('rider-exit-records.html')) {
        // 绑定离职记录筛选器事件
        bindExitRecordsFilterEvents();
        
        // 绑定导出数据按钮事件
        const exportBtn = document.querySelector('.rider-actions button');
        if (exportBtn && exportBtn.textContent.trim() === '导出数据') {
            exportBtn.addEventListener('click', function() {
                exportExitRecordsData();
            });
        }
    }
    
    // 检查是否是待离职统计页面
    if (window.location.pathname.includes('rider-pending-exit.html')) {
        // 绑定待离职统计筛选器事件
        bindPendingExitFilterEvents();
        
        // 绑定导出数据按钮事件
        const exportBtn = document.querySelector('.rider-actions button');
        if (exportBtn && exportBtn.textContent.trim() === '导出数据') {
            exportBtn.addEventListener('click', function() {
                exportPendingExitData();
            });
        }
    }
});