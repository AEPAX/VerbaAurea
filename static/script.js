// VerbaAurea Web服务前端交互脚本 - 批量处理版本

let currentSessionId = null;
let processingInterval = null;
let uploadedFiles = [];

// DOM元素
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const browseBtn = document.getElementById('browseBtn');
const uploadedFilesSection = document.getElementById('uploadedFilesSection');
const uploadedFilesList = document.getElementById('uploadedFilesList');
const noUploadedFiles = document.getElementById('noUploadedFiles');
const processBtn = document.getElementById('processBtn');
const clearBtn = document.getElementById('clearBtn');
const statusSection = document.getElementById('statusSection');
const resultSection = document.getElementById('resultSection');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const currentFileName = document.getElementById('currentFileName');
const processProgress = document.getElementById('processProgress');
const processStatus = document.getElementById('processStatus');
const startTime = document.getElementById('startTime');
const successCard = document.getElementById('successCard');
const errorCard = document.getElementById('errorCard');
const downloadBtn = document.getElementById('downloadBtn');
const errorMessage = document.getElementById('errorMessage');
const resultSummary = document.getElementById('resultSummary');

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
    loadConfig();
    resetBatch();
});

// 设置事件监听器
function setupEventListeners() {
    // 文件拖拽
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);

    // 文件选择
    fileInput.addEventListener('change', handleFileSelect);

    // 点击上传区域（但不包括按钮）
    uploadArea.addEventListener('click', (e) => {
        // 如果点击的是按钮，不触发文件选择
        if (e.target !== browseBtn && !browseBtn.contains(e.target)) {
            fileInput.click();
        }
    });

    // 选择文件按钮
    browseBtn.addEventListener('click', (e) => {
        e.stopPropagation(); // 防止事件冒泡
        fileInput.click();
    });

    // 处理按钮
    processBtn.addEventListener('click', startBatchProcessing);

    // 清空按钮
    clearBtn.addEventListener('click', clearUploadedFiles);

    // 下载按钮
    downloadBtn.addEventListener('click', downloadBatchResult);
}

// 拖拽处理
function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleMultipleFiles(Array.from(files));
    }
}

// 文件选择处理
function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        handleMultipleFiles(Array.from(files));
    }
    // 清空文件输入，允许重复选择相同文件
    fileInput.value = '';
}

// 多文件处理
function handleMultipleFiles(files) {
    const validFiles = [];
    const invalidFiles = [];

    for (let file of files) {
        // 检查是否已经上传过
        if (uploadedFiles.some(f => f.name === file.name && f.size === file.size)) {
            showToast(`文件 ${file.name} 已存在，已跳过`, 'info');
            continue;
        }

        if (!file.name.toLowerCase().endsWith('.docx')) {
            invalidFiles.push(`${file.name} (不是.docx格式)`);
            continue;
        }

        if (file.size > 50 * 1024 * 1024) {
            invalidFiles.push(`${file.name} (超过50MB)`);
            continue;
        }

        validFiles.push(file);
    }

    if (invalidFiles.length > 0) {
        showToast(`跳过无效文件: ${invalidFiles.join(', ')}`, 'error');
    }

    if (validFiles.length === 0) {
        if (invalidFiles.length === 0) {
            showToast('没有新文件需要上传', 'info');
        }
        return;
    }

    // 批量上传文件
    uploadMultipleFiles(validFiles);
}

// 批量上传文件
async function uploadMultipleFiles(files) {
    showToast(`开始上传 ${files.length} 个文件...`, 'info');

    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        try {
            showToast(`上传文件 ${i + 1}/${files.length}: ${file.name}`, 'info');
            await uploadSingleFile(file);
        } catch (error) {
            showToast(`上传文件 ${file.name} 失败: ${error.message}`, 'error');
        }
    }

    showToast(`文件上传完成，共 ${uploadedFiles.length} 个文件`, 'success');
    updateUploadedFilesList();
}

// 上传单个文件
async function uploadSingleFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    if (currentSessionId) {
        formData.append('session_id', currentSessionId);
    }

    const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData
    });

    const result = await response.json();

    if (response.ok && result.success) {
        // 更新会话ID
        if (!currentSessionId) {
            currentSessionId = result.session_id;
        }

        // 添加到已上传文件列表
        uploadedFiles.push({
            file_id: result.file_id,
            name: result.original_filename,
            size: result.file_size,
            upload_time: new Date().toLocaleString()
        });

        return result;
    } else {
        throw new Error(result.error || '上传失败');
    }
}

// 更新已上传文件列表显示
function updateUploadedFilesList() {
    if (uploadedFiles.length === 0) {
        uploadedFilesSection.style.display = 'none';
        return;
    }

    uploadedFilesSection.style.display = 'block';

    const filesHTML = uploadedFiles.map((file, index) => `
        <div class="uploaded-file-item" data-file-id="${file.file_id}">
            <div class="file-info">
                <div class="file-name">📄 ${file.name}</div>
                <div class="file-details">
                    <span class="file-size">${formatFileSize(file.size)}</span>
                    <span class="upload-time">${file.upload_time}</span>
                </div>
            </div>
            <button class="remove-file-btn" onclick="removeUploadedFile('${file.file_id}')">
                ❌
            </button>
        </div>
    `).join('');

    uploadedFilesList.innerHTML = filesHTML;

    // 更新处理按钮状态
    processBtn.disabled = uploadedFiles.length === 0;
    processBtn.textContent = `🚀 开始处理 (${uploadedFiles.length} 个文件)`;
}

// 移除已上传的文件
async function removeUploadedFile(fileId) {
    try {
        const response = await fetch('/api/batch/remove-file', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: currentSessionId,
                file_id: fileId
            })
        });

        const result = await response.json();

        if (response.ok && result.success) {
            // 从本地列表中移除
            uploadedFiles = uploadedFiles.filter(f => f.file_id !== fileId);
            updateUploadedFilesList();
            showToast('文件已移除', 'success');
        } else {
            showToast(`移除文件失败: ${result.error}`, 'error');
        }
    } catch (error) {
        showToast(`移除文件失败: ${error.message}`, 'error');
    }
}

// 清空已上传文件列表
function clearUploadedFiles() {
    if (uploadedFiles.length === 0) {
        return;
    }

    if (confirm(`确定要清空所有 ${uploadedFiles.length} 个已上传文件吗？`)) {
        // 逐个移除文件
        const fileIds = uploadedFiles.map(f => f.file_id);
        fileIds.forEach(fileId => removeUploadedFile(fileId));
    }
}

// 开始批量处理
async function startBatchProcessing() {
    if (!currentSessionId || uploadedFiles.length === 0) {
        showToast('没有文件需要处理', 'error');
        return;
    }

    try {
        // 显示处理状态区域
        statusSection.style.display = 'block';
        resultSection.style.display = 'none';
        uploadedFilesSection.style.display = 'none';

        // 初始化状态
        updateProcessStatus('processing', '开始批量处理...', 0);
        startTime.textContent = new Date().toLocaleString();

        // 发送批量处理请求
        const response = await fetch('/api/batch/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: currentSessionId
            })
        });

        const result = await response.json();

        if (response.ok && result.success) {
            showToast('批量处理已开始', 'success');
            // 开始监控处理进度
            startBatchProgressMonitoring();
        } else {
            throw new Error(result.error || '批量处理启动失败');
        }

    } catch (error) {
        showToast(`批量处理失败: ${error.message}`, 'error');
        showBatchResult(false, { error: error.message });
    }
}

// 更新处理状态
function updateProcessStatus(status, message, progress = 0) {
    processStatus.textContent = message;
    processStatus.className = 'status-badge ' + status;

    progressFill.style.width = progress + '%';
    progressText.textContent = progress + '%';
}

// 开始批量进度监控
function startBatchProgressMonitoring() {
    if (processingInterval) {
        clearInterval(processingInterval);
    }

    processingInterval = setInterval(async () => {
        try {
            const response = await fetch(`/api/batch/status/${currentSessionId}`);
            const status = await response.json();

            if (response.ok) {
                // 更新进度显示
                updateProcessStatus(status.status, getStatusText(status.status), status.progress);
                processProgress.textContent = `${status.processed_count}/${status.total_count}`;

                if (status.current_file) {
                    currentFileName.textContent = status.current_file;
                }

                // 检查是否完成
                if (status.status === 'completed') {
                    clearInterval(processingInterval);
                    processingInterval = null;

                    showBatchResult(true, {
                        processed_count: status.processed_count,
                        failed_count: status.total_count - status.processed_count,
                        processed_files: status.processed_files,
                        failed_files: status.failed_files,
                        download_url: status.download_url
                    });
                } else if (status.status === 'failed') {
                    clearInterval(processingInterval);
                    processingInterval = null;

                    showBatchResult(false, { error: '批量处理失败' });
                }
            }
        } catch (error) {
            console.error('获取处理状态失败:', error);
        }
    }, 1000); // 每秒更新一次
}

// 显示批量处理结果
function showBatchResult(success, data) {
    statusSection.style.display = 'none';
    resultSection.style.display = 'block';

    if (success) {
        successCard.style.display = 'block';
        errorCard.style.display = 'none';

        // 更新结果摘要
        const successCount = data.processed_count || 0;
        const failedCount = data.failed_count || 0;
        const totalCount = successCount + failedCount;

        resultSummary.innerHTML = `
            <p>📊 处理完成：共 ${totalCount} 个文件</p>
            <p>✅ 成功：${successCount} 个文件</p>
            ${failedCount > 0 ? `<p>❌ 失败：${failedCount} 个文件</p>` : ''}
        `;

        // 设置下载按钮
        if (data.download_url && successCount > 0) {
            downloadBtn.style.display = 'inline-block';
            downloadBtn.onclick = () => {
                window.location.href = data.download_url;
            };
        } else {
            downloadBtn.style.display = 'none';
        }
    } else {
        successCard.style.display = 'none';
        errorCard.style.display = 'block';
        errorMessage.textContent = data.error || '批量处理失败';
    }
}



// 重置批量处理
function resetBatch() {
    currentSessionId = null;
    uploadedFiles = [];

    // 隐藏所有区域
    uploadedFilesSection.style.display = 'none';
    statusSection.style.display = 'none';
    resultSection.style.display = 'none';

    // 重置按钮状态
    processBtn.disabled = true;
    processBtn.textContent = '🚀 开始处理';

    // 清除进度监控
    if (processingInterval) {
        clearInterval(processingInterval);
        processingInterval = null;
    }

    // 清空文件输入
    fileInput.value = '';
}

// 下载批量处理结果
function downloadBatchResult() {
    if (currentSessionId) {
        window.location.href = `/api/batch/download/${currentSessionId}`;
    }
}

// 格式化文件大小
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 获取状态文本
function getStatusText(status) {
    const statusMap = {
        'uploading': '上传中',
        'processing': '处理中',
        'completed': '已完成',
        'failed': '失败'
    };
    return statusMap[status] || status;
}



// 显示提示消息
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// 配置管理
function getCurrentConfig() {
    return {
        document_settings: {
            max_length: parseInt(document.getElementById('maxLength').value),
            min_length: parseInt(document.getElementById('minLength').value),
            sentence_integrity_weight: parseFloat(document.getElementById('sentenceWeight').value),
            preserve_images: document.getElementById('preserveImages').checked,
            table_length_factor: 1.2,
            image_length_factor: 100
        },
        processing_options: {
            debug_mode: false,
            output_folder: "processed",
            skip_existing: false
        },
        advanced_settings: {
            min_split_score: 7,
            heading_score_bonus: 10,
            sentence_end_score_bonus: 6,
            length_score_factor: 100,
            search_window: 5,
            heading_after_penalty: 12,
            force_split_before_heading: true
        }
    };
}

// 加载配置
async function loadConfig() {
    try {
        const response = await fetch('/api/config');
        const config = await response.json();
        
        if (response.ok) {
            // 更新界面配置
            document.getElementById('maxLength').value = config.document_settings?.max_length || 1000;
            document.getElementById('minLength').value = config.document_settings?.min_length || 300;
            document.getElementById('sentenceWeight').value = config.document_settings?.sentence_integrity_weight || 8.0;
            document.getElementById('preserveImages').checked = config.document_settings?.preserve_images !== false;
            
            showToast('配置加载成功', 'success');
        } else {
            throw new Error(config.error || '加载配置失败');
        }
    } catch (error) {
        console.error('加载配置错误:', error);
        showToast('加载配置失败: ' + error.message, 'error');
    }
}

// 保存配置
async function saveConfig() {
    try {
        const config = getCurrentConfig();
        
        const response = await fetch('/api/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            showToast('配置保存成功', 'success');
        } else {
            throw new Error(result.error || '保存配置失败');
        }
    } catch (error) {
        console.error('保存配置错误:', error);
        showToast('保存配置失败: ' + error.message, 'error');
    }
}

// 健康检查
async function healthCheck() {
    try {
        const response = await fetch('/api/health');
        const result = await response.json();
        
        if (response.ok && result.status === 'healthy') {
            console.log('服务健康状态正常');
        }
    } catch (error) {
        console.error('健康检查失败:', error);
    }
}



// 定期健康检查
setInterval(() => {
    healthCheck();
}, 30000); // 每30秒检查一次
