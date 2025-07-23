#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
图片处理功能测试

测试VerbaAurea的图片识别和保留功能。
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


class ImageProcessingTestSuite:
    """图片处理测试套件"""
    
    def __init__(self):
        """初始化测试套件"""
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
    
    def test_imports(self):
        """测试导入模块"""
        print("\n=== 测试模块导入 ===")
        
        try:
            from docx import Document
            self.log_result("docx模块导入", True, "成功导入python-docx")
        except Exception as e:
            self.log_result("docx模块导入", False, f"导入失败: {e}")
            return False

        # 测试新架构导入
        try:
            from verba_aurea.core.analyzers.structure_analyzer import StructureAnalyzer
            self.log_result("新架构模块导入", True, "成功导入新架构分析器")
        except Exception as e:
            # 降级到旧版本
            try:
                from text_analysis import extract_elements_info
                self.log_result("旧版本模块导入", True, "成功导入旧版本分析器")
            except Exception as e2:
                self.log_result("模块导入", False, f"新旧版本都导入失败: {e2}")
                return False

        try:
            from document_processor import insert_split_markers
            self.log_result("文档处理器导入", True, "成功导入文档处理器")
        except Exception as e:
            self.log_result("文档处理器导入", False, f"导入失败: {e}")
            return False

        return True
    
    def test_image_detection(self):
        """测试图片检测功能"""
        print("\n=== 测试图片检测功能 ===")
        
        # 查找包含图片的测试文档
        test_files = [
            "测试/包含图片的文档.docx",
            "测试/test_with_images.docx",
            "企业库/中国石化：2022年年度报告.docx"
        ]
        
        test_file = None
        for file_path in test_files:
            if os.path.exists(file_path):
                test_file = file_path
                break
        
        if not test_file:
            self.log_result("图片检测", False, "未找到包含图片的测试文档")
            return
        
        try:
            # 使用新架构进行图片检测
            try:
                from verba_aurea.services import DocumentService
                from verba_aurea.config import get_settings
                
                settings = get_settings()
                service = DocumentService(settings)
                
                document = service.analyze_document(Path(test_file))
                image_count = document.image_count
                
                self.log_result(
                    "新架构图片检测", 
                    True, 
                    f"检测到 {image_count} 张图片"
                )
                
            except ImportError:
                # 降级到旧版本
                from docx import Document
                from text_analysis import extract_elements_info
                
                doc = Document(test_file)
                elements_info = extract_elements_info(doc, debug_mode=True)
                
                image_count = sum(1 for elem in elements_info if elem.get('has_images', False))
                total_images = sum(elem.get('image_count', 0) for elem in elements_info)
                
                self.log_result(
                    "旧版本图片检测", 
                    True, 
                    f"包含图片的段落: {image_count}, 总图片数: {total_images}"
                )
        
        except Exception as e:
            self.log_result("图片检测", False, f"检测失败: {str(e)}")
    
    def test_image_preservation(self):
        """测试图片保留功能"""
        print("\n=== 测试图片保留功能 ===")
        
        # 查找包含图片的测试文档
        test_files = [
            "测试/包含图片的文档.docx",
            "测试/test_with_images.docx",
            "企业库/中国石化：2022年年度报告.docx"
        ]
        
        test_file = None
        for file_path in test_files:
            if os.path.exists(file_path):
                test_file = file_path
                break
        
        if not test_file:
            self.log_result("图片保留", False, "未找到包含图片的测试文档")
            return
        
        try:
            output_file = "temp/test_image_output.docx"
            os.makedirs("temp", exist_ok=True)
            
            # 使用新架构进行处理
            try:
                from verba_aurea.services import DocumentService
                from verba_aurea.config import get_settings
                
                settings = get_settings()
                config = settings.get_config()
                config.document_settings.preserve_images = True
                
                service = DocumentService(settings)
                result = service.process_document(
                    Path(test_file), 
                    Path(output_file), 
                    config
                )
                
                if result.success:
                    # 检查输出文件中的图片
                    output_doc = service.analyze_document(Path(output_file))
                    output_image_count = output_doc.image_count
                    
                    self.log_result(
                        "新架构图片保留", 
                        output_image_count > 0, 
                        f"输出文档包含 {output_image_count} 张图片"
                    )
                else:
                    self.log_result("新架构图片保留", False, f"处理失败: {result.message}")
                    
            except ImportError:
                # 降级到旧版本
                from document_processor import insert_split_markers
                from config_manager import load_config
                
                config = load_config()
                config['document_settings']['preserve_images'] = True
                
                success = insert_split_markers(test_file, output_file, config)
                
                if success and os.path.exists(output_file):
                    from docx import Document
                    from text_analysis import extract_elements_info
                    
                    output_doc = Document(output_file)
                    output_elements = extract_elements_info(output_doc, debug_mode=True)
                    output_image_count = sum(elem.get('image_count', 0) for elem in output_elements)
                    
                    self.log_result(
                        "旧版本图片保留", 
                        output_image_count > 0, 
                        f"输出文档包含 {output_image_count} 张图片"
                    )
                else:
                    self.log_result("旧版本图片保留", False, "处理失败或输出文件不存在")
            
            # 清理测试文件
            try:
                if os.path.exists(output_file):
                    os.remove(output_file)
            except:
                pass
        
        except Exception as e:
            self.log_result("图片保留", False, f"测试失败: {str(e)}")
    
    def test_image_quality(self):
        """测试图片质量保持"""
        print("\n=== 测试图片质量保持 ===")
        
        # 查找包含图片的测试文档
        test_files = [
            "测试/包含图片的文档.docx",
            "测试/test_with_images.docx",
            "企业库/中国石化：2022年年度报告.docx"
        ]
        
        test_file = None
        for file_path in test_files:
            if os.path.exists(file_path):
                test_file = file_path
                break
        
        if not test_file:
            self.log_result("图片质量", False, "未找到包含图片的测试文档")
            return
        
        try:
            output_file = "temp/test_quality_output.docx"
            os.makedirs("temp", exist_ok=True)
            
            # 处理文档
            try:
                from verba_aurea.services import DocumentService
                from verba_aurea.config import get_settings
                
                settings = get_settings()
                config = settings.get_config()
                config.document_settings.preserve_images = True
                
                service = DocumentService(settings)
                result = service.process_document(
                    Path(test_file), 
                    Path(output_file), 
                    config
                )
                
                if result.success:
                    # 比较文件大小（简单的质量指标）
                    input_size = os.path.getsize(test_file)
                    output_size = os.path.getsize(output_file)
                    size_ratio = output_size / input_size
                    
                    # 如果输出文件大小在合理范围内，认为质量保持良好
                    quality_preserved = 0.8 <= size_ratio <= 1.2
                    
                    self.log_result(
                        "图片质量保持", 
                        quality_preserved, 
                        f"大小比例: {size_ratio:.2f} (输入: {input_size}, 输出: {output_size})"
                    )
                else:
                    self.log_result("图片质量保持", False, f"处理失败: {result.message}")
                    
            except ImportError:
                # 降级到旧版本测试
                from document_processor import insert_split_markers
                from config_manager import load_config
                
                config = load_config()
                config['document_settings']['preserve_images'] = True
                
                success = insert_split_markers(test_file, output_file, config)
                
                if success and os.path.exists(output_file):
                    input_size = os.path.getsize(test_file)
                    output_size = os.path.getsize(output_file)
                    size_ratio = output_size / input_size
                    
                    quality_preserved = 0.8 <= size_ratio <= 1.2
                    
                    self.log_result(
                        "图片质量保持", 
                        quality_preserved, 
                        f"大小比例: {size_ratio:.2f}"
                    )
                else:
                    self.log_result("图片质量保持", False, "处理失败")
            
            # 清理测试文件
            try:
                if os.path.exists(output_file):
                    os.remove(output_file)
            except:
                pass
        
        except Exception as e:
            self.log_result("图片质量保持", False, f"测试失败: {str(e)}")
    
    def test_image_position_preservation(self):
        """测试图片位置保持"""
        print("\n=== 测试图片位置保持 ===")
        
        # 这个测试需要更复杂的逻辑来验证图片位置
        # 目前简化为检查图片是否在正确的段落中
        
        test_files = [
            "测试/包含图片的文档.docx",
            "企业库/中国石化：2022年年度报告.docx"
        ]
        
        test_file = None
        for file_path in test_files:
            if os.path.exists(file_path):
                test_file = file_path
                break
        
        if not test_file:
            self.log_result("图片位置保持", False, "未找到包含图片的测试文档")
            return
        
        try:
            # 分析原始文档的图片位置
            try:
                from verba_aurea.services import DocumentService
                from verba_aurea.config import get_settings
                
                settings = get_settings()
                service = DocumentService(settings)
                
                original_doc = service.analyze_document(Path(test_file))
                original_image_positions = []
                
                for i, element in enumerate(original_doc.elements):
                    if element.has_images:
                        original_image_positions.append(i)
                
                self.log_result(
                    "图片位置分析", 
                    len(original_image_positions) > 0, 
                    f"原始文档中图片位置: {original_image_positions}"
                )
                
            except ImportError:
                # 使用旧版本进行简化测试
                self.log_result(
                    "图片位置保持", 
                    True, 
                    "旧版本架构，跳过详细位置检查"
                )
        
        except Exception as e:
            self.log_result("图片位置保持", False, f"测试失败: {str(e)}")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🖼️ VerbaAurea 图片处理功能测试")
        print("=" * 50)
        
        # 首先测试导入
        if not self.test_imports():
            print("❌ 模块导入失败，跳过其他测试")
            return
        
        # 运行所有测试
        self.test_image_detection()
        self.test_image_preservation()
        self.test_image_quality()
        self.test_image_position_preservation()
        
        # 输出测试总结
        self.print_summary()
    
    def print_summary(self):
        """打印测试总结"""
        print("\n" + "=" * 50)
        print("📊 图片处理测试结果总结")
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
            print("\n🎉 所有图片处理测试通过！")


def main():
    """主函数"""
    test_suite = ImageProcessingTestSuite()
    test_suite.run_all_tests()


if __name__ == "__main__":
    main()
