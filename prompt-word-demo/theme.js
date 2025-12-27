/**
 * 通用主题切换脚本
 * 在HTML文件的<head>中添加以下CSS变量定义，然后在</body>前引入此脚本
 * 
 * CSS变量示例：
 * :root { --bg-body: #0a1628; --text-primary: #fff; ... }
 * [data-theme="light"] { --bg-body: #f0f4f8; --text-primary: #1e293b; ... }
 */

(function() {
    // 从URL参数或localStorage获取主题
    const urlParams = new URLSearchParams(window.location.search);
    let theme = urlParams.get('theme') || localStorage.getItem('theme') || 'dark';
    
    // 应用主题
    function applyTheme(t) {
        if (t === 'light') {
            document.documentElement.setAttribute('data-theme', 'light');
        } else {
            document.documentElement.removeAttribute('data-theme');
        }
        localStorage.setItem('theme', t);
        theme = t;
        
        // 更新主题按钮图标（如果存在）
        const btn = document.getElementById('themeBtn') || document.getElementById('themeToggle');
        if (btn) btn.textContent = t === 'light' ? '☀️' : '🌙';
    }
    
    // 初始化
    applyTheme(theme);
    
    // 绑定切换按钮
    document.addEventListener('DOMContentLoaded', function() {
        const btn = document.getElementById('themeBtn') || document.getElementById('themeToggle');
        if (btn) {
            btn.textContent = theme === 'light' ? '☀️' : '🌙';
            btn.onclick = function() {
                applyTheme(theme === 'dark' ? 'light' : 'dark');
            };
        }
    });
    
    // 导出给全局使用
    window.toggleTheme = function() {
        applyTheme(theme === 'dark' ? 'light' : 'dark');
    };
    window.getTheme = function() { return theme; };
})();
