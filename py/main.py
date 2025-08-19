#!/usr/bin/env python3
"""
MetaData String Editor - Python版本
主程序入口点

用于编辑Unity global-metadata.dat文件中的字符串内容
"""
import sys
import os
import argparse
import tkinter as tk
from tkinter import messagebox

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main_window import MainWindow
from utils import Logger


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="MetaData String Editor - 用于编辑Unity global-metadata.dat文件中的字符串",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py                           # 启动GUI界面
  python main.py file.dat                  # 启动GUI并加载指定文件
  python main.py --help                    # 显示帮助信息

支持的文件格式:
  - Unity global-metadata.dat 文件
  - 由Il2CppDumper生成的元数据文件

快捷键:
  Ctrl+O      打开文件
  Ctrl+S      另存为
  Ctrl+F      搜索
  F3          查找下一个
  Shift+F3    查找上一个
  Esc         清除搜索
  Ctrl+Q      退出程序
        """
    )
    
    parser.add_argument(
        "file",
        nargs="?",
        help="要加载的global-metadata.dat文件路径"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="MetaData String Editor Python版本 1.0.0"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="启用调试模式，显示详细日志"
    )
    
    return parser.parse_args()


def check_dependencies():
    """检查依赖项"""
    try:
        import tkinter
        import tkinter.ttk
        import tkinter.filedialog
        import tkinter.messagebox
    except ImportError as e:
        print(f"错误: 缺少必要的依赖项: {e}")
        print("请确保已安装Python的tkinter模块")
        if sys.platform.startswith("linux"):
            print("在Ubuntu/Debian上，请运行: sudo apt-get install python3-tk")
        elif sys.platform.startswith("darwin"):
            print("在macOS上，tkinter通常随Python一起安装")
        elif sys.platform.startswith("win"):
            print("在Windows上，tkinter通常随Python一起安装")
        return False
    
    return True


def setup_logging(debug_mode=False):
    """设置日志"""
    if debug_mode:
        Logger.set_debug_mode(True)
        Logger.info("调试模式已启用")


def main():
    """主函数"""
    try:
        # 解析命令行参数
        args = parse_arguments()
        
        # 检查依赖项
        if not check_dependencies():
            sys.exit(1)
        
        # 设置日志
        setup_logging(args.debug)
        
        # 验证文件参数
        file_to_load = None
        if args.file:
            if os.path.exists(args.file):
                file_to_load = os.path.abspath(args.file)
                Logger.info(f"将加载文件: {file_to_load}")
            else:
                print(f"错误: 文件不存在: {args.file}")
                sys.exit(1)
        
        # 创建主窗口
        Logger.info("启动MetaData String Editor")
        app = MainWindow()
        
        # 如果指定了文件，则在启动后加载
        if file_to_load:
            app.load_file_on_startup(file_to_load)
        
        # 运行应用程序
        app.run()
        
    except KeyboardInterrupt:
        Logger.info("用户中断程序")
        sys.exit(0)
    except Exception as e:
        error_msg = f"程序启动失败: {str(e)}"
        Logger.error(error_msg)
        
        # 尝试显示错误对话框
        try:
            root = tk.Tk()
            root.withdraw()  # 隐藏主窗口
            messagebox.showerror("启动错误", error_msg)
        except:
            print(error_msg)
        
        sys.exit(1)


if __name__ == "__main__":
    main()