# 📚 VerbaAurea 🌟

[中文](./README.md) | [English](./README_EN.md)

VerbaAurea is an intelligent document preprocessing tool dedicated to transforming raw documents into "golden" knowledge, providing high-quality text data for knowledge base construction. It focuses on intelligent document segmentation, ensuring semantic integrity, and delivers premium material for knowledge base retrieval and large language model fine-tuning.

## Project Features

- **Intelligent Document Segmentation** - Precise segmentation based on sentence boundaries and semantic integrity, currently supporting only docx and doc format documents
- **Multi-dimensional Scoring System** - Considers titles, sentence integrity, paragraph length, and other factors to determine optimal split points
- **Semantic Integrity Protection** - Prioritizes the completeness of sentences and semantic units, avoiding breaks in the middle of sentences
- **Configurable Design** - Flexibly adjust segmentation strategies through configuration files without modifying code
- **Multi-language Support** - Employs different sentence segmentation strategies for Chinese and English texts
- **Format Preservation** - Maintains the original document's formatting information, including styles, fonts, and tables

## Application Scenarios

- **Knowledge Base Construction** - Provides text units of appropriate granularity for retrieval-based question answering systems

- **Corpus Preparation** - Prepares high-quality training data for large language model fine-tuning

- **Document Indexing** - Optimizes index units for document retrieval systems

- **Content Management** - Improves document organization in content management systems

  
## Project Structure
```
├── main.py                 # Main program entry
├── config_manager.py       # Configuration management
├── document_processor.py   # Document processing core
├── text_analysis.py        # Text analysis functionality
├── parallel_processor.py   # Parallel processing implementation
├── utils.py                # Utility functions
├── config.json             # Auto-generated configuration file
├── requirements.txt        # Project dependencies
├── README.md               # Chinese documentation
├── README_EN.md            # English documentation
├── LICENSE                 # Open source license
└── Documents or document folders...
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
git clone https://github.com/AEPAX/VerbaAurea.git
cd VerbaAurea
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

## User Guide

### Basic Usage

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

4. Processed documents will be saved in the `文件输出` (default) or custom output folder

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

## Development Plan

- Add support for more document formats
- Implement a graphical user interface
- Enhance semantic analysis capabilities using more advanced NLP models

## 🧪 Testing

VerbaAurea provides a comprehensive test suite to ensure functionality reliability and stability.

### Test Structure

```
verba_aurea/tests/
├── api/                     # API tests
│   └── test_api_endpoints.py
├── functional/              # Functional tests
│   └── test_image_processing.py
├── unit/                    # Unit tests
└── integration/             # Integration tests
```

### Running Tests

#### Using Unified Test Runner (Recommended)

```bash
# Run all tests
python run_tests.py

# Run specific type of tests
python run_tests.py --type api          # API tests
python run_tests.py --type functional   # Functional tests
python run_tests.py --type unit         # Unit tests
python run_tests.py --type integration  # Integration tests

# Check test dependencies
python run_tests.py --check-deps
```

#### Running Tests Individually

```bash
# API tests (requires API service to be started first)
python start_api.py  # Start in another terminal
python verba_aurea/tests/api/test_api_endpoints.py

# Functional tests
python verba_aurea/tests/functional/test_image_processing.py

# Using pytest (requires pytest installation)
pytest verba_aurea/tests/unit/ -v
pytest verba_aurea/tests/integration/ -v
```

### Test Coverage

- **API Endpoint Tests** - Verify functionality and responses of all API endpoints
- **Image Processing Tests** - Verify image recognition, preservation, and quality maintenance
- **Document Analysis Tests** - Verify document structure analysis and element extraction
- **Configuration Management Tests** - Verify configuration loading, validation, and updates
- **Error Handling Tests** - Verify handling of various error conditions
- **Performance Tests** - Verify processing speed and resource usage

### Test Reports

After testing completion, detailed test reports are generated, including:
- Test pass rate
- Performance metrics
- Error details
- Improvement suggestions

View historical test reports: [docs/API_TEST_REPORT.md](./docs/API_TEST_REPORT.md)

## Frequently Asked Questions

**Q: Why are some paragraphs too short or too long after splitting?**

A: Try adjusting the `max_length` and `min_length` parameters in the configuration file to balance segmentation granularity.

**Q: How to avoid sentences being split in the middle?**

A: Increase the `sentence_integrity_weight` parameter value; the default value is 8.0, you can try setting it to 10.0 or higher.

**Q: How to handle documents with special formatting?**

A: For special formats, you can adapt to different document structures by adjusting the scoring parameters in the advanced settings.

## Contribution Guidelines

Contributions to the VerbaAurea project are welcome! You can participate in the following ways:

1. Report bugs or suggest features
2. Submit Pull Requests to improve the code
3. Improve documentation and usage examples
4. Share your experiences and cases using VerbaAurea

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=AEPAX/VerbaAurea&type=Date)](https://www.star-history.com/#AEPAX/VerbaAurea&Date)

This project is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
