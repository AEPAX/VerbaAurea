#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
VerbaAurea CLI主程序

使用新架构的命令行接口实现。
"""

import os
import sys
import time
from pathlib import Path
from typing import List, Dict, Any

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from verba_aurea.services.document_service import DocumentService
from verba_aurea.services.processing_service import ProcessingService
from verba_aurea.config.settings import get_settings
from verba_aurea.config.manager import ConfigManager


class VerbaAureaCLI:
    """VerbaAurea命令行接口"""
    
    def __init__(self):
        """初始化CLI"""
        self.settings = get_settings()
        self.config_manager = ConfigManager(self.settings)
        self.document_service = DocumentService(self.settings)
        self.processing_service = ProcessingService(self.settings)
    
    def display_logo(self):
        """显示Logo"""
        logo = """
========================================================
                    VerbaAurea
                智能文档预处理工具 v2.0
              将文档转化为"黄金"般的知识
========================================================
        """
        print(logo)
    
    def display_menu(self):
        """显示主菜单"""
        menu = """
=========================================
                主菜单
=========================================
  1. 开始处理文档
  2. 查看/修改配置
  3. 查看处理统计
  4. 退出程序
=========================================
        """
        print(menu)
    
    def process_documents(self):
        """处理文档"""
        print("\n🔄 开始文档处理任务...")
        
        config = self.settings.get_config()
        input_dir = Path(config.input_folder)
        
        if not input_dir.exists():
            print(f"❌ 输入目录不存在: {input_dir}")
            return
        
        # 显示进度的回调函数
        def progress_callback(completed: int, total: int):
            percentage = (completed / total) * 100 if total > 0 else 0
            print(f"\r进度: {completed}/{total} ({percentage:.1f}%)", end="", flush=True)
        
        start_time = time.time()
        
        # 处理目录
        result = self.processing_service.process_directory_with_progress(
            input_dir, config, progress_callback
        )
        
        print()  # 换行
        
        # 显示结果
        summary = result['summary']
        elapsed_time = time.time() - start_time
        
        print(f"\n✅ 处理完成!")
        print(f"📊 处理统计:")
        print(f"   总文件数: {summary['total_files']}")
        print(f"   成功处理: {summary['processed_files']}")
        print(f"   处理失败: {summary['failed_files']}")
        print(f"   处理时间: {elapsed_time:.2f}秒")
        print(f"   处理速度: {summary['files_per_second']:.2f}文件/秒")
        
        if summary['failed_files'] > 0:
            print(f"\n❌ 失败的文件:")
            for file_path, result in result['results'].items():
                if not result.success:
                    print(f"   {file_path}: {result.message}")
    
    def show_config(self):
        """显示配置"""
        config = self.settings.get_config()
        summary = self.config_manager.get_config_summary()
        
        print("\n⚙️ 当前配置:")
        print(f"📁 配置文件: {summary['config_file']}")
        print(f"📄 文档设置:")
        print(f"   长度范围: {summary['document_settings']['length_range']}")
        print(f"   保留图片: {summary['document_settings']['preserve_images']}")
        print(f"   表格因子: {summary['document_settings']['table_factor']}")
        print(f"🔧 处理选项:")
        print(f"   调试模式: {summary['processing_options']['debug_mode']}")
        print(f"   输出目录: {summary['processing_options']['output_folder']}")
        print(f"   跳过已存在: {summary['processing_options']['skip_existing']}")
        print(f"⚡ 性能设置:")
        print(f"   并行处理: {summary['performance']['parallel_processing']}")
        print(f"   工作进程: {summary['performance']['num_workers']}")
        print(f"   批处理大小: {summary['performance']['batch_size']}")
    
    def modify_config(self):
        """修改配置"""
        print("\n🔧 配置修改功能")
        print("注意: 这是简化版配置修改，完整功能请编辑配置文件")
        
        config = self.settings.get_config()
        
        # 简单的配置修改选项
        print("\n可修改的选项:")
        print("1. 调试模式")
        print("2. 输出目录")
        print("3. 并行处理")
        print("4. 返回主菜单")
        
        choice = input("\n请选择要修改的选项 (1-4): ").strip()
        
        if choice == '1':
            current = config.processing_options.debug_mode
            new_value = not current
            self.settings.update_config(
                processing_options={'debug_mode': new_value}
            )
            print(f"✅ 调试模式已设置为: {new_value}")
        
        elif choice == '2':
            current = config.processing_options.output_folder
            new_value = input(f"当前输出目录: {current}\n请输入新的输出目录: ").strip()
            if new_value:
                self.settings.update_config(
                    processing_options={'output_folder': new_value}
                )
                print(f"✅ 输出目录已设置为: {new_value}")
        
        elif choice == '3':
            current = config.performance_settings.parallel_processing
            new_value = not current
            self.settings.update_config(
                performance_settings={'parallel_processing': new_value}
            )
            print(f"✅ 并行处理已设置为: {new_value}")
    
    def show_statistics(self):
        """显示统计信息"""
        print("\n📊 系统统计信息")
        
        # 显示支持的格式
        formats = self.document_service.get_supported_formats()
        print(f"📋 支持的文件格式: {', '.join(formats)}")
        
        # 显示配置摘要
        summary = self.config_manager.get_config_summary()
        print(f"⚙️ 配置文件: {summary['config_file']}")
        
        # 检查输入目录
        config = self.settings.get_config()
        input_dir = Path(config.input_folder)
        if input_dir.exists():
            files = self.document_service._collect_files(input_dir, recursive=True)
            print(f"📁 输入目录: {input_dir} ({len(files)} 个可处理文件)")
        else:
            print(f"📁 输入目录: {input_dir} (不存在)")
    
    def run(self):
        """运行CLI"""
        # 清屏
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # 显示Logo
        self.display_logo()
        
        print("🔍 正在检查系统依赖...")
        
        # 检查依赖
        try:
            import docx
            import jieba
            import nltk
            print("✅ 所有依赖检查通过")
        except ImportError as e:
            print(f"❌ 依赖检查失败: {e}")
            return
        
        # 主循环
        while True:
            self.display_menu()
            
            choice = input("请选择操作 (1-4): ").strip()
            
            if choice == '1':
                self.process_documents()
                input("\n按Enter键返回主菜单...")
            
            elif choice == '2':
                self.show_config()
                print("\n修改配置选项:")
                print("1. 修改配置")
                print("2. 返回主菜单")
                
                sub_choice = input("请选择 (1-2): ").strip()
                if sub_choice == '1':
                    self.modify_config()
                
                input("\n按Enter键返回主菜单...")
            
            elif choice == '3':
                self.show_statistics()
                input("\n按Enter键返回主菜单...")
            
            elif choice == '4':
                print("\n👋 感谢使用VerbaAurea！")
                break
            
            else:
                print("❌ 无效选择，请重新输入")
                time.sleep(1)


def main():
    """主函数"""
    try:
        cli = VerbaAureaCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\n\n👋 程序已退出")
    except Exception as e:
        print(f"\n❌ 程序运行出错: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
