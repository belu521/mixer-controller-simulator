#!/usr/bin/env python3
# main.py
# 混音控制器模拟器 - 主入口文件

import sys
import os

# 确保可以找到mixer_simulator包
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from mixer_simulator.ui.main_window import MainWindow


def main():
    """主入口函数"""
    # 高DPI支持
    os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")

    app = QApplication(sys.argv)
    app.setApplicationName("混音控制器模拟器")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("MixerSimulator")

    # 创建并显示主窗口
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
