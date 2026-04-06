document.addEventListener('DOMContentLoaded', function() {
    const loginBtn = document.getElementById('login-btn');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const loginMessage = document.getElementById('login-message');

    loginBtn.addEventListener('click', function() {
        const username = usernameInput.value.trim();
        const password = passwordInput.value.trim();

        if (!username || !password) {
            showMessage('用户名和密码不能为空', 'error');
            return;
        }

        // 登录请求
        fetch(window.API_BASE_URL + '/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // 存储用户信息到本地存储
                localStorage.setItem('user', JSON.stringify(data.user));
                showMessage('登录成功', 'success');
                // 登录成功后跳转到主页
                setTimeout(() => {
                    window.location.href = 'dashboard.html';
                }, 1000);
            } else {
                showMessage(data.message || '登录失败', 'error');
            }
        })
        .catch(error => {
            console.error('登录请求失败:', error);
            showMessage('网络错误，请稍后重试', 'error');
        });
    });

    function showMessage(message, type) {
        loginMessage.textContent = message;
        loginMessage.className = `login-message ${type}`;
    }
});