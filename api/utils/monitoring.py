#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
监控和指标工具
"""

import time
import psutil
from typing import Dict, Any
from collections import defaultdict, deque


class MetricsCollector:
    """指标收集器"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.request_times = deque(maxlen=max_history)
        self.request_counts = defaultdict(int)
        self.error_counts = defaultdict(int)
        self.file_sizes = deque(maxlen=max_history)
        self.processing_times = deque(maxlen=max_history)
        self.start_time = time.time()
    
    def record_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """记录请求指标"""
        self.request_times.append(duration)
        self.request_counts[f"{method}_{endpoint}"] += 1
        
        if status_code >= 400:
            self.error_counts[f"{status_code}"] += 1
    
    def record_file_processing(self, file_size: int, processing_time: float):
        """记录文件处理指标"""
        self.file_sizes.append(file_size)
        self.processing_times.append(processing_time)
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取当前指标"""
        current_time = time.time()
        uptime = current_time - self.start_time
        
        # 计算请求统计
        total_requests = sum(self.request_counts.values())
        avg_request_time = sum(self.request_times) / len(self.request_times) if self.request_times else 0
        
        # 计算错误率
        total_errors = sum(self.error_counts.values())
        error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0
        
        # 计算文件处理统计
        avg_file_size = sum(self.file_sizes) / len(self.file_sizes) if self.file_sizes else 0
        avg_processing_time = sum(self.processing_times) / len(self.processing_times) if self.processing_times else 0
        
        # 系统资源使用情况
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "uptime": round(uptime, 2),
            "requests": {
                "total": total_requests,
                "average_time": round(avg_request_time, 4),
                "error_rate": round(error_rate, 2),
                "by_endpoint": dict(self.request_counts),
                "errors_by_code": dict(self.error_counts)
            },
            "file_processing": {
                "total_files": len(self.file_sizes),
                "average_file_size": round(avg_file_size, 2),
                "average_processing_time": round(avg_processing_time, 4)
            },
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available": memory.available,
                "disk_percent": disk.percent,
                "disk_free": disk.free
            }
        }
    
    def reset_metrics(self):
        """重置指标"""
        self.request_times.clear()
        self.request_counts.clear()
        self.error_counts.clear()
        self.file_sizes.clear()
        self.processing_times.clear()
        self.start_time = time.time()


# 全局指标收集器实例
metrics_collector = MetricsCollector()


def get_metrics_collector() -> MetricsCollector:
    """获取指标收集器实例"""
    return metrics_collector
