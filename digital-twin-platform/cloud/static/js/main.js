/**
 * 云边端数字孪生平台 - 主JavaScript文件
 */

// WebSocket连接
let socket;

// 初始化函数
function initApp() {
    console.log('初始化应用...');
    
    // 初始化WebSocket连接
    initWebSocket();
    
    // 设置全局事件监听器
    setupEventListeners();
}

// 初始化WebSocket连接
function initWebSocket() {
    try {
        socket = io();
        
        socket.on('connect', function() {
            console.log('WebSocket连接已建立');
            showToast('系统连接', '已成功连接到服务器', 'success');
        });
        
        socket.on('disconnect', function() {
            console.log('WebSocket连接已断开');
            showToast('系统连接', '与服务器的连接已断开', 'error');
        });
        
        socket.on('error', function(error) {
            console.error('WebSocket错误:', error);
            showToast('系统错误', '连接发生错误', 'error');
        });
        
    } catch (error) {
        console.error('初始化WebSocket失败:', error);
    }
}

// 设置全局事件监听器
function setupEventListeners() {
    // 页面可见性变化时重新连接WebSocket
    document.addEventListener('visibilitychange', function() {
        if (document.visibilityState === 'visible' && socket && !socket.connected) {
            console.log('页面可见，尝试重新连接...');
            socket.connect();
        }
    });
    
    // 响应式导航栏激活状态
    const currentPath = window.location.pathname;
    document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}

// 显示Toast通知
function showToast(title, message, type = 'info') {
    // 检查是否已加载Bootstrap
    if (typeof bootstrap === 'undefined') {
        console.warn('Bootstrap未加载，无法显示Toast');
        return;
    }
    
    // 创建Toast元素
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toastEl = document.createElement('div');
    toastEl.className = `toast align-items-center text-white bg-${getToastBgClass(type)} border-0`;
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');
    
    toastEl.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <strong>${title}</strong>: ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    toastContainer.appendChild(toastEl);
    
    // 初始化并显示Toast
    const toast = new bootstrap.Toast(toastEl, {
        delay: 5000,
        autohide: true
    });
    toast.show();
    
    // 自动移除
    toastEl.addEventListener('hidden.bs.toast', function() {
        toastContainer.removeChild(toastEl);
    });
}

// 创建Toast容器
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    container.style.zIndex = '1050';
    document.body.appendChild(container);
    return container;
}

// 获取Toast背景类
function getToastBgClass(type) {
    switch (type) {
        case 'success':
            return 'success';
        case 'error':
            return 'danger';
        case 'warning':
            return 'warning';
        case 'info':
        default:
            return 'primary';
    }
}

// 格式化日期时间
function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString();
}

// 格式化数值，保留指定小数位
function formatNumber(value, decimals = 2) {
    return Number(value).toFixed(decimals);
}

// 页面加载完成后初始化应用
document.addEventListener('DOMContentLoaded', initApp); 