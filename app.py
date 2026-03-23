"""
主程序入口
"""
import sys
import os

# 添加项目根目录和 src/ 到路径，使 src/ 内的模块可相互导入
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

from main_window import main

if __name__ == '__main__':
    main()
