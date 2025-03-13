// 全局变量存储上传的文件
let uploadedFiles = [];

// 生成系统秘钥
async function generateSystemKey() {
    const authNumber = document.getElementById('authNumber').value;
    if (!authNumber) {
        showAlert('请先输入授权编号');
        return;
    }
    
    try {
        const response = await fetch('/generate-key', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ auth_number: authNumber })
        });
        
        const data = await response.json();
        if (data.success) {
            document.getElementById('systemKey').value = data.systemKey;
        } else {
            showAlert(data.error);
        }
    } catch (error) {
        showAlert('生成秘钥失败，请重试');
    }
}

// 复制系统秘钥
function copySystemKey() {
    const systemKey = document.getElementById('systemKey').value;
    if (systemKey) {
        copyToClipboard(systemKey);
    }
}

// 文件上传相关
const dropZone = document.getElementById('dropZone');

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    handleFiles(e.dataTransfer.files);
});

dropZone.addEventListener('click', () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.multiple = true;
    input.accept = '.pdf,.doc,.docx,.jpg,.jpeg,.png,.tif';
    input.onchange = (e) => handleFiles(e.target.files);
    input.click();
});

async function handleFiles(files) {
    const progressContainer = document.querySelector('.progress-container');
    const progressBar = document.querySelector('.progress');
    const progressText = document.querySelector('.progress-text');
    
    for (const file of files) {
        if (file.size > 10 * 1024 * 1024) {
            showAlert(`文件 ${file.name} 超过10MB限制`);
            continue;
        }
        
        progressContainer.style.display = 'block';
        
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            if (data.success) {
                uploadedFiles.push({
                    filename: data.filename,
                    filepath: data.filepath,
                    ocrResults: data.ocrResults
                });
                updateFileList();
                
                // 处理OCR结果
                if (data.ocrResults) {
                    updateOCRResults(data.ocrResults);
                }
            } else {
                showAlert(data.error);
            }
        } catch (error) {
            showAlert('上传失败，请重试');
        }
        
        progressContainer.style.display = 'none';
    }
}

function updateFileList() {
    const fileList = document.getElementById('fileList');
    fileList.innerHTML = '';
    
    uploadedFiles.forEach((file, index) => {
        const li = document.createElement('li');
        li.innerHTML = `
            <span>${file.filename}</span>
            <button onclick="removeFile(${index})" class="btn btn-small">删除</button>
        `;
        fileList.appendChild(li);
    });
}

function removeFile(index) {
    uploadedFiles.splice(index, 1);
    updateFileList();
}

function updateOCRResults(results) {
    document.getElementById('company').value = results.company || '';
    document.getElementById('channel').value = results.channel || '';
    document.getElementById('validPeriod').value = results.valid_period || '';
    document.getElementById('brand').value = results.brand || '';
}

async function submitForm() {
    const authNumber = document.getElementById('authNumber').value;
    const systemKey = document.getElementById('systemKey').value;
    
    if (!authNumber || !systemKey || uploadedFiles.length === 0) {
        showAlert('请填写完整信息并上传文件');
        return;
    }
    
    const formData = {
        authNumber,
        systemKey,
        company: document.getElementById('company').value,
        channel: document.getElementById('channel').value,
        validPeriod: document.getElementById('validPeriod').value,
        brand: document.getElementById('brand').value,
        files: uploadedFiles
    };
    
    try {
        const response = await fetch('/submit-auth', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        if (data.success) {
            showAlert('提交成功', 'success');
            setTimeout(() => {
                window.location.href = '/main/list';
            }, 1500);
        } else {
            showAlert(data.error);
        }
    } catch (error) {
        showAlert('提交失败，请重试');
    }
} 