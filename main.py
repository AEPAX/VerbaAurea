#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
VerbaAurea - 高质量文档预处理工具
主程序入口
"""

import time
import sys
import os
from typing import List, Tuple
from datetime import datetime

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    from rich.table import Table
    from rich.text import Text
    from rich.prompt import Prompt, Confirm
    from rich import box
    from rich.style import Style
    from rich.align import Align
except ImportError:
    print("正在安装必要的依赖...")
    import subprocess

    subprocess.check_call([sys.executable, "-m", "pip", "install", "rich"])
    from rich.console import Console
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    from rich.table import Table
    from rich.text import Text
    from rich.prompt import Prompt, Confirm
    from rich import box
    from rich.style import Style
    from rich.align import Align

# 导入项目模块
from config_manager import load_config, show_config, edit_config, save_config
from parallel_processor import process_all_documents
from utils import check_dependencies

# 创建Rich控制台
console = Console()

# 应用程序版本
VERSION = "1.0.0"


def display_logo():
    """显示VerbaAurea的ASCII艺术logo"""
    logo = """
[bold gold1]
▀█▀█▀█▀█▀█▀█▀█▀█▀█▀█▀█▀█▀█▀█▀█▀█▀█▀█▀█▀█▀█▀█▀█▀█▀█▀█▀█▀█▀█▀█▀█▀

██╗   ██╗███████╗██████╗ ██████╗  █████╗      █████╗ ██╗   ██╗██████╗ ███████╗ █████╗ 
██║   ██║██╔════╝██╔══██╗██╔══██╗██╔══██╗    ██╔══██╗██║   ██║██╔══██╗██╔════╝██╔══██╗
██║   ██║█████╗  ██████╔╝██████╔╝███████║    ███████║██║   ██║██████╔╝█████╗  ███████║
╚██╗ ██╔╝██╔══╝  ██╔══██╗██╔══██╗██╔══██║    ██╔══██║██║   ██║██╔══██╗██╔══╝  ██╔══██║
 ╚████╔╝ ███████╗██║  ██║██████╔╝██║  ██║    ██║  ██║╚██████╔╝██║  ██║███████╗██║  ██║
  ╚═══╝  ╚══════╝╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝    ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝

▀█▀█▀█▀█▀█▀█▀█▀█▀█▀█▀█▀█▀█▀█▀█▀█▀█▀█▀█▀█▀█▀█▀█▀█▀█▀█▀█▀█▀█▀█▀█▀
[/bold gold1]
"""

    tagline = """
[italic yellow]"Verba Aurea" - 文字的炼金术，知识的黄金[/italic yellow]
[bold white]v""" + VERSION + """[/bold white] | [cyan]专注于为知识库构建提供高质量的文本数据[/cyan]
    """

    console.print(Align.center(logo))
    console.print(Align.center(tagline))


def display_header():
    """显示应用程序标题和版本信息"""
    display_logo()

    # 显示系统信息
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    info_table = Table(show_header=False, box=None, show_edge=False, padding=(0, 2))
    info_table.add_column(style="bright_blue")
    info_table.add_column(style="white")

    info_table.add_row("系统时间:", now)
    info_table.add_row("Python版本:", f"{sys.version.split()[0]}")
    info_table.add_row("平台:", f"{sys.platform}")

    console.print(Align.center(info_table))

    console.print()
    console.print(Align.center("[dim bright_black]" + "=" * 80 + "[/dim bright_black]"))
    console.print()


def display_menu():
    """显示美化的主菜单"""
    menu_table = Table(
        show_header=False,
        box=box.ROUNDED,
        border_style="bright_blue",
        width=60,
        highlight=True
    )
    menu_table.add_column(style="cyan", justify="center", width=6)
    menu_table.add_column(style="white")
    menu_table.add_column(style="dim", width=30)

    menu_table.add_row("[1]", "[bold cyan]开始处理文档[/bold cyan]", "[dim]对文档进行预处理和优化[/dim]")
    menu_table.add_row("[2]", "[bold yellow]查看当前配置[/bold yellow]", "[dim]显示系统当前配置参数[/dim]")
    menu_table.add_row("[3]", "[bold green]编辑配置[/bold green]", "[dim]调整系统参数和处理规则[/dim]")
    menu_table.add_row("[4]", "[bold red]退出[/bold red]", "[dim]退出程序[/dim]")

    console.print(Align.center(Panel(
        menu_table,
        title="[bold]主菜单[/bold]",
        border_style="bright_blue",
        width=70,
        subtitle="[dim]请选择操作[/dim]"
    )))


def animated_loading():
    """显示动画加载效果"""
    with Progress(
            SpinnerColumn(spinner_name="dots"),
            TextColumn("[cyan]系统加载中...[/cyan]"),
            transient=True,
    ) as progress:
        task = progress.add_task("", total=100)
        while not progress.finished:
            progress.update(task, advance=1.5)
            time.sleep(0.05)


def process_documents_with_progress(config):
    """处理文档并显示漂亮的进度条"""
    # 模拟扫描文档数量
    console.print()
    console.print(Panel("[yellow]正在扫描文档目录...[/yellow]",
                        border_style="yellow",
                        box=box.ROUNDED))

    with Progress(
            SpinnerColumn(spinner_name="dots"),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=40, complete_style="green", finished_style="green"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console,
            expand=True
    ) as progress:
        # 开始处理任务
        scan_task = progress.add_task("[bright_yellow]扫描文档中...", total=100)

        # 模拟扫描过程
        for i in range(101):
            progress.update(scan_task, completed=i)
            time.sleep(0.01)

        # 处理文档任务
        task = progress.add_task("[cyan]处理文档中...", total=100)

        # 调用实际处理函数，但需要修改process_all_documents来支持进度报告
        # 这里简单模拟进度更新
        total_files, processed_files, failed_files = process_all_documents(config)

        # 确保进度条完成
        progress.update(task, completed=100)

    return total_files, processed_files, failed_files


def display_processing_results(total_files, processed_files, failed_files, elapsed_time):
    """显示处理结果的统计信息"""
    # 计算成功率
    success_rate = (processed_files / total_files * 100) if total_files > 0 else 0

    results_table = Table(box=box.SIMPLE_HEAD, border_style="green")
    results_table.add_column("项目", style="dim cyan", justify="right")
    results_table.add_column("数值", style="green bold")
    results_table.add_column("详情", style="dim")

    results_table.add_row("总文档数", f"{total_files}", "")
    results_table.add_row("成功处理", f"{processed_files}",
                          f"[{'green' if success_rate > 90 else 'yellow' if success_rate > 70 else 'red'}]{success_rate:.1f}%[/]")
    results_table.add_row("处理失败", f"{len(failed_files)}",
                          "[dim red]详见下方失败列表[/dim red]" if failed_files else "[green]无[/green]")
    results_table.add_row("总处理时间", f"{elapsed_time:.2f}秒", "")

    if processed_files > 0:
        avg_time = elapsed_time / processed_files
        results_table.add_row("平均处理时间", f"{avg_time:.2f}秒/文档",
                              f"[{'green' if avg_time < 1 else 'yellow' if avg_time < 3 else 'red'}]{'快速' if avg_time < 1 else '正常' if avg_time < 3 else '较慢'}[/]")

    # 添加处理总结
    quality_note = ""
    if success_rate == 100:
        quality_note = "[bold green]完美处理！所有文档都已成功优化。[/bold green]"
    elif success_rate > 95:
        quality_note = "[bold green]优秀！绝大多数文档都已成功处理。[/bold green]"
    elif success_rate > 80:
        quality_note = "[yellow]良好。大部分文档已成功处理，但有少量失败。[/yellow]"
    else:
        quality_note = "[bold red]需注意！有较多文档处理失败，请检查原因。[/bold red]"

    panel_title = f"[bold green]处理结果摘要 {'✓' if success_rate > 90 else '⚠'}[/bold green]"

    console.print(Panel(
        Align.center(results_table),
        title=panel_title,
        border_style="green",
        box=box.ROUNDED,
        width=80,
        subtitle=quality_note
    ))

    if failed_files:
        # 创建失败文件表格
        failed_table = Table(box=box.SIMPLE, show_header=True, border_style="red")
        failed_table.add_column("№", style="dim", justify="right")
        failed_table.add_column("文件名", style="red")
        failed_table.add_column("可能原因", style="yellow dim")

        for i, file in enumerate(failed_files, 1):
            # 这里可以添加实际的失败原因分析，暂时用占位符
            reason = "格式不支持或内容损坏"
            failed_table.add_row(f"{i}", file, reason)

        console.print(Panel(
            failed_table,
            title=f"[bold red]处理失败的文件 ({len(failed_files)})[/bold red]",
            border_style="red",
            box=box.ROUNDED,
            width=80
        ))


def display_config(config):
    """显示当前配置的美化版本"""
    # 创建配置表
    config_table = Table(box=box.SIMPLE_HEAD, border_style="blue", highlight=True)
    config_table.add_column("配置项", style="bright_cyan", justify="right")
    config_table.add_column("当前值", style="yellow")
    config_table.add_column("说明", style="dim")

    # 添加主要配置
    config_table.add_row("输入目录", config.get("input_folder", "当前目录"), "待处理文档的源目录")
    config_table.add_row(
        "输出目录",
        config.get("processing_options", {}).get("output_folder", "output"),
        "处理后文档的存放目录"
    )

    # 分割规则部分
    config_table.add_section()
    config_table.add_row("[bold blue]分割规则[/bold blue]", "", "")
    splitting_rules = config.get("splitting_rules", {})
    for rule, value in splitting_rules.items():
        config_table.add_row(rule, str(value), "文档分割参数")

    # 性能设置部分
    config_table.add_section()
    config_table.add_row("[bold blue]性能设置[/bold blue]", "", "")
    perf = config.get("performance_settings", {})
    config_table.add_row(
        "并行处理",
        "[green]✓ 开启[/green]" if perf.get("parallel_processing", True) else "[red]❌ 关闭[/red]",
        "多线程并行处理文档"
    )
    config_table.add_row(
        "工作线程数",
        f"{perf.get('num_workers', 0)}",
        "[dim]0=自动选择CPU核心数[/dim]"
    )
    config_table.add_row("缓存大小", f"{perf.get('cache_size', 1024)}MB", "内存缓存大小")
    config_table.add_row("批处理大小", str(perf.get("batch_size", 50)), "每批处理的文档数量")

    console.print(Panel(
        config_table,
        title="[bold blue]系统配置详情[/bold blue]",
        subtitle="[dim]使用 [3] 编辑配置 选项可修改这些参数[/dim]",
        border_style="blue",
        box=box.ROUNDED,
        width=90
    ))


def edit_config_interactive(config):
    """交互式编辑配置的美化版本"""
    console.print(Panel(
        "[bold yellow]进入配置编辑模式[/bold yellow]\n"
        "[dim]请按提示输入新的配置值，或直接按回车保留当前值[/dim]",
        border_style="yellow",
        box=box.ROUNDED,
        width=80
    ))

    # 使用Rich的Prompt组件获取输入
    input_folder = Prompt.ask(
        "输入目录",
        default=config.get("input_folder", "."),
        show_default=True
    )
    config["input_folder"] = input_folder

    output_folder = Prompt.ask(
        "输出目录",
        default=config.get("processing_options", {}).get("output_folder", "output"),
        show_default=True
    )
    if "processing_options" not in config:
        config["processing_options"] = {}
    config["processing_options"]["output_folder"] = output_folder

    # 编辑性能设置
    console.print("\n[yellow]性能设置:[/yellow]")
    if "performance_settings" not in config:
        config["performance_settings"] = {
            "parallel_processing": True,
            "num_workers": 0,
            "cache_size": 1024,
            "batch_size": 50
        }

    perf = config["performance_settings"]
    parallel = Confirm.ask(
        "启用并行处理?",
        default=perf.get("parallel_processing", True)
    )
    perf['parallel_processing'] = parallel

    workers = int(Prompt.ask(
        "工作线程数 [dim](0=自动)[/dim]",
        default=str(perf.get("num_workers", 0)),
        show_default=True
    ))
    perf['num_workers'] = workers

    cache = int(Prompt.ask(
        "缓存大小 (MB)",
        default=str(perf.get("cache_size", 1024)),
        show_default=True
    ))
    perf['cache_size'] = cache

    batch = int(Prompt.ask(
        "批处理大小",
        default=str(perf.get("batch_size", 50)),
        show_default=True
    ))
    perf['batch_size'] = batch

    # 保存配置
    save_config(config)
    console.print(Panel(
        "[green bold]✓ 配置已成功保存[/green bold]",
        border_style="green",
        box=box.ROUNDED
    ))



def main():
    """主函数"""
    # 清屏
    os.system('cls' if os.name == 'nt' else 'clear')

    # 显示标题和动画
    display_header()
    animated_loading()

    # 检查必要的库
    console.print("[dim]正在检查系统依赖...[/dim]")
    check_dependencies()

    # 加载配置
    config = load_config()

    # 确保性能配置存在
    if "performance_settings" not in config:
        config["performance_settings"] = {
            "parallel_processing": True,
            "num_workers": 0,  # 0表示自动选择
            "cache_size": 1024,  # 缓存大小(MB)
            "batch_size": 50
        }
        save_config(config)

    while True:
        # 显示主菜单
        display_menu()

        choice = Prompt.ask(
            "请选择操作",
            choices=["1", "2", "3", "4"],
            default="1",
            show_choices=False,
            show_default=False
        )

        if choice == '1':
            # 开始处理文档
            console.print("\n[bold cyan]开始文档处理任务[/bold cyan]")
            start_time = time.time()

            total_files, processed_files, failed_files = process_documents_with_progress(config)

            elapsed_time = time.time() - start_time

            # 显示结果
            display_processing_results(total_files, processed_files, failed_files, elapsed_time)

            console.print(
                f"\n处理后的文档已保存在目录: [green bold]'{config['processing_options']['output_folder']}'[/green bold]"
            )

            Prompt.ask("[dim]按Enter键返回主菜单[/dim]", default="")

        elif choice == '2':
            # 查看当前配置
            display_config(config)
            Prompt.ask("[dim]按Enter键返回主菜单[/dim]", default="")

        elif choice == '3':
            # 编辑配置
            edit_config_interactive(config)
            # 重新加载配置以确保使用最新的值
            config = load_config()
            Prompt.ask("[dim]按Enter键返回主菜单[/dim]", default="")

        elif choice == '4':
            # 退出
            console.print(Panel(
                "[bold gold1]感谢使用 VerbaAurea![/bold gold1]\n"
                "[italic]黄金之言，知识探索的未来[/italic]",
                border_style="gold1",
                box=box.ROUNDED,
                width=60
            ))
            break

        # 每次操作后清屏以保持界面干净
        os.system('cls' if os.name == 'nt' else 'clear')
        display_header()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]程序被用户中断[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[bold red]错误:[/bold red] {str(e)}")
        sys.exit(1)