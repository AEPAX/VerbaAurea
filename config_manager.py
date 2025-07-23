import os
import json
import sys

DEFAULT_CONFIG = {
    "document_settings": {
        "max_length": 1000,
        "min_length": 300,
        "sentence_integrity_weight": 8.0,
        "table_length_factor": 1.2
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
        "force_split_before_heading": True
    }
}


def get_config_path():
    """获取配置文件路径"""
    # 获取脚本当前路径
    current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    if not current_dir:  # 如果为空，使用当前工作目录
        current_dir = os.getcwd()

    return os.path.join(current_dir, "config.json")


def load_config():
    """加载配置，如果配置文件不存在则创建默认配置"""
    config_path = get_config_path()

    if not os.path.exists(config_path):
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_CONFIG, f, ensure_ascii=False, indent=2)
        print(f"已创建默认配置文件: {config_path}")
        return DEFAULT_CONFIG

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # 检查配置完整性，补充缺失的默认值
        for section, settings in DEFAULT_CONFIG.items():
            if section not in config:
                config[section] = settings
            else:
                for key, value in settings.items():
                    if key not in config[section]:
                        config[section][key] = value

        return config
    except Exception as e:
        print(f"加载配置文件时出错: {str(e)}")
        print("使用默认配置")
        return DEFAULT_CONFIG


def save_config(config):
    """保存配置到文件"""
    config_path = get_config_path()

    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存配置文件时出错: {str(e)}")
        return False


def show_config():
    """展示当前配置"""
    config = load_config()
    print("\n当前配置:")

    # 文档设置
    doc_settings = config["document_settings"]
    print("\n文档设置:")
    print(f"  最大段落长度: {doc_settings['max_length']} 字符")
    print(f"  最小段落长度: {doc_settings['min_length']} 字符")
    print(f"  句子完整性权重: {doc_settings['sentence_integrity_weight']}")
    print(f"  表格文字权重: {doc_settings['table_length_factor']}")

    # 处理选项
    proc_options = config["processing_options"]
    print("\n处理选项:")
    print(f"  调试模式: {'开启' if proc_options['debug_mode'] else '关闭'}")
    print(f"  输出文件夹: {proc_options['output_folder']}")
    print(f"  跳过已存在文件: {'是' if proc_options['skip_existing'] else '否'}")

    # 高级设置
    adv_settings = config["advanced_settings"]
    print("\n高级设置:")
    print(f"  最小分割得分: {adv_settings['min_split_score']}")
    print(f"  标题加分: {adv_settings['heading_score_bonus']}")
    print(f"  句子结束加分: {adv_settings['sentence_end_score_bonus']}")
    print(f"  长度评分因子: {adv_settings['length_score_factor']}")
    print(f"  搜索窗口大小: {adv_settings['search_window']}")
    print(f"  标题后惩罚: {adv_settings['heading_after_penalty']}")

    return config


def edit_config():
    """交互式编辑配置"""
    config = load_config()

    print("\n编辑配置 (按Enter保留当前值):")

    # 文档设置
    print("\n文档设置:")
    max_length = input(f"  最大段落长度 [{config['document_settings']['max_length']}]: ")
    min_length = input(f"  最小段落长度 [{config['document_settings']['min_length']}]: ")
    sentence_weight = input(f"  句子完整性权重 [{config['document_settings']['sentence_integrity_weight']}]: ")

    if max_length.strip():
        try:
            config['document_settings']['max_length'] = int(max_length)
        except ValueError:
            print("  输入无效，保留原值")

    if min_length.strip():
        try:
            config['document_settings']['min_length'] = int(min_length)
        except ValueError:
            print("  输入无效，保留原值")

    if sentence_weight.strip():
        try:
            config['document_settings']['sentence_integrity_weight'] = float(sentence_weight)
        except ValueError:
            print("  输入无效，保留原值")

    # 处理选项
    print("\n处理选项:")
    debug_mode = input(f"  调试模式 (y/n) [{'y' if config['processing_options']['debug_mode'] else 'n'}]: ")
    output_folder = input(f"  输出文件夹 [{config['processing_options']['output_folder']}]: ")
    skip_existing = input(f"  跳过已存在文件 (y/n) [{'y' if config['processing_options']['skip_existing'] else 'n'}]: ")

    if debug_mode.strip():
        config['processing_options']['debug_mode'] = debug_mode.lower() == 'y'

    if output_folder.strip():
        config['processing_options']['output_folder'] = output_folder

    if skip_existing.strip():
        config['processing_options']['skip_existing'] = skip_existing.lower() == 'y'

    # 询问是否编辑高级设置
    edit_advanced = input("\n是否编辑高级设置? (y/n, 默认n): ").lower().strip() == 'y'

    if edit_advanced:
        print("\n高级设置:")
        min_score = input(f"  最小分割得分 [{config['advanced_settings']['min_split_score']}]: ")
        heading_bonus = input(f"  标题加分 [{config['advanced_settings']['heading_score_bonus']}]: ")
        sentence_bonus = input(f"  句子结束加分 [{config['advanced_settings']['sentence_end_score_bonus']}]: ")
        length_factor = input(f"  长度评分因子 [{config['advanced_settings']['length_score_factor']}]: ")
        window = input(f"  搜索窗口大小 [{config['advanced_settings']['search_window']}]: ")

        if min_score.strip():
            try:
                config['advanced_settings']['min_split_score'] = float(min_score)
            except ValueError:
                print("  输入无效，保留原值")

        if heading_bonus.strip():
            try:
                config['advanced_settings']['heading_score_bonus'] = float(heading_bonus)
            except ValueError:
                print("  输入无效，保留原值")

        if sentence_bonus.strip():
            try:
                config['advanced_settings']['sentence_end_score_bonus'] = float(sentence_bonus)
            except ValueError:
                print("  输入无效，保留原值")

        if length_factor.strip():
            try:
                config['advanced_settings']['length_score_factor'] = int(length_factor)
            except ValueError:
                print("  输入无效，保留原值")

        if window.strip():
            try:
                config['advanced_settings']['search_window'] = int(window)
            except ValueError:
                print("  输入无效，保留原值")

    # 保存配置
    if save_config(config):
        print("配置已保存")

    return config