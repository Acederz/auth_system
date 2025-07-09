// 通用工具函数
function showAlert(message, type = "error") {
  const alertDiv = document.createElement("div");
  alertDiv.className = `alert alert-${type}`;
  alertDiv.textContent = message;

  document.body.insertBefore(alertDiv, document.body.firstChild);

  setTimeout(() => {
    alertDiv.remove();
  }, 3000);
}

function showAlertS(message, type = "success") {
  const alertDiv = document.createElement("div");
  alertDiv.className = `alert alert-${type}`;
  alertDiv.textContent = message;

  document.body.insertBefore(alertDiv, document.body.firstChild);

  setTimeout(() => {
    alertDiv.remove();
  }, 3000);
}

// 复制文本到剪贴板
function copyToClipboard(text) {
  navigator.clipboard
    .writeText(text)
    .then(() => {
      showAlert("复制成功", "success");
    })
    .catch(() => {
      showAlert("复制失败，请手动复制");
    });
}

// 格式化日期
function formatDate(date) {
  const d = new Date(date);
  return d.toLocaleDateString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

// 格式化文件大小
function formatFileSize(bytes) {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
}

// 移动端表格优化
document.addEventListener('DOMContentLoaded', function() {
    // 检测是否为移动设备
    const isMobile = window.innerWidth <= 768;
    
    // 如果是移动设备，优化表格显示
    if (isMobile) {
        // 为所有表格添加水平滚动提示
        const tables = document.querySelectorAll('.auth-table');
        tables.forEach(table => {
            // 创建提示元素
            const scrollHint = document.createElement('div');
            scrollHint.className = 'scroll-hint';
            scrollHint.textContent = '← 左右滑动查看更多 →';
            scrollHint.style.textAlign = 'center';
            scrollHint.style.fontSize = '0.8rem';
            scrollHint.style.color = '#666';
            scrollHint.style.padding = '0.5rem 0';
            
            // 插入到表格前
            table.parentNode.insertBefore(scrollHint, table);
            
            // 监听表格滚动，隐藏提示
            table.addEventListener('scroll', function() {
                scrollHint.style.opacity = '0.5';
                setTimeout(() => {
                    scrollHint.style.opacity = '0';
                }, 1500);
            });
        });
    }
});
