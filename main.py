#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文件清理工具(FileSweeper)主程序
跨平台的图形化应用程序，帮助用户识别、查看和管理计算机上的重复文件
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PySide6.QtCore import Qt

from ui.main_window import MainWindow


def main():
    """主函数"""
    # 设置高DPI支持
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    # Qt.AA_EnableHighDpiScaling 和 Qt.AA_UseHighDpiPixmaps 已弃用，从Qt 6.4开始不再需要

    # 创建应用程序实例
    app = QApplication(sys.argv)
    app.setApplicationName("FileSweeper")
    app.setApplicationDisplayName("文件清理工具")
    app.setOrganizationName("FileSweeper")
    app.setApplicationVersion("1.0.0")

    try:
        # 创建主窗口
        window = MainWindow()
        window.show()
    except Exception as e:
        QMessageBox.critical(None, "错误", f"程序启动失败：{str(e)}")
        sys.exit(1)

    # 运行应用程序
    sys.exit(app.exec())


if __name__ == "__main__":
    main()