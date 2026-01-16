# -*- coding: utf-8 -*-
"""
SLM 智能报价系统 - 程序入口
==============================
金属3D打印智能报价软件

版本: 2.1
作者: DW Tech
环境: Python 3.10+ / Windows 10/11
"""

import sys
import os

# 确保src目录在路径中
if getattr(sys, 'frozen', False):
    # 打包后的exe
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # 开发环境
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, BASE_DIR)


def main():
    """程序主入口"""
    try:
        # 导入数据库模块并初始化
        from src.database import init_db, close_db
        
        print("[SLM] SLM Smart Quoter v2.1")
        print("=" * 40)
        print("[DB] Initializing database...")
        
        # 初始化数据库
        init_db()
        print("[OK] Database ready")
        
        # 导入并启动UI
        print("[UI] Starting interface...")
        from src.ui.app_window import AppWindow
        
        # 创建主窗口
        app = AppWindow()
        
        print("[OK] Application started!")
        print("-" * 40)
        
        # 运行主循环
        app.mainloop()
        
        # 关闭数据库连接
        close_db()
        
    except ImportError as e:
        print(f"[ERROR] Import failed: {e}")
        print("Please install dependencies:")
        print("  pip install customtkinter peewee")
        input("Press Enter to exit...")
        sys.exit(1)
        
    except Exception as e:
        print(f"[ERROR] Runtime error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
        sys.exit(1)


if __name__ == "__main__":
    main()
