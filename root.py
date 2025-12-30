from pathlib import Path


def get_project_root():
    """
    递归查询父目录，查找项目根目录
    
    通过查找包含settings.py文件的目录来确定项目根目录
    如果找不到，则返回当前文件的父目录
    
    Returns:
        Path: 项目根目录路径
    """
    current_path = Path(__file__).resolve()
    
    # 递归遍历所有父目录
    for parent in current_path.parents:
        # 检查当前目录是否包含settings.py文件
        settings_files = list(parent.glob("main.py"))
        if settings_files:
            return parent
        #
        # # 也可以检查其他项目标识文件
        # project_files = list(parent.glob("*.py"))
        # if len(project_files) > 5:  # 如果有多个Python文件，可能是项目根目录
        #     return parents
    
    # 如果找不到项目根目录，返回当前目录的父目录
    print("未找到明确的项目根目录标识，返回当前目录的父目录")
    return current_path.parent


if __name__ == "__main__":
    # 测试获取项目根目录
    root = get_project_root()
    print(f"项目根目录: {root}")
