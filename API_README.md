# VerbaAurea Document Processing API

[中文](./API_README.md) | [English](./API_README_EN.md)

## 概述

VerbaAurea Document Processing API 是基于模块化架构构建的生产级RESTful API服务。它提供智能的Word文档分割功能，通过先进的语义分析算法在文档的适当位置插入分隔符，为知识库构建提供高质量的文档切分服务。

## 主要特性

- 🚀 **高性能**: 基于FastAPI构建，支持异步处理
- 📄 **智能分割**: 基于标题识别、语义结构分析、长度控制等多种策略
- 🖼️ **图片保留**: 完整保留文档中的图片和格式
- 📊 **表格支持**: 完整复制表格结构和内容
- 🔒 **生产级**: 包含错误处理、日志记录、健康检查等特性
- 🐳 **容器化**: 提供Docker部署支持
- 📖 **自动文档**: 自动生成API文档

## 快速开始

### 方式一：Docker部署（推荐）

1. **克隆项目**
```bash
git clone <repository-url>
cd VerbaAurea
```

2. **构建并启动服务**
```bash
# 开发环境
docker-compose up verba-aurea-api

# 生产环境（包含Nginx）
docker-compose --profile production up -d
```

3. **访问API文档**
- Swagger UI: http://localhost:8000/docs
- ReDoc文档: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

### 方式二：本地开发

1. **安装依赖**
```bash
pip install -r requirements-api.txt
```

2. **启动服务**
```bash
cd api
python main.py
```

## API端点

### 文档处理

#### POST /api/v1/process-document
处理Word文档并返回处理结果信息。

**请求参数:**
- `file`: Word文档文件（.docx格式）
- `config`: 可选的处理配置（JSON格式）
- `debug_mode`: 是否启用调试模式

**响应示例:**
```json
{
  "success": true,
  "message": "文档处理成功",
  "request_id": "req_123456789",
  "timestamp": "2025-01-21T10:30:00.123456",
  "data": {
    "split_count": 5,
    "processing_time": 2.34,
    "file_size_before": 1024000,
    "file_size_after": 1025000,
    "element_count": 50,
    "paragraph_count": 45,
    "table_count": 2,
    "image_count": 3,
    "has_images": true,
    "heading_count": 8,
    "split_points": [12, 25, 38, 51, 64],
    "avg_segment_length": 850.5,
    "min_segment_length": 320,
    "max_segment_length": 1200
  },
  "filename": "processed_document.docx"
}
```

#### POST /api/v1/process-document/download
处理Word文档并直接返回处理后的文件。

### 健康检查

#### GET /api/v1/health
获取服务健康状态。

#### GET /api/v1/health/metrics
获取性能指标和统计信息。

#### GET /api/v1/health/dependencies
检查所有依赖库的可用性。

#### GET /api/v1/health/system
获取系统和运行环境信息。

### 配置管理

#### GET /api/v1/config
获取当前配置。

#### PUT /api/v1/config
更新配置参数。

#### GET /api/v1/config/default
获取系统默认配置。

#### POST /api/v1/config/reset
重置配置为默认值。

#### GET /api/v1/config/validate
验证当前配置的有效性。

## 配置参数

### 文档设置
- `max_length`: 最大段落长度（默认: 1000）
- `min_length`: 最小段落长度（默认: 300）
- `sentence_integrity_weight`: 句子完整性权重（默认: 8.0）
- `preserve_images`: 是否保留图片（默认: true）

### 高级设置
- `min_split_score`: 最小分割得分（默认: 7.0）
- `heading_score_bonus`: 标题加分（默认: 10.0）
- `search_window`: 搜索窗口大小（默认: 5）

## 使用示例

### Python客户端示例

```python
import requests

# 处理文档并获取结果信息
with open('document.docx', 'rb') as f:
    files = {'file': f}
    data = {
        'debug_mode': False,
        'config': '{"max_length": 1200, "min_length": 400}'
    }

    response = requests.post(
        'http://localhost:8000/api/v1/process-document',
        files=files,
        data=data
    )

    if response.status_code == 200:
        result = response.json()
        print(f"处理成功，插入了 {result['data']['split_count']} 个分隔符")
        print(f"处理时间: {result['data']['processing_time']}秒")
        print(f"平均段落长度: {result['data']['avg_segment_length']}")
    else:
        print(f"处理失败: {response.text}")

# 直接下载处理后的文档
with open('document.docx', 'rb') as f:
    files = {'file': f}

    response = requests.post(
        'http://localhost:8000/api/v1/process-document/download',
        files=files
    )

    if response.status_code == 200:
        with open('processed_document.docx', 'wb') as output_file:
            output_file.write(response.content)
        print("文档下载成功")
    else:
        print(f"下载失败: {response.text}")
```

### cURL示例

```bash
# 处理文档
curl -X POST "http://localhost:8000/api/v1/process-document" \
  -F "file=@document.docx" \
  -F "debug_mode=false"

# 下载处理后的文档
curl -X POST "http://localhost:8000/api/v1/process-document/download" \
  -F "file=@document.docx" \
  -o "processed_document.docx"

# 健康检查
curl -X GET "http://localhost:8000/api/v1/health"

# 获取配置
curl -X GET "http://localhost:8000/api/v1/config"

# 获取性能指标
curl -X GET "http://localhost:8000/api/v1/health/metrics"
```

## 环境变量配置

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| `VERBA_DEBUG` | 调试模式 | false |
| `VERBA_LOG_LEVEL` | 日志级别 | INFO |
| `VERBA_MAX_FILE_SIZE` | 最大文件大小 | 52428800 (50MB) |
| `VERBA_REQUEST_TIMEOUT` | 请求超时时间 | 300 |

## 部署建议

### 生产环境部署

1. **使用Nginx反向代理**
2. **配置SSL证书**
3. **设置适当的资源限制**
4. **配置日志轮转**
5. **设置监控和告警**

### 性能优化

- 根据服务器配置调整 `MAX_CONCURRENT_REQUESTS`
- 合理设置文件大小限制
- 配置适当的超时时间
- 使用负载均衡器进行水平扩展

## 故障排除

### 常见问题

1. **文件上传失败**
   - 检查文件大小是否超过限制（默认50MB）
   - 确认文件格式为.docx
   - 检查文件是否损坏

2. **处理超时**
   - 增加 `REQUEST_TIMEOUT` 设置（默认300秒）
   - 检查文档复杂度和大小
   - 对于大型文档，考虑分批处理

3. **内存不足**
   - 减少 `MAX_CONCURRENT_REQUESTS`（默认10）
   - 增加服务器内存
   - 监控系统资源使用情况

4. **编码问题**
   - API服务已自动处理中文编码问题
   - 确保客户端使用UTF-8编码
   - 调试模式在API环境下已优化

5. **端口冲突**
   - 默认端口8000，如被占用可修改为其他端口
   - 使用 `--port` 参数指定端口
   - 检查防火墙设置

### 日志查看

```bash
# Docker环境
docker logs verba-aurea-api

# 本地环境（查看控制台输出）
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000

# 或使用启动脚本
python start_api.py --log-level debug
```

### 测试API服务

项目提供了完整的测试脚本：

```bash
# 运行API功能测试
python test_api.py
```

测试脚本会自动检查：
- 健康检查端点
- 文档处理功能
- 文档下载功能
- 配置管理端点
- 错误处理机制
- API文档可访问性
- 性能指标端点

## 开发指南

### 项目结构
```
api/
├── main.py              # FastAPI应用入口
├── models/              # 数据模型
├── routers/             # API路由
├── services/            # 业务服务
├── utils/               # 工具函数
├── middleware/          # 中间件
└── config/              # 配置管理
```

### 添加新功能

1. 在 `models/` 中定义数据模型
2. 在 `services/` 中实现业务逻辑
3. 在 `routers/` 中添加API端点
4. 更新API文档

## 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。
