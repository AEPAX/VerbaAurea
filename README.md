# 📚 VerbaAurea 🌟

[中文](./README.md) | [English](./README_EN.md)

VerbaAurea 是一个智能文档预处理工具，致力于将原始文档转化为"黄金"般的知识，为知识库构建提供高质量的文本数据。它专注于文档智能分割，确保语义完整性，为知识库检索和大语言模型微调提供优质素材。

## ✨ 主要特性

- **🧠 智能文档分割** - 基于语义结构和句子边界的精准分段
- **🔌 模块化架构** - 支持轻松扩展PDF、Excel、PowerPoint等格式
- **🖼️ 完整图片保留** - 保持图片在原始位置，支持高质量图片处理
- **📊 表格结构保护** - 完整复制表格结构和内容
- **⚡ 高性能处理** - 支持并行处理和批量操作
- **🌐 RESTful API** - 生产级API服务，支持远程调用和系统集成
- **🖥️ 友好CLI界面** - 直观的命令行界面，支持交互式操作
- **🐳 容器化部署** - 提供Docker支持，便于生产环境部署
- **🔧 灵活配置** - 丰富的配置选项，支持多种处理策略

## 🏗️ 架构设计

VerbaAurea 采用分层模块化架构：

```
verba_aurea/
├── core/                    # 核心业务逻辑层
│   ├── processors/          # 文件处理器（插件化）
│   ├── analyzers/          # 文本分析器
│   ├── splitters/          # 分割策略
│   └── models/             # 核心数据模型
├── services/               # 服务层
├── interfaces/             # 接口层
│   ├── api/               # REST API
│   └── cli/               # 命令行接口
├── config/                # 统一配置管理
└── tests/                 # 完整测试套件
```

### 🔌 插件化扩展

```python
# 轻松添加新格式支持
from verba_aurea.core.processors import register_processor

class PDFProcessor(BaseProcessor):
    # 实现PDF处理逻辑
    pass

register_processor('.pdf', PDFProcessor)
```

## 应用场景

- **知识库构建** - 为检索式问答系统提供合适粒度的文本单元

- **语料库准备** - 为大语言模型微调准备高质量的训练数据

- **文档索引** - 优化文档检索系统的索引单元

- **内容管理** - 改进内容管理系统中的文档组织方式
- **API集成** - 通过RESTful API集成到现有系统和工作流中

## 🏗️ 项目架构

VerbaAurea 采用现代化的分层模块化架构：

```
├── main.py                 # 主程序入口（使用新架构CLI）
├── start_api.py            # API服务启动脚本
├── verba_aurea/            # 新架构核心模块
│   ├── core/              # 核心业务逻辑
│   │   ├── analyzers/     # 文档分析器
│   │   ├── models/        # 数据模型
│   │   ├── processors/    # 文档处理器
│   │   └── splitters/     # 文档分割器
│   ├── services/          # 服务层
│   │   ├── document_service.py    # 文档服务
│   │   └── processing_service.py  # 处理服务
│   ├── interfaces/        # 接口层
│   │   ├── api/          # API接口适配器
│   │   └── cli/          # 命令行接口
│   ├── config/           # 配置管理
│   │   ├── settings.py   # 配置设置
│   │   └── manager.py    # 配置管理器
│   ├── tests/            # 测试套件
│   │   ├── api/         # API测试
│   │   ├── functional/  # 功能测试
│   │   ├── unit/        # 单元测试
│   │   └── integration/ # 集成测试
│   └── legacy_adapter.py # 向后兼容适配器
├── api/                   # API服务目录（兼容层）
│   ├── main.py           # FastAPI应用入口
│   ├── models/           # 数据模型
│   ├── routers/          # API路由
│   ├── services/         # 业务服务
│   ├── utils/            # API工具函数
│   ├── middleware/       # 中间件
│   └── config/           # API配置
├── config.json           # 配置文件
├── requirements.txt      # 基础依赖
├── requirements-api.txt  # API服务依赖
├── Dockerfile            # Docker构建文件
├── docker-compose.yml    # Docker Compose配置
├── API_README.md         # API服务详细文档
├── README.md             # 中文文档
├── README_EN.md          # 英文文档
├── LICENSE               # 开源许可证
└── 企业库/               # 示例文档目录
```



## 核心功能

- **句子边界检测** - 结合规则和NLP技术，精确识别句子边界
- **分割点评分系统** - 多维度评分，选择最佳分割点
- **语义块分析** - 分析文档结构，保留段落间的语义联系
- **自适应长度控制** - 根据配置自动调整文本片段长度
- **格式保留处理** - 在分割的同时保留文档原始格式

## 🚀 快速开始

### 环境要求

- Python 3.8 或更高版本
- 支持 Windows、macOS 和 Linux 系统

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/yourusername/VerbaAurea.git
cd VerbaAurea
```

2. **安装依赖**

```bash
# 安装命令行版本依赖
pip install -r requirements.txt

# 或安装API服务依赖
pip install -r requirements-api.txt
```

## 📖 使用指南

VerbaAurea 提供三种使用方式：

### 方式一：命令行工具

```bash
python main.py
```

### 方式二：API服务

```bash
# 启动API服务
python start_api.py --host 0.0.0.0 --port 8000

# 或使用Docker
docker-compose up verba-aurea-api
```

### 方式三：Python库

```python
# 使用新架构（推荐）
from verba_aurea.services import DocumentService
from verba_aurea.config import get_settings

settings = get_settings()
service = DocumentService(settings)

result = service.process_document(
    input_file=Path("document.docx"),
    config=settings.get_config()
)

print(f"处理完成，插入了 {result.split_count} 个分隔符")

# 或使用传统方式（向后兼容）
from document_processor import insert_split_markers
from config_manager import load_config

config = load_config()
success = insert_split_markers("input.docx", "output.docx", config)

# 生产环境（包含Nginx）
docker-compose --profile production up -d
```

3. **访问API文档**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

#### API使用示例

**Python客户端示例：**
```python
import requests

# 处理文档
with open('document.docx', 'rb') as f:
    files = {'file': f}
    data = {'debug_mode': False}

    response = requests.post(
        'http://localhost:8000/api/v1/process-document',
        files=files,
        data=data
    )

    result = response.json()
    print(f"处理成功，插入了 {result['data']['split_count']} 个分隔符")
```

**主要API端点：**
- `POST /api/v1/process-document` - 处理文档并返回结果信息
- `POST /api/v1/process-document/download` - 处理文档并直接下载
- `GET /api/v1/health` - 健康检查
- `GET /api/v1/config` - 获取配置
- `PUT /api/v1/config` - 更新配置

详细的API文档请参考：[API_README.md](./API_README.md)

## 🧪 测试

VerbaAurea 提供完整的测试套件，确保功能的可靠性和稳定性。

### 测试结构

```
verba_aurea/tests/
├── api/                     # API测试
│   └── test_api_endpoints.py
├── functional/              # 功能测试
│   └── test_image_processing.py
├── unit/                    # 单元测试
└── integration/             # 集成测试
```

### 运行测试

#### 使用统一测试运行器（推荐）

```bash
# 运行所有测试
python run_tests.py

# 运行特定类型的测试
python run_tests.py --type api          # API测试
python run_tests.py --type functional   # 功能测试
python run_tests.py --type unit         # 单元测试
python run_tests.py --type integration  # 集成测试

# 检查测试依赖
python run_tests.py --check-deps
```

#### 单独运行测试

```bash
# API测试（需要先启动API服务）
python start_api.py  # 在另一个终端启动
python verba_aurea/tests/api/test_api_endpoints.py

# 功能测试
python verba_aurea/tests/functional/test_image_processing.py

# 使用pytest运行（需要安装pytest）
pytest verba_aurea/tests/unit/ -v
pytest verba_aurea/tests/integration/ -v
```

### 测试覆盖

- **API端点测试** - 验证所有API端点的功能和响应
- **图片处理测试** - 验证图片识别、保留和质量保持
- **文档分析测试** - 验证文档结构分析和元素提取
- **配置管理测试** - 验证配置加载、验证和更新
- **错误处理测试** - 验证各种错误情况的处理
- **性能测试** - 验证处理速度和资源使用

### 测试报告

测试完成后会生成详细的测试报告，包括：
- 测试通过率
- 性能指标
- 错误详情
- 改进建议

查看历史测试报告：[docs/API_TEST_REPORT.md](./docs/API_TEST_REPORT.md)

### 配置说明

可以通过菜单编辑或直接修改`config.json`文件定制分割参数:

#### 文档设置

- `max_length`: 最大段落长度。控制每个分割后文本块的最大字符数。过大可能导致检索效率下降，过小可能破坏语义完整性。
- `min_length`: 最小段落长度。(防止生成太短的片段。过短的文本块可能缺乏足够上下文，影响知识库质量。
- `sentence_integrity_weight`: 句子完整性权重。值越大，系统越倾向于保持句子完整，减少在句子中间分割的可能性。

#### 处理选项

- `debug_mode`: 调试模式。启用后会输出详细的处理信息，包括分割点评分、计算过程等。(该设置目前主要用于算法优化研究上)。
- `output_folder`: 输出文件夹名称。处理后的文档将保存在此文件夹中，保持原始目录结构。
- `skip_existing`: 是否跳过已存在的文件

#### 高级设置

- `min_split_score`: 最小分割得分。只有评分高于此值的位置才会被选为分割点。提高此值可减少分割点数量。
- `heading_score_bonus`: 标题加分值。在标题前后分割通常更合理，此参数控制标题位置的优先级。
- `sentence_end_score_bonus`: 句子结束加分值。增加此值会优先在句子边界处分割，提高文档语义完整性。
- `length_score_factor`: 长度评分因子。控制段落长度对评分的影响程度，较大值会产生更均匀的分割。
- `search_window`: 搜索窗口大小。当需要调整分割点到句子边界时，系统会在此窗口范围内搜索最近的句子边界。

#### 性能设置

- `num_workers`: 工作进程数。设为0会自动使用(CPU核心数-1)个进程。可根据系统资源情况调整。
- `cache_size`: 缓存大小。用于存储文本分析结果以避免重复计算，提高处理速度。单位为条目数。
- `batch_size`: 批处理大小。每个工作进程一次处理的文件数，较大值可减少进程切换开销。

### 最佳实践

- **设置合理的长度范围** - 根据知识库，微调或应用需求，设置合适的最大和最小段落长度
- **调整句子完整性权重** - 如果出现句子被分割的情况，提高此权重

## 工作原理

1. **文档解析** - 解析文档，提取文本、样式和结构信息
2. **段落分析** - 分析每个段落的特征，如长度、是否为标题、是否以句号结尾等
3. **评分计算** - 为每个潜在分割点计算综合评分
4. **分割点选择** - 基于评分和配置选择最佳分割点
5. **句子边界校正** - 调整分割点位置，在句子边界处分割
6. **分割标记插入** - 在选定的位置插入`<!--split-->`标记
7. **格式保留** - 保留原文档的格式信息并保存为新文档

## 开发计划

- ✅ RESTful API服务
- ✅ Docker容器化部署
- 🔄 添加对更多文档格式的支持（PDF、TXT等）
- 🔄 实现图形用户界面
- 🔄 增强语义分析能力，使用更先进的NLP模型
- 🔄 支持批量文档处理API
- 🔄 添加文档处理队列和异步处理

## 常见问题

**Q: 为什么分割后的文档中有些段落太短或太长？**

A: 尝试调整配置文件中的 `max_length` 和 `min_length` 参数，平衡分割粒度。

**Q: 如何避免句子被分割在中间？**

A: 提高 `sentence_integrity_weight` 参数值，默认值为 8.0，可以尝试设置为 10.0 或更高。

**Q: 如何处理特殊格式的文档？**

A: 对于特殊格式，可以通过调整高级设置中的评分参数来适应不同的文档结构。

**Q: API服务和命令行工具有什么区别？**

A: API服务提供RESTful接口，支持远程调用和系统集成，适合生产环境；命令行工具适合本地批量处理和开发测试。

**Q: 如何在生产环境中部署API服务？**

A: 推荐使用Docker部署，运行 `docker-compose --profile production up -d` 即可启动包含Nginx反向代理的完整服务。

## 贡献指南

欢迎对VerbaAurea项目做出贡献! 您可以通过以下方式参与:

1. 报告Bug或提出功能建议
2. 提交Pull Request改进代码
3. 完善文档和使用示例
4. 分享您使用VerbaAurea的经验和案例

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=AEPAX/VerbaAurea&type=Date)](https://www.star-history.com/#AEPAX/VerbaAurea&Date)

本项目使用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可协议。
