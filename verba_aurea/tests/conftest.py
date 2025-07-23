#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
pytest配置文件

为所有测试提供共享的fixtures和配置。
"""

import pytest
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def project_root_path():
    """项目根目录路径"""
    return project_root


@pytest.fixture(scope="session")
def test_data_dir():
    """测试数据目录"""
    return project_root / "test_data"


@pytest.fixture(scope="session")
def temp_dir():
    """临时目录"""
    temp_path = project_root / "temp"
    temp_path.mkdir(exist_ok=True)
    return temp_path


@pytest.fixture
def sample_config():
    """示例配置"""
    return {
        "document_settings": {
            "max_length": 1000,
            "min_length": 300,
            "sentence_integrity_weight": 8.0,
            "table_length_factor": 1.2,
            "image_length_factor": 100,
            "preserve_images": True
        },
        "processing_options": {
            "debug_mode": False,
            "output_folder": "输出文件夹",
            "skip_existing": True
        },
        "advanced_settings": {
            "min_split_score": 7,
            "heading_score_bonus": 10,
            "sentence_end_score_bonus": 6,
            "length_score_factor": 100,
            "search_window": 5,
            "heading_after_penalty": 12,
            "force_split_before_heading": True,
            "custom_heading_regex": []
        },
        "performance_settings": {
            "parallel_processing": True,
            "num_workers": 0,
            "cache_size": 1024,
            "batch_size": 50
        },
        "input_folder": "."
    }


@pytest.fixture
def api_base_url():
    """API基础URL"""
    return "http://localhost:8001/api/v1"


# 测试标记
def pytest_configure(config):
    """配置pytest标记"""
    config.addinivalue_line(
        "markers", "api: marks tests as API tests"
    )
    config.addinivalue_line(
        "markers", "functional: marks tests as functional tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )
