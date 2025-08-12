#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文件夹树状视图
"""

from PySide6.QtWidgets import QTreeView, QFileSystemModel
from PySide6.QtCore import QDir, Qt


class FileTreeView(QTreeView):
    """文件夹树状视图类"""

    def __init__(self):
        super().__init__()
        self.init_model()
        self.init_ui()

    def init_model(self):
        """初始化模型"""
        self.model = QFileSystemModel()
        self.model.setRootPath("")
        self.model.setFilter(QDir.AllDirs | QDir.NoDotAndDotDot)
        
        # 设置模型
        self.setModel(self.model)

    def init_ui(self):
        """初始化UI"""
        # 隐藏列
        for i in range(1, self.model.columnCount()):
            self.hideColumn(i)

        # 设置标题
        self.setHeaderHidden(True)

        # 设置属性
        self.setAnimated(True)
        self.setIndentation(20)
        self.setSortingEnabled(True)
        self.sortByColumn(0, Qt.AscendingOrder)

    def set_root_path(self, path):
        """设置根路径"""
        index = self.model.setRootPath(path)
        self.setRootIndex(index)

    def get_root_path(self):
        """获取根路径"""
        root_index = self.rootIndex()
        return self.model.filePath(root_index) if root_index.isValid() else ""