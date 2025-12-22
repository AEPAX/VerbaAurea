#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
VerbaAurea Web服务
将文档处理工具转换为Web服务，提供RESTful API接口
"""

import os
import uuid
import time
import json
import shutil
import zipfile
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, send_file, render_template, send_from_directory

# 导入现有的处理模块
from document_processor import insert_split_markers
from config_manager import load_config, save_config
from utils import setup_logger, log_error, log_info, log_warning

# 设置日志记录器
_logger = setup_logger()

# 创建Flask应用
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB文件大小限制

# 配置目录
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
ALLOWED_EXTENSIONS = {'docx', 'pdf'}

# 确保目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
os.makedirs('templates', exist_ok=True)
os.makedirs('static', exist_ok=True)

# 文件处理状态跟踪
processing_status = {}

# 批量处理会话管理
batch_sessions = {}


def insert_split_markers_with_progress(input_file, output_file, config, progress_callback=None):
    """
    带进度回调的文档处理函数
    """
    try:
        if progress_callback:
            progress_callback(20)

        # 调用原有的处理函数
        success = insert_split_markers(input_file, output_file, config)

        if progress_callback:
            progress_callback(90)

        return success
    except Exception as e:
        log_error(_logger, input_file, e, type(e).__name__, traceback.format_exc())
        return False


def allowed_file(filename):
    """检查文件类型是否允许"""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def cleanup_old_files():
    """清理超过24小时的临时文件"""
    cutoff_time = datetime.now() - timedelta(hours=24)

    for folder in [UPLOAD_FOLDER, PROCESSED_FOLDER]:
        for file_path in Path(folder).glob('*'):
            if file_path.is_file():
                file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_time < cutoff_time:
                    try:
                        file_path.unlink()
                        log_info(_logger, f"清理过期文件: {file_path}")
                    except Exception as e:
                        log_warning(_logger, f"清理文件失败 {file_path}: {e}")


@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')


@app.route('/static/<path:filename>')
def static_files(filename):
    """静态文件服务"""
    return send_from_directory('static', filename)


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """文件上传API - 只上传不处理"""
    try:
        # 检查是否有文件
        if 'file' not in request.files:
            return jsonify({'error': '没有选择文件'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': '只支持.docx和.pdf格式的文件'}), 400

        # 生成唯一文件ID
        file_id = str(uuid.uuid4())
        original_filename = file.filename  # 保持原始文件名
        safe_filename = secure_filename(file.filename)  # 用于文件系统的安全文件名

        # 保存上传的文件（使用安全文件名）
        input_path = os.path.join(UPLOAD_FOLDER, f"{file_id}_{safe_filename}")
        file.save(input_path)

        # 获取会话ID（如果没有则创建新会话）
        session_id = request.form.get('session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            batch_sessions[session_id] = {
                'files': [],
                'created_time': datetime.now().isoformat(),
                'status': 'uploading'
            }

        # 添加文件到会话
        file_info = {
            'file_id': file_id,
            'original_filename': original_filename,
            'file_size': os.path.getsize(input_path),
            'upload_time': datetime.now().isoformat(),
            'input_path': input_path
        }

        if session_id in batch_sessions:
            batch_sessions[session_id]['files'].append(file_info)
        else:
            batch_sessions[session_id] = {
                'files': [file_info],
                'created_time': datetime.now().isoformat(),
                'status': 'uploading'
            }

        return jsonify({
            'success': True,
            'file_id': file_id,
            'session_id': session_id,
            'original_filename': original_filename,
            'file_size': file_info['file_size'],
            'message': '文件上传成功'
        })

    except Exception as e:
        return jsonify({'error': f'上传失败: {str(e)}'}), 500


@app.route('/api/download/<file_id>')
def download_file(file_id):
    """文件下载API - 返回ZIP压缩包"""
    try:
        if file_id not in processing_status:
            return jsonify({'error': '文件不存在'}), 404

        status_info = processing_status[file_id]
        if status_info['status'] != 'completed':
            return jsonify({'error': '文件尚未处理完成'}), 400

        # 查找处理后的文件
        output_filename = f"{file_id}_{status_info['output_filename']}"
        output_path = os.path.join(PROCESSED_FOLDER, output_filename)

        if not os.path.exists(output_path):
            return jsonify({'error': '处理后的文件不存在'}), 404

        # 创建ZIP文件
        zip_filename = f"{file_id}_processed.zip"
        zip_path = os.path.join(PROCESSED_FOLDER, zip_filename)

        # 如果ZIP文件不存在，创建它
        if not os.path.exists(zip_path):
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # 将处理后的文档添加到ZIP中，使用原文件名
                zipf.write(output_path, status_info['output_filename'])

        # 获取原文件名（不含扩展名）用于ZIP文件命名
        original_name = os.path.splitext(status_info['original_filename'])[0]
        zip_download_name = f"{original_name}_processed.zip"

        return send_file(
            zip_path,
            as_attachment=True,
            download_name=zip_download_name,
            mimetype='application/zip'
        )

    except Exception as e:
        return jsonify({'error': f'下载失败: {str(e)}'}), 500


@app.route('/api/batch/process', methods=['POST'])
def process_batch():
    """批量处理API"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')

        if not session_id or session_id not in batch_sessions:
            return jsonify({'error': '无效的会话ID'}), 400

        session = batch_sessions[session_id]
        if not session['files']:
            return jsonify({'error': '没有文件需要处理'}), 400

        # 更新会话状态
        session['status'] = 'processing'
        session['start_time'] = datetime.now().isoformat()
        session['processed_count'] = 0
        session['total_count'] = len(session['files'])
        session['progress'] = 0

        # 加载配置
        config = load_config()

        # 创建批量输出ZIP文件
        batch_id = str(uuid.uuid4())
        zip_filename = f"batch_{batch_id}_processed.zip"
        zip_path = os.path.join(PROCESSED_FOLDER, zip_filename)

        processed_files = []
        failed_files = []

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for i, file_info in enumerate(session['files']):
                try:
                    # 更新进度
                    session['progress'] = int((i / session['total_count']) * 90)  # 90%用于处理，10%用于打包
                    session['current_file'] = file_info['original_filename']

                    # 设置输出路径
                    # 如果输入是PDF，输出应该是DOCX格式
                    original_filename = file_info['original_filename']
                    if original_filename.lower().endswith('.pdf'):
                        # PDF文件输出为DOCX格式
                        output_filename_base = os.path.splitext(original_filename)[0] + '.docx'
                        output_filename_for_zip = f"processed_{output_filename_base}"
                        safe_output_filename = f"processed_{secure_filename(output_filename_base)}"
                    else:
                        output_filename_for_zip = f"processed_{original_filename}"
                        safe_output_filename = f"processed_{secure_filename(original_filename)}"

                    output_path = os.path.join(PROCESSED_FOLDER, f"{file_info['file_id']}_{safe_output_filename}")

                    # 处理文档
                    success = insert_split_markers(file_info['input_path'], output_path, config)

                    if success and os.path.exists(output_path):
                        # 添加到ZIP文件（使用原始文件名）
                        zipf.write(output_path, output_filename_for_zip)
                        processed_files.append(file_info['original_filename'])

                        # 清理临时文件
                        try:
                            os.remove(output_path)
                            os.remove(file_info['input_path'])
                        except:
                            pass
                    else:
                        failed_files.append(file_info['original_filename'])
                        # 记录到日志
                        log_error(_logger, file_info['input_path'],
                                  "处理失败: insert_split_markers返回False或输出文件不存在",
                                  "ProcessingError")

                except Exception as e:
                    error_msg = f"{file_info['original_filename']} (错误: {str(e)})"
                    failed_files.append(error_msg)
                    # 记录详细错误到日志
                    log_error(_logger, file_info['input_path'], e, type(e).__name__, traceback.format_exc())

                session['processed_count'] = i + 1

        # 完成处理
        session['progress'] = 100
        session['status'] = 'completed'
        session['end_time'] = datetime.now().isoformat()
        session['download_url'] = f'/api/batch/download/{session_id}'
        session['zip_path'] = zip_path
        session['processed_files'] = processed_files
        session['failed_files'] = failed_files

        return jsonify({
            'success': True,
            'session_id': session_id,
            'processed_count': len(processed_files),
            'failed_count': len(failed_files),
            'download_url': session['download_url'],
            'message': f'批量处理完成：成功 {len(processed_files)} 个，失败 {len(failed_files)} 个'
        })

    except Exception as e:
        if session_id in batch_sessions:
            batch_sessions[session_id]['status'] = 'failed'
            batch_sessions[session_id]['error'] = str(e)
        return jsonify({'error': f'批量处理失败: {str(e)}'}), 500


@app.route('/api/batch/download/<session_id>')
def download_batch(session_id):
    """批量下载API"""
    try:
        if session_id not in batch_sessions:
            return jsonify({'error': '会话不存在'}), 404

        session = batch_sessions[session_id]
        if session['status'] != 'completed':
            return jsonify({'error': '批量处理尚未完成'}), 400

        if 'zip_path' not in session or not os.path.exists(session['zip_path']):
            return jsonify({'error': '处理结果文件不存在'}), 404

        # 生成下载文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        download_name = f"VerbaAurea_批量处理_{timestamp}.zip"

        return send_file(
            session['zip_path'],
            as_attachment=True,
            download_name=download_name,
            mimetype='application/zip'
        )

    except Exception as e:
        return jsonify({'error': f'下载失败: {str(e)}'}), 500


@app.route('/api/batch/status/<session_id>')
def get_batch_status(session_id):
    """获取批量处理状态"""
    if session_id not in batch_sessions:
        return jsonify({'error': '会话不存在'}), 404

    session = batch_sessions[session_id]
    return jsonify({
        'session_id': session_id,
        'status': session['status'],
        'progress': session.get('progress', 0),
        'processed_count': session.get('processed_count', 0),
        'total_count': session.get('total_count', len(session['files'])),
        'current_file': session.get('current_file', ''),
        'files': [{'filename': f['original_filename'], 'size': f['file_size']} for f in session['files']],
        'processed_files': session.get('processed_files', []),
        'failed_files': session.get('failed_files', []),
        'download_url': session.get('download_url', ''),
        'start_time': session.get('start_time', ''),
        'end_time': session.get('end_time', '')
    })


@app.route('/api/batch/remove-file', methods=['POST'])
def remove_file_from_batch():
    """从批量处理中移除文件"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        file_id = data.get('file_id')

        if not session_id or session_id not in batch_sessions:
            return jsonify({'error': '无效的会话ID'}), 400

        session = batch_sessions[session_id]
        if session['status'] != 'uploading':
            return jsonify({'error': '只能在上传阶段移除文件'}), 400

        # 查找并移除文件
        for i, file_info in enumerate(session['files']):
            if file_info['file_id'] == file_id:
                # 删除物理文件
                try:
                    if os.path.exists(file_info['input_path']):
                        os.remove(file_info['input_path'])
                except:
                    pass

                # 从列表中移除
                session['files'].pop(i)
                return jsonify({'success': True, 'message': '文件已移除'})

        return jsonify({'error': '文件不存在'}), 404

    except Exception as e:
        return jsonify({'error': f'移除文件失败: {str(e)}'}), 500


@app.route('/api/status/<file_id>')
def get_status(file_id):
    """获取文件处理状态"""
    if file_id not in processing_status:
        return jsonify({'error': '文件不存在'}), 404

    return jsonify(processing_status[file_id])


@app.route('/api/config', methods=['GET'])
def get_config():
    """获取当前配置"""
    try:
        config = load_config()
        return jsonify(config)
    except Exception as e:
        return jsonify({'error': f'获取配置失败: {str(e)}'}), 500


@app.route('/api/config', methods=['POST'])
def update_config():
    """更新配置"""
    try:
        new_config = request.get_json()
        if not new_config:
            return jsonify({'error': '无效的配置数据'}), 400

        # 保存配置
        save_config(new_config)
        return jsonify({'success': True, 'message': '配置已更新'})

    except Exception as e:
        return jsonify({'error': f'更新配置失败: {str(e)}'}), 500


@app.route('/api/health')
def health_check():
    """健康检查API"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })


def cleanup_task():
    """定期清理任务"""
    cleanup_old_files()
    cutoff_time = datetime.now() - timedelta(hours=24)

    # 清理过期的处理状态
    expired_ids = []
    for file_id, status_info in processing_status.items():
        try:
            start_time = datetime.fromisoformat(status_info['start_time'])
            if start_time < cutoff_time:
                expired_ids.append(file_id)
        except:
            expired_ids.append(file_id)

    for file_id in expired_ids:
        del processing_status[file_id]

    # 清理过期的批量会话
    expired_sessions = []
    for session_id, session_info in batch_sessions.items():
        try:
            created_time = datetime.fromisoformat(session_info['created_time'])
            if created_time < cutoff_time:
                # 清理会话相关文件
                if 'zip_path' in session_info and os.path.exists(session_info['zip_path']):
                    try:
                        os.remove(session_info['zip_path'])
                    except:
                        pass

                # 清理未处理的上传文件
                for file_info in session_info.get('files', []):
                    if 'input_path' in file_info and os.path.exists(file_info['input_path']):
                        try:
                            os.remove(file_info['input_path'])
                        except:
                            pass

                expired_sessions.append(session_id)
        except:
            expired_sessions.append(session_id)

    for session_id in expired_sessions:
        del batch_sessions[session_id]


if __name__ == '__main__':
    # 设置控制台编码
    import sys

    if sys.platform == 'win32':
        import codecs

        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

    # 初始化错误日志记录器
    try:
        from utils import get_error_logger, get_log_file_path, get_error_log_file_path

        error_logger = get_error_logger()
        log_file = get_log_file_path(_logger)
        error_log_file = get_error_log_file_path()
        if log_file:
            print(f"📝 日志文件: {log_file}")
        if error_log_file:
            print(f"📝 错误日志文件: {error_log_file}")
    except Exception:
        pass

    log_info(_logger, "🚀 启动 VerbaAurea Web服务...")
    log_info(_logger, f"📍 服务地址: http://localhost:18080")
    log_info(_logger, f"📁 上传目录: {os.path.abspath(UPLOAD_FOLDER)}")
    log_info(_logger, f"📁 输出目录: {os.path.abspath(PROCESSED_FOLDER)}")
    print("🚀 启动 VerbaAurea Web服务...")
    print("📍 服务地址: http://localhost:18080")
    print("📁 上传目录:", os.path.abspath(UPLOAD_FOLDER))
    print("📁 输出目录:", os.path.abspath(PROCESSED_FOLDER))

    # 启动时清理一次
    cleanup_task()

    # 启动Flask应用
    app.run(host='0.0.0.0', port=18080, debug=True)
