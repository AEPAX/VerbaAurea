#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
图片处理功能测试脚本
测试VerbaAurea的图片识别和保留功能
"""

import os
import sys

def test_imports():
    """测试导入模块"""
    print("测试导入模块...")
    try:
        from docx import Document
        print("✓ docx 导入成功")
    except Exception as e:
        print(f"✗ docx 导入失败: {e}")
        return False

    try:
        from text_analysis import extract_elements_info
        print("✓ text_analysis 导入成功")
    except Exception as e:
        print(f"✗ text_analysis 导入失败: {e}")
        return False

    try:
        from document_processor import insert_split_markers
        print("✓ document_processor 导入成功")
    except Exception as e:
        print(f"✗ document_processor 导入失败: {e}")
        return False

    try:
        from config_manager import load_config
        print("✓ config_manager 导入成功")
    except Exception as e:
        print(f"✗ config_manager 导入失败: {e}")
        return False

    return True

# 删除这些函数，在main中直接实现简化版本


def main():
    """主测试函数"""
    print("VerbaAurea 图片处理功能测试")
    print("=" * 50)

    # 首先测试导入
    if not test_imports():
        print("导入测试失败，退出")
        return False

    print("\n所有模块导入成功！")

    # 如果导入成功，继续其他测试
    try:
        from docx import Document
        from text_analysis import extract_elements_info
        from document_processor import insert_split_markers
        from config_manager import load_config

        # 简单的功能测试
        print("\n=== 基础功能测试 ===")

        # 测试配置加载
        try:
            config = load_config()
            print("✓ 配置加载成功")
            print(f"  图片保留设置: {config.get('document_settings', {}).get('preserve_images', True)}")
            print(f"  图片长度因子: {config.get('document_settings', {}).get('image_length_factor', 100)}")
        except Exception as e:
            print(f"✗ 配置加载失败: {e}")
            return False

        # 查找测试文档
        test_files = []
        for root, dirs, files in os.walk("."):
            for file in files:
                if file.endswith(('.docx', '.doc')) and not file.startswith('~$'):
                    test_files.append(os.path.join(root, file))

        print(f"\n找到 {len(test_files)} 个文档文件")

        if test_files:
            # 测试第一个文档
            test_file = test_files[0]
            print(f"测试文档: {test_file}")

            try:
                doc = Document(test_file)
                elements_info = extract_elements_info(doc, debug_mode=True)

                total_elements = len(elements_info)
                elements_with_images = sum(1 for elem in elements_info if elem.get('has_images', False))
                total_images = sum(elem.get('image_count', 0) for elem in elements_info)

                print(f"✓ 文档分析成功")
                print(f"  总元素数: {total_elements}")
                print(f"  包含图片的元素: {elements_with_images}")
                print(f"  图片总数: {total_images}")

            except Exception as e:
                print(f"✗ 文档分析失败: {e}")
                return False
        else:
            print("未找到测试文档")

        # 如果找到了包含图片的文档，进行完整的处理测试
        if test_files and total_images > 0:
            print("\n=== 完整图片处理测试 ===")

            # 选择包含图片的文档进行测试
            input_file = test_file
            output_file = "test_output_with_images.docx"

            print(f"输入文档: {input_file}")
            print(f"输出文档: {output_file}")
            print(f"原文档包含 {total_images} 个图片")

            try:
                # 确保图片处理功能开启
                config["document_settings"]["preserve_images"] = True
                config["processing_options"]["debug_mode"] = True

                # 执行处理
                result = insert_split_markers(input_file, output_file, config)

                if result:
                    print("✓ 图片处理成功完成")

                    # 验证输出文档
                    if os.path.exists(output_file):
                        print(f"✓ 输出文档已创建: {output_file}")

                        # 检查输出文档中的图片
                        try:
                            output_doc = Document(output_file)
                            output_elements = extract_elements_info(output_doc, debug_mode=False)
                            output_images = sum(elem.get('image_count', 0) for elem in output_elements)
                            print(f"✓ 输出文档包含 {output_images} 个图片")

                            if output_images == total_images:
                                print("🎉 图片完全保留！")
                            elif output_images > 0:
                                print(f"⚠ 部分图片保留 ({output_images}/{total_images})")
                            else:
                                print("⚠ 图片未保留")

                        except Exception as e:
                            print(f"⚠ 验证输出文档时出错: {str(e)}")
                    else:
                        print("✗ 输出文档未创建")
                        return False
                else:
                    print("✗ 图片处理失败")
                    return False

            except Exception as e:
                print(f"✗ 处理过程中出错: {str(e)}")
                import traceback
                traceback.print_exc()
                return False

        print("\n🎉 所有测试完成！")
        return True

    except Exception as e:
        print(f"\n✗ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    main()
