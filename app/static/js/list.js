// 搜索授权书
function searchAuths() {
    const searchInput = document.getElementById('searchInput').value;
    const channelFilter = document.getElementById('channelFilter').value;
    const statusFilter = document.getElementById('statusFilter').value;
    const yearFilter = document.getElementById('yearFilter').value;

    const params = new URLSearchParams({
        search: searchInput,
        channel: channelFilter,
        status: statusFilter,
        year: yearFilter
    });
    
    window.location.href = `/main/list?${params.toString()}`;
}

// 导出Excel
function exportExcel() {
    window.location.href = '/export-excel';
}

// 查看授权书详情
async function viewAuth(authid) {
    // TODO: 实现查看详情功能
    // 创建模态框
    const modal = document.getElementById('viewModal');
    const imageContainer = modal.querySelector('.modal-image-container');
    imageContainer.innerHTML = ''; // 清空之前的内容
    modal.style.display = 'block'; // 显示模态框
    
    const response = await fetch('/main/images', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ authid: authid })
    })
    const data = await response.json()
    if(data.success) {
        data.images.forEach(imageUrl => {
            const img = document.createElement('img');
            img.src = imageUrl;
            img.className = 'auth-image';
            img.style.maxWidth = '100%'; // 设置图片最大宽度
            img.style.height = 'auto'; // 高度自适应
            imageContainer.appendChild(img);
        });
    } else {
        const errorMessage = document.createElement('p');
        errorMessage.textContent = '未找到相关图片';
        imageContainer.appendChild(errorMessage);
    }
    
    console.log('查看授权书：'+authid);
}

// 下载授权书
function downloadAuth(authId) {
    // TODO: 实现下载功能
    window.location.href = `/downloadauth/${authId}`;
    
    console.log('下载授权书:', authId);
}

// 为搜索输入框添加回车事件监听
document.getElementById('searchInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        searchAuths();
    }
}); 

function closeModal() {
    document.getElementById('editModal').style.display = 'none'; // 隐藏模态框
    document.getElementById('viewModal').style.display = 'none'; 
    document.getElementById('deleteModal').style.display = 'none';
}

// 打开编辑模态框并填充当前行数据
function openEditModal(button, authId, authNumber, company, brand, channel, validPeriod) {
    document.getElementById('editAuthNumber').value = authNumber;
    document.getElementById('editCompany').value = company;
    document.getElementById('editBrand').value = brand;
    document.getElementById('editChannel').value = channel;
    document.getElementById('editValidPeriod').value = validPeriod;
    // 保存当前授权ID
    window.currentAuthId = authId;
    document.getElementById('editModal').style.display = 'block';
}

// 保存编辑内容
async function saveEdit() {
    const updatedData = {
        authId: window.currentAuthId,
        authNumber: document.getElementById('editAuthNumber').value,
        company: document.getElementById('editCompany').value,
        brand: document.getElementById('editBrand').value,
        channel: document.getElementById('editChannel').value,
        validPeriod: document.getElementById('editValidPeriod').value
    };

    const response = await fetch('/updateauth', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(updatedData)
    });

    if (response.ok) {
        // 更新成功后刷新页面或更新表格
        location.reload();
    } else {
        alert('更新失败');
    }
}

function confirmDelete(authId) {
    window.currentAuthId = authId; // 保存当前要删除的授权ID
    document.getElementById('deleteModal').style.display = 'block';
}

// 执行删除操作
async function deleteAuth() {
    try {
        const response = await fetch(`/deleteauth/${window.currentAuthId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const result = await response.json();
        
        if (result.success) {
            // 删除成功后刷新页面
            location.reload();
        } else {
            alert('删除失败: ' + result.error);
        }
    } catch (error) {
        console.error('删除过程中出错:', error);
        alert('删除过程中出错');
    } finally {
        closeModal();
    }
}