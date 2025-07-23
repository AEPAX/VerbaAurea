#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
VerbaAurea API端点测试

测试所有API端点的功能和响应。
"""

import requests
import json
import os
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# API基础URL
API_BASE_URL = "http://localhost:8001/api/v1"


class APITestSuite:
    """API测试套件"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        """初始化测试套件"""
        self.base_url = base_url
        self.test_results = []
    
    def log_result(self, test_name: str, success: bool, message: str = ""):
        """记录测试结果"""
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message
        })
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}: {message}")
    
    def test_health_check(self):
        """测试健康检查端点"""
        print("\n=== 测试健康检查端点 ===")
        
        try:
            response = requests.get(f"{self.base_url}/health")
            
            if response.status_code == 200:
                data = response.json()
                status = data['data']['status']
                version = data['data']['version']
                uptime = data['data']['uptime']
                dependencies = data['data']['dependencies']
                
                self.log_result(
                    "健康检查端点", 
                    True, 
                    f"状态: {status}, 版本: {version}, 运行时间: {uptime}s"
                )
                
                # 检查依赖状态
                all_deps_ok = all(dependencies.values())
                self.log_result(
                    "依赖检查", 
                    all_deps_ok, 
                    f"依赖状态: {dependencies}"
                )
            else:
                self.log_result(
                    "健康检查端点", 
                    False, 
                    f"状态码: {response.status_code}, 响应: {response.text}"
                )
        
        except Exception as e:
            self.log_result("健康检查端点", False, f"异常: {str(e)}")
    
    def test_document_processing(self):
        """测试文档处理端点"""
        print("\n=== 测试文档处理端点 ===")
        
        # 查找测试文档
        test_files = [
            "测试/15698J24 HZ25-8 Evidence of Cover.docx",
            "企业库/中国石化：2022年年度报告.docx"
        ]
        
        test_file = None
        for file_path in test_files:
            if os.path.exists(file_path):
                test_file = file_path
                break
        
        if not test_file:
            self.log_result("文档处理端点", False, "未找到测试文档")
            return
        
        try:
            with open(test_file, 'rb') as f:
                files = {'file': f}
                data = {'debug_mode': True}
                
                response = requests.post(
                    f"{self.base_url}/process-document",
                    files=files,
                    data=data
                )
            
            if response.status_code == 200:
                result = response.json()
                split_count = result['data']['split_count']
                processing_time = result['data']['processing_time']
                
                self.log_result(
                    "文档处理端点", 
                    True, 
                    f"分割符: {split_count}, 处理时间: {processing_time}s"
                )
            else:
                self.log_result(
                    "文档处理端点", 
                    False, 
                    f"状态码: {response.status_code}, 响应: {response.text}"
                )
        
        except Exception as e:
            self.log_result("文档处理端点", False, f"异常: {str(e)}")
    
    def test_document_download(self):
        """测试文档下载端点"""
        print("\n=== 测试文档下载端点 ===")
        
        # 查找测试文档
        test_files = [
            "测试/15698J24 HZ25-8 Evidence of Cover.docx",
            "企业库/中国石化：2022年年度报告.docx"
        ]
        
        test_file = None
        for file_path in test_files:
            if os.path.exists(file_path):
                test_file = file_path
                break
        
        if not test_file:
            self.log_result("文档下载端点", False, "未找到测试文档")
            return
        
        try:
            with open(test_file, 'rb') as f:
                files = {'file': f}
                data = {'debug_mode': False}
                
                response = requests.post(
                    f"{self.base_url}/process-document/download",
                    files=files,
                    data=data
                )
            
            if response.status_code == 200:
                # 保存下载的文件
                output_file = "test_output.docx"
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                
                file_size = len(response.content)
                self.log_result(
                    "文档下载端点", 
                    True, 
                    f"文件大小: {file_size} 字节"
                )
                
                # 清理测试文件
                try:
                    os.remove(output_file)
                except:
                    pass
            else:
                self.log_result(
                    "文档下载端点", 
                    False, 
                    f"状态码: {response.status_code}"
                )
        
        except Exception as e:
            self.log_result("文档下载端点", False, f"异常: {str(e)}")
    
    def test_config_endpoints(self):
        """测试配置管理端点"""
        print("\n=== 测试配置管理端点 ===")
        
        try:
            # 获取当前配置
            response = requests.get(f"{self.base_url}/config")
            
            if response.status_code == 200:
                config_data = response.json()
                config_count = len(config_data['data'])
                self.log_result(
                    "配置获取端点", 
                    True, 
                    f"配置项数量: {config_count}"
                )
            else:
                self.log_result(
                    "配置获取端点", 
                    False, 
                    f"状态码: {response.status_code}"
                )
            
            # 测试配置验证
            response = requests.get(f"{self.base_url}/config/validate")
            
            if response.status_code == 200:
                validation_result = response.json()
                is_valid = validation_result['data']['valid']
                self.log_result(
                    "配置验证端点", 
                    True, 
                    f"配置有效性: {is_valid}"
                )
            else:
                self.log_result(
                    "配置验证端点", 
                    False, 
                    f"状态码: {response.status_code}"
                )
        
        except Exception as e:
            self.log_result("配置管理端点", False, f"异常: {str(e)}")
    
    def test_error_handling(self):
        """测试错误处理"""
        print("\n=== 测试错误处理 ===")
        
        try:
            # 测试上传非支持格式文件
            test_content = b"This is not a docx file"
            files = {'file': ('test.txt', test_content, 'text/plain')}
            
            response = requests.post(
                f"{self.base_url}/process-document",
                files=files
            )
            
            if response.status_code == 400:
                error_data = response.json()
                error_message = error_data['message']
                self.log_result(
                    "错误处理", 
                    True, 
                    f"正确返回400错误: {error_message}"
                )
            else:
                self.log_result(
                    "错误处理", 
                    False, 
                    f"未正确处理错误，状态码: {response.status_code}"
                )
        
        except Exception as e:
            self.log_result("错误处理", False, f"异常: {str(e)}")
    
    def test_api_documentation(self):
        """测试API文档端点"""
        print("\n=== 测试API文档端点 ===")
        
        try:
            # 测试OpenAPI JSON
            response = requests.get(f"{self.base_url.replace('/api/v1', '')}/openapi.json")
            
            if response.status_code == 200:
                openapi_data = response.json()
                api_title = openapi_data.get('info', {}).get('title', 'N/A')
                api_version = openapi_data.get('info', {}).get('version', 'N/A')
                endpoints_count = len(openapi_data.get('paths', {}))
                
                self.log_result(
                    "OpenAPI文档", 
                    True, 
                    f"标题: {api_title}, 版本: {api_version}, 端点数: {endpoints_count}"
                )
            else:
                self.log_result(
                    "OpenAPI文档", 
                    False, 
                    f"状态码: {response.status_code}"
                )
            
            # 测试Swagger UI
            response = requests.get(f"{self.base_url.replace('/api/v1', '')}/docs")
            
            if response.status_code == 200:
                self.log_result("Swagger UI", True, "可访问")
            else:
                self.log_result("Swagger UI", False, f"状态码: {response.status_code}")
        
        except Exception as e:
            self.log_result("API文档端点", False, f"异常: {str(e)}")
    
    def test_metrics_endpoint(self):
        """测试性能指标端点"""
        print("\n=== 测试性能指标端点 ===")
        
        try:
            response = requests.get(f"{self.base_url}/health/metrics")
            
            if response.status_code == 200:
                metrics_data = response.json()
                self.log_result(
                    "性能指标端点", 
                    True, 
                    f"指标数据: {len(metrics_data['data'])} 项"
                )
            else:
                self.log_result(
                    "性能指标端点", 
                    False, 
                    f"状态码: {response.status_code}"
                )
        
        except Exception as e:
            self.log_result("性能指标端点", False, f"异常: {str(e)}")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 VerbaAurea API 功能测试")
        print("=" * 50)
        
        # 运行所有测试
        self.test_health_check()
        self.test_document_processing()
        self.test_document_download()
        self.test_config_endpoints()
        self.test_error_handling()
        self.test_api_documentation()
        self.test_metrics_endpoint()
        
        # 输出测试总结
        self.print_summary()
    
    def print_summary(self):
        """打印测试总结"""
        print("\n" + "=" * 50)
        print("📊 测试结果总结")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests}")
        print(f"失败: {failed_tests}")
        print(f"成功率: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ 失败的测试:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['message']}")
        else:
            print("\n🎉 所有测试通过！")


def main():
    """主函数"""
    test_suite = APITestSuite()
    test_suite.run_all_tests()


if __name__ == "__main__":
    main()
