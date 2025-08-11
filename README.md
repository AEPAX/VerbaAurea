# 📚 VerbaAurea 🌟

中文 [中文](./README.md) | 英文 [English](./README_EN.md)

VerbaAurea 是一个智能文档预处理工具，致力于将原始文档转化为"黄金"般的知识，为知识库构建提供高质量的文本数据。它专注于文档智能分割，确保语义完整性，为知识库检索和大语言模型微调提供优质素材。

## 项目特点

- **智能文档分割** - 基于句子边界和语义完整性进行精准分段，支持DOCX格式文档
- **多维度评分系统** - 考虑标题、句子完整性、段落长度等多种因素决定最佳分割点
- **语义完整性保护** - 优先保证句子和语义单元的完整，避免在句子中间断开
- **Web界面支持** - 提供现代化的Web界面，支持拖拽上传和批量处理
- **批量处理能力** - 支持同时处理多个文档，统一打包下载处理结果
- **可配置化设计** - 通过配置文件或Web界面灵活调整分割策略
- **多语言支持** - 针对中英文文本采用不同的句子分割策略
- **格式保留** - 保留原始文档的格式信息，包括样式、字体和表格

## 应用场景

- **知识库构建** - 为检索式问答系统提供合适粒度的文本单元

- **语料库准备** - 为大语言模型微调准备高质量的训练数据

- **文档索引** - 优化文档检索系统的索引单元

- **内容管理** - 改进内容管理系统中的文档组织方式

  
## 项目结构

```
├── main.py                 # 命令行主程序入口
├── web_service.py          # Web服务主程序
├── config_manager.py       # 配置管理
├── document_processor.py   # 文档处理核心
├── text_analysis.py        # 文本分析功能
├── parallel_processor.py   # 并行处理实现
├── utils.py                # 工具函数
├── config.json            # 配置文件
├── requirements.txt       # 项目依赖
├── templates/             # Web界面模板
│   └── index.html         # 主页面模板
├── static/                # 静态资源
│   ├── style.css          # 样式文件
│   └── script.js          # 前端脚本
├── uploads/               # 上传文件临时目录
├── processed/             # 处理结果目录
├── README.md              # 中文文档
├── README_EN.md           # 英文文档
├── LICENSE                # 开源许可证
└── 启动Web服务.bat        # Windows快速启动脚本
```



## 核心功能

- **句子边界检测** - 结合规则和NLP技术，精确识别句子边界
- **分割点评分系统** - 多维度评分，选择最佳分割点
- **语义块分析** - 分析文档结构，保留段落间的语义联系
- **自适应长度控制** - 根据配置自动调整文本片段长度
- **格式保留处理** - 在分割的同时保留文档原始格式

## 安装说明

### 环境要求

- Python 3.6 或更高版本
- 支持 Windows、macOS 和 Linux 系统



### 安装步骤

1. 克隆项目到本地

```bash
git clone https://github.com/yourusername/VerbaAurea.git
cd VerbaAurea
```

2. 安装依赖

```bash
pip install -r requirements.txt
```

## 使用指南

### Web界面使用（推荐）

1. 启动Web服务

```bash
python web_service.py
```

或在Windows系统中双击 `启动Web服务.bat` 文件

2. 打开浏览器访问 `http://localhost:18080`

3. 使用Web界面进行文档处理：
   - **上传文件**：拖拽DOCX文件到上传区域或点击选择文件
   - **批量处理**：支持同时上传多个文件
   - **文件管理**：可以预览已上传文件，移除不需要的文件
   - **开始处理**：点击"开始处理"按钮统一处理所有文件
   - **实时进度**：查看处理进度和状态
   - **下载结果**：处理完成后下载ZIP压缩包

### 命令行使用

1. 将需要处理的Word文档放在脚本所在目录或子目录中
2. 运行主脚本

```bash
python main.py
```

3. 根据菜单选择操作:
   - 选择 `1` 开始处理文档
   - 选择 `2` 查看当前配置
   - 选择 `3` 编辑配置
   - 选择 `4` 退出程序

4. 处理后的文档将保存在`processed`(默认)或自定义的输出文件夹中

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

## Web界面特性

- **现代化界面** - 响应式设计，支持桌面和移动设备
- **拖拽上传** - 支持拖拽文件到上传区域
- **批量处理** - 一次处理多个文档，提高工作效率
- **实时进度** - 显示处理进度和当前处理文件
- **文件管理** - 上传后可预览和管理文件列表
- **配置调整** - 在线调整处理参数
- **结果下载** - 处理完成后统一打包下载

## 开发计划

- ✅ Web界面支持
- ✅ 批量文档处理
- ✅ 拖拽上传功能
- 🔄 添加对更多文档格式的支持
- 🔄 增强语义分析能力，使用更先进的NLP模型
- 🔄 添加文档预览功能

## 常见问题

**Q: 为什么分割后的文档中有些段落太短或太长？**

A: 尝试调整配置文件中的 `max_length` 和 `min_length` 参数，平衡分割粒度。

**Q: 如何避免句子被分割在中间？**

A: 提高 `sentence_integrity_weight` 参数值，默认值为 8.0，可以尝试设置为 10.0 或更高。

**Q: 如何处理特殊格式的文档？**

A: 对于特殊格式，可以通过调整高级设置中的评分参数来适应不同的文档结构。

## API 接口

以下为主要API端点，所有接口均返回JSON（除下载接口）：

- 健康检查
  - 方法: GET
  - 路径: /api/health
  - 示例:
    ```bash
    curl -s http://localhost:18080/api/health
    ```

- 获取/更新配置
  - 方法: GET / POST
  - 路径: /api/config
  - 示例（获取配置）:
    ```bash
    curl -s http://localhost:18080/api/config
    ```
  - 示例（更新配置）:
    ```bash
    curl -s -X POST http://localhost:18080/api/config \
      -H "Content-Type: application/json" \
      -d '{"document_settings": {"max_length": 1200, "min_length": 200}}'
    ```

- 上传文件（只上传，不立即处理）
  - 方法: POST (multipart/form-data)
  - 路径: /api/upload
  - 参数: file (必填), session_id (可选，首次不传会自动创建)
  - 返回: { success, session_id, file_id, original_filename, file_size, message }
  - 示例:
    ```bash
    curl -s -F "file=@/path/to/file.docx" http://localhost:18080/api/upload
    ```

- 启动批量处理
  - 方法: POST (application/json)
  - 路径: /api/batch/process
  - 请求体: { "session_id": "<会话ID>" }
  - 返回: { success, session_id, processed_count, failed_count, download_url, message }
  - 示例:
    ```bash
    curl -s -X POST http://localhost:18080/api/batch/process \
      -H "Content-Type: application/json" \
      -d '{"session_id": "<SESSION_ID>"}'
    ```

- 查询批量处理状态
  - 方法: GET
  - 路径: /api/batch/status/<session_id>
  - 返回: { status, progress, processed_count, total_count, current_file, files[], download_url }
  - 示例:
    ```bash
    curl -s http://localhost:18080/api/batch/status/<SESSION_ID>
    ```

- 批量结果下载（ZIP）
  - 方法: GET
  - 路径: /api/batch/download/<session_id>
  - 返回: ZIP文件（Content-Disposition 附件）
  - 示例:
    ```bash
    curl -L -o result.zip http://localhost:18080/api/batch/download/<SESSION_ID>
    ```

- 从批处理中移除文件
  - 方法: POST (application/json)
  - 路径: /api/batch/remove-file
  - 请求体: { "session_id": "<会话ID>", "file_id": "<文件ID>" }
  - 返回: { success, message }
  - 示例:
    ```bash
    curl -s -X POST http://localhost:18080/api/batch/remove-file \
      -H "Content-Type: application/json" \
      -d '{"session_id": "<SESSION_ID>", "file_id": "<FILE_ID>"}'
    ```

- 单文件下载（兼容保留）
  - 方法: GET
  - 路径: /api/download/<file_id>
  - 说明: 仅对历史接口兼容保留，新流程建议使用批量下载

## 贡献指南

欢迎对VerbaAurea项目做出贡献! 您可以通过以下方式参与:

1. 报告Bug或提出功能建议
2. 提交Pull Request改进代码
3. 完善文档和使用示例
4. 分享您使用VerbaAurea的经验和案例

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=AEPAX/VerbaAurea&type=Date)](https://www.star-history.com/#AEPAX/VerbaAurea&Date)

本项目使用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可协议。
