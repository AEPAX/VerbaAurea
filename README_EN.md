# 📚 VerbaAurea 🌟

中文 [中文](./README.md) | 英文 [English](./README_EN.md)

VerbaAurea is an intelligent document preprocessing tool dedicated to transforming raw documents into "golden" knowledge, providing high-quality text data for knowledge base construction. It focuses on intelligent document segmentation, ensuring semantic integrity, and delivers premium material for knowledge base retrieval and large language model fine-tuning.

## Project Features

- **Intelligent Document Segmentation** - Precise segmentation based on sentence boundaries and semantic integrity, supporting DOCX format documents
- **Multi-dimensional Scoring System** - Considers titles, sentence integrity, paragraph length, and other factors to determine optimal split points
- **Semantic Integrity Protection** - Prioritizes the completeness of sentences and semantic units, avoiding breaks in the middle of sentences
- **Web Interface Support** - Provides modern web interface with drag-and-drop upload and batch processing
- **Batch Processing Capability** - Supports processing multiple documents simultaneously with unified download
- **Configurable Design** - Flexibly adjust segmentation strategies through configuration files or web interface
- **Multi-language Support** - Employs different sentence segmentation strategies for Chinese and English texts
- **Format Preservation** - Maintains the original document's formatting information, including styles, fonts, and tables

## Application Scenarios

- **Knowledge Base Construction** - Provides text units of appropriate granularity for retrieval-based question answering systems

- **Corpus Preparation** - Prepares high-quality training data for large language model fine-tuning

- **Document Indexing** - Optimizes index units for document retrieval systems

- **Content Management** - Improves document organization in content management systems

  
## Project Structure

```
├── main.py                 # Command-line main program
├── web_service.py          # Web service main program
├── config_manager.py       # Configuration management
├── document_processor.py   # Document processing core
├── text_analysis.py        # Text analysis functionality
├── parallel_processor.py   # Parallel processing implementation
├── utils.py                # Utility functions
├── config.json            # Configuration file
├── requirements.txt       # Project dependencies
├── templates/             # Web interface templates
│   └── index.html         # Main page template
├── static/                # Static resources
│   ├── style.css          # Stylesheet
│   └── script.js          # Frontend scripts
├── uploads/               # Upload temporary directory
├── processed/             # Processing results directory
├── README.md              # Chinese documentation
├── README_EN.md           # English documentation
├── LICENSE                # Open source license
└── 启动Web服务.bat        # Windows quick start script
```



## Core Functions

- **Sentence Boundary Detection** - Precisely identifies sentence boundaries by combining rules and NLP techniques
- **Split Point Scoring System** - Multi-dimensional scoring to select optimal split points
- **Semantic Block Analysis** - Analyzes document structure, preserving semantic connections between paragraphs
- **Adaptive Length Control** - Automatically adjusts text fragment length based on configuration
- **Format Preservation Processing** - Maintains the original document format while splitting

## Installation Guide

### Requirements

- Python 3.6 or higher
- Supports Windows, macOS, and Linux systems



### Installation Steps

1. Clone the project locally

```bash
git clone https://github.com/yourusername/VerbaAurea.git
cd VerbaAurea
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

## User Guide

### Web Interface Usage (Recommended)

1. Start the web service

```bash
python web_service.py
```

Or double-click the `启动Web服务.bat` file on Windows systems

2. Open your browser and visit `http://localhost:18080`

3. Use the web interface for document processing:
   - **Upload Files**: Drag DOCX files to the upload area or click to select files
   - **Batch Processing**: Support uploading multiple files simultaneously
   - **File Management**: Preview uploaded files and remove unwanted files
   - **Start Processing**: Click "Start Processing" button to process all files
   - **Real-time Progress**: View processing progress and status
   - **Download Results**: Download ZIP package after processing completion

### Command Line Usage

1. Place Word documents that need processing in the script directory or subdirectories
2. Run the main script

```bash
python main.py
```

3. Select operations according to the menu:
   - Select `1` to start processing documents
   - Select `2` to view current configuration
   - Select `3` to edit configuration
   - Select `4` to exit the program

4. Processed documents will be saved in the `processed` (default) or custom output folder

### Configuration Instructions

You can customize segmentation parameters by editing through the menu or directly modifying the `config.json` file:

#### Document Settings

- `max_length`: Maximum paragraph length. Controls the maximum character count of each segmented text block. Too large may reduce retrieval efficiency, too small may disrupt semantic integrity.
- `min_length`: Minimum paragraph length. Prevents the generation of fragments that are too short. Text blocks that are too short may lack sufficient context, affecting knowledge base quality.
- `sentence_integrity_weight`: Sentence integrity weight. Higher values make the system more inclined to keep sentences complete, reducing the possibility of splitting in the middle of sentences.

#### Processing Options

- `debug_mode`: Debug mode. When enabled, outputs detailed processing information, including split point scoring and calculation processes. (This setting is currently mainly used for algorithm optimization research).
- `output_folder`: Output folder name. Processed documents will be saved in this folder, maintaining the original directory structure.
- `skip_existing`: Whether to skip existing files

#### Advanced Settings

- `min_split_score`: Minimum split score. Only positions with scores higher than this value will be selected as split points. Increasing this value can reduce the number of split points.
- `heading_score_bonus`: Title bonus value. Splitting before and after titles is usually more reasonable; this parameter controls the priority of title positions.
- `sentence_end_score_bonus`: Sentence ending bonus value. Increasing this value prioritizes splitting at sentence boundaries, improving document semantic integrity.
- `length_score_factor`: Length scoring factor. Controls the impact of paragraph length on scoring; larger values produce more uniform splits.
- `search_window`: Search window size. When adjusting split points to sentence boundaries, the system searches for the nearest sentence boundary within this window range.

#### Performance Settings

- `num_workers`: Number of worker processes. Setting to 0 will automatically use (CPU cores - 1) processes. Can be adjusted according to system resources.
- `cache_size`: Cache size. Used to store text analysis results to avoid repetitive calculations and improve processing speed. Unit is number of entries.
- `batch_size`: Batch size. The number of files processed by each worker process at once; larger values can reduce process switching overhead.

### Best Practices

- **Set reasonable length ranges** - Set appropriate maximum and minimum paragraph lengths based on knowledge base, fine-tuning, or application requirements
- **Adjust sentence integrity weight** - If sentences are being split, increase this weight

## How It Works

1. **Document Parsing** - Parse documents, extract text, style, and structural information
2. **Paragraph Analysis** - Analyze characteristics of each paragraph, such as length, whether it's a heading, whether it ends with a period, etc.
3. **Score Calculation** - Calculate comprehensive scores for each potential split point
4. **Split Point Selection** - Select optimal split points based on scores and configuration
5. **Sentence Boundary Correction** - Adjust split point positions to occur at sentence boundaries
6. **Split Marker Insertion** - Insert `<!--split-->` markers at selected positions
7. **Format Preservation** - Preserve the original document's formatting and save as a new document

## Web Interface Features

- **Modern Interface** - Responsive design supporting desktop and mobile devices
- **Drag & Drop Upload** - Support dragging files to upload area
- **Batch Processing** - Process multiple documents at once for improved efficiency
- **Real-time Progress** - Display processing progress and current file
- **File Management** - Preview and manage file list after upload
- **Configuration Adjustment** - Online adjustment of processing parameters
- **Result Download** - Unified packaging and download after processing completion

## Development Plan

- ✅ Web interface support
- ✅ Batch document processing
- ✅ Drag & drop upload functionality
- 🔄 Add support for more document formats
- 🔄 Enhance semantic analysis capabilities using more advanced NLP models
- 🔄 Add document preview functionality

## Frequently Asked Questions

**Q: Why are some paragraphs too short or too long after splitting?**

A: Try adjusting the `max_length` and `min_length` parameters in the configuration file to balance segmentation granularity.

**Q: How to avoid sentences being split in the middle?**

A: Increase the `sentence_integrity_weight` parameter value; the default value is 8.0, you can try setting it to 10.0 or higher.

**Q: How to handle documents with special formatting?**

A: For special formats, you can adapt to different document structures by adjusting the scoring parameters in the advanced settings.

## API Endpoints

Below are the main API endpoints. All return JSON (except the download endpoint):

- Health Check
  - Method: GET
  - Path: /api/health
  - Example:
    ```bash
    curl -s http://localhost:18080/api/health
    ```

- Get/Update Configuration
  - Method: GET / POST
  - Path: /api/config
  - Example (get config):
    ```bash
    curl -s http://localhost:18080/api/config
    ```
  - Example (update config):
    ```bash
    curl -s -X POST http://localhost:18080/api/config \
      -H "Content-Type: application/json" \
      -d '{"document_settings": {"max_length": 1200, "min_length": 200}}'
    ```

- Upload File (upload only, no immediate processing)
  - Method: POST (multipart/form-data)
  - Path: /api/upload
  - Params: file (required), session_id (optional, auto-created if omitted)
  - Returns: { success, session_id, file_id, original_filename, file_size, message }
  - Example:
    ```bash
    curl -s -F "file=@/path/to/file.docx" http://localhost:18080/api/upload
    ```

- Start Batch Processing
  - Method: POST (application/json)
  - Path: /api/batch/process
  - Body: { "session_id": "<SESSION_ID>" }
  - Returns: { success, session_id, processed_count, failed_count, download_url, message }
  - Example:
    ```bash
    curl -s -X POST http://localhost:18080/api/batch/process \
      -H "Content-Type: application/json" \
      -d '{"session_id": "<SESSION_ID>"}'
    ```

- Get Batch Status
  - Method: GET
  - Path: /api/batch/status/<session_id>
  - Returns: { status, progress, processed_count, total_count, current_file, files[], download_url }
  - Example:
    ```bash
    curl -s http://localhost:18080/api/batch/status/<SESSION_ID>
    ```

- Batch Result Download (ZIP)
  - Method: GET
  - Path: /api/batch/download/<session_id>
  - Returns: ZIP file (Content-Disposition attachment)
  - Example:
    ```bash
    curl -L -o result.zip http://localhost:18080/api/batch/download/<SESSION_ID>
    ```

- Remove File From Batch
  - Method: POST (application/json)
  - Path: /api/batch/remove-file
  - Body: { "session_id": "<SESSION_ID>", "file_id": "<FILE_ID>" }
  - Returns: { success, message }
  - Example:
    ```bash
    curl -s -X POST http://localhost:18080/api/batch/remove-file \
      -H "Content-Type: application/json" \
      -d '{"session_id": "<SESSION_ID>", "file_id": "<FILE_ID>"}'
    ```

- Single File Download (legacy compatibility)
  - Method: GET
  - Path: /api/download/<file_id>
  - Note: Kept only for legacy compatibility; the new flow uses batch download

## Contribution Guidelines

Contributions to the VerbaAurea project are welcome! You can participate in the following ways:

1. Report bugs or suggest features
2. Submit Pull Requests to improve the code
3. Improve documentation and usage examples
4. Share your experiences and cases using VerbaAurea

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=AEPAX/VerbaAurea&type=Date)](https://www.star-history.com/#AEPAX/VerbaAurea&Date)

This project is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).