#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
VerbaAurea 测试运行器

统一的测试运行脚本，支持运行不同类型的测试。
"""

import sys
import os
import argparse
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))


def run_api_tests():
    """运行API测试"""
    print("🌐 运行API测试...")
    try:
        from verba_aurea.tests.api.test_api_endpoints import APITestSuite
        test_suite = APITestSuite()
        test_suite.run_all_tests()
        return True
    except Exception as e:
        print(f"❌ API测试运行失败: {e}")
        return False


def run_functional_tests():
    """运行功能测试"""
    print("🖼️ 运行功能测试...")
    try:
        from verba_aurea.tests.functional.test_image_processing import ImageProcessingTestSuite
        test_suite = ImageProcessingTestSuite()
        test_suite.run_all_tests()
        return True
    except Exception as e:
        print(f"❌ 功能测试运行失败: {e}")
        return False


def run_unit_tests():
    """运行单元测试"""
    print("🔧 运行单元测试...")
    try:
        # 检查是否安装了pytest
        import pytest
        
        # 运行单元测试
        test_dir = Path(__file__).parent / "verba_aurea" / "tests" / "unit"
        if test_dir.exists():
            exit_code = pytest.main([str(test_dir), "-v"])
            return exit_code == 0
        else:
            print("⚠️ 单元测试目录不存在，跳过单元测试")
            return True
    except ImportError:
        print("⚠️ pytest未安装，跳过单元测试")
        print("提示: 运行 'pip install pytest' 安装pytest")
        return True
    except Exception as e:
        print(f"❌ 单元测试运行失败: {e}")
        return False


def run_integration_tests():
    """运行集成测试"""
    print("🔗 运行集成测试...")
    try:
        # 检查是否安装了pytest
        import pytest
        
        # 运行集成测试
        test_dir = Path(__file__).parent / "verba_aurea" / "tests" / "integration"
        if test_dir.exists():
            exit_code = pytest.main([str(test_dir), "-v"])
            return exit_code == 0
        else:
            print("⚠️ 集成测试目录不存在，跳过集成测试")
            return True
    except ImportError:
        print("⚠️ pytest未安装，跳过集成测试")
        return True
    except Exception as e:
        print(f"❌ 集成测试运行失败: {e}")
        return False


def check_test_dependencies():
    """检查测试依赖"""
    print("🔍 检查测试依赖...")
    
    dependencies = {
        'requests': '用于API测试',
        'docx': '用于文档处理测试',
        'jieba': '用于中文文本分析',
        'nltk': '用于英文文本分析'
    }
    
    missing_deps = []
    
    for dep, description in dependencies.items():
        try:
            if dep == 'docx':
                import docx
            else:
                __import__(dep)
            print(f"✅ {dep}: 已安装")
        except ImportError:
            print(f"❌ {dep}: 未安装 ({description})")
            missing_deps.append(dep)
    
    if missing_deps:
        print(f"\n⚠️ 缺少依赖: {', '.join(missing_deps)}")
        print("请运行以下命令安装:")
        if 'docx' in missing_deps:
            missing_deps[missing_deps.index('docx')] = 'python-docx'
        print(f"pip install {' '.join(missing_deps)}")
        return False
    
    print("✅ 所有测试依赖已安装")
    return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="VerbaAurea 测试运行器")
    parser.add_argument(
        '--type', 
        choices=['all', 'api', 'functional', 'unit', 'integration'],
        default='all',
        help='要运行的测试类型'
    )
    parser.add_argument(
        '--check-deps',
        action='store_true',
        help='仅检查测试依赖'
    )
    
    args = parser.parse_args()
    
    print("🧪 VerbaAurea 测试运行器")
    print("=" * 50)
    
    # 检查依赖
    if not check_test_dependencies():
        if not args.check_deps:
            print("\n❌ 依赖检查失败，无法运行测试")
            sys.exit(1)
        else:
            sys.exit(1)
    
    if args.check_deps:
        print("\n✅ 依赖检查完成")
        return
    
    print("\n🚀 开始运行测试...")
    
    test_results = []
    
    if args.type in ['all', 'api']:
        test_results.append(('API测试', run_api_tests()))
    
    if args.type in ['all', 'functional']:
        test_results.append(('功能测试', run_functional_tests()))
    
    if args.type in ['all', 'unit']:
        test_results.append(('单元测试', run_unit_tests()))
    
    if args.type in ['all', 'integration']:
        test_results.append(('集成测试', run_integration_tests()))
    
    # 输出总结
    print("\n" + "=" * 50)
    print("📊 测试结果总结")
    print("=" * 50)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for _, result in test_results if result)
    failed_tests = total_tests - passed_tests
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n总测试套件: {total_tests}")
    print(f"通过: {passed_tests}")
    print(f"失败: {failed_tests}")
    
    if failed_tests == 0:
        print("\n🎉 所有测试通过！")
        sys.exit(0)
    else:
        print(f"\n⚠️ {failed_tests} 个测试套件失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
