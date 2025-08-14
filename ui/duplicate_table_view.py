#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
重复文件表格视图
"""

import os
from PySide6.QtWidgets import QTableView, QAbstractItemView, QHeaderView
from PySide6.QtCore import Qt, QModelIndex, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl
from ui.duplicate_model import DuplicateModel


class DuplicateTableView(QTableView):
    """重复文件表格视图类"""
    
    # 文件选中状态改变信号
    checked_files_changed = Signal()
    
    # 文件被选中信号
    file_selected = Signal(str)

    def __init__(self):
        super().__init__()
        self.model = DuplicateModel()
        self.init_ui()
        self.init_connections()

    def init_ui(self):
        """初始化UI"""
        # 设置模型
        self.setModel(self.model)
        
        # 设置选择行为
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # 设置编辑行为
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # 设置排序
        self.setSortingEnabled(False)  # 分组显示时禁用排序

        # 设置网格线
        self.setShowGrid(True)

        # 设置交替行颜色
        self.setAlternatingRowColors(True)

        # 设置水平表头
        if self.horizontalHeader():
            self.horizontalHeader().setStretchLastSection(True)
            self.horizontalHeader().setHighlightSections(False)
            # 设置选择列的大小
            self.horizontalHeader().setSectionResizeMode(self.model.CHECK_COLUMN, QHeaderView.Fixed)
            self.setColumnWidth(self.model.CHECK_COLUMN, 60)

        # 设置垂直表头
        if self.verticalHeader():
            self.verticalHeader().setVisible(False)
            self.verticalHeader().setDefaultSectionSize(24)

        # 设置选择样式
        self.setStyleSheet("""
            QTableView {
                selection-background-color: #a0d2eb;
                selection-color: black;
            }
        """)

    def init_connections(self):
        """初始化信号连接"""
        # 连接模型的信号
        self.model.checked_files_changed.connect(self.checked_files_changed)
        
        # 连接选择改变信号
        self.selectionModel().selectionChanged.connect(self.on_selection_changed)
        
    def on_selection_changed(self, selected, deselected):
        """处理选择改变事件"""
        # 获取当前选中的索引
        indexes = self.selectionModel().selectedRows()
        if indexes:
            # 获取第一个选中行的数据
            index = indexes[0]
            file_info = self.model.get_file_info(index.row())
            if file_info and file_info['type'] == 'file':
                # 发送文件选中信号
                self.file_selected.emit(file_info['path'])

    def on_model_data_changed(self, topLeft, bottomRight, roles):
        """模型数据改变时的处理"""
        if Qt.CheckStateRole in roles:
            self.checked_files_changed.emit()

    def on_double_clicked(self, index):
        """双击文件时的处理"""
        if not index.isValid():
            return
            
        # 获取文件信息
        item = self.model.get_file_info(index.row())
        
        # 只处理文件行，不处理组标题行
        if item and item['type'] == 'file':
            file_path = item['path']
            
            # 检查文件是否存在
            if os.path.exists(file_path):
                # 使用系统默认应用打开文件
                url = QUrl.fromLocalFile(file_path)
                QDesktopServices.openUrl(url)
            else:
                # 文件不存在时提示用户
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "文件不存在", f"文件不存在或已被删除:\n{file_path}")

    def update_data(self, duplicates):
        """更新表格数据"""
        self.model.update_data(duplicates)
        
        # 调整列宽
        self.resizeColumnsToContents()
        
        # 至少保证路径列可以显示完整路径
        if self.model.columnCount() > 0:
            self.setColumnWidth(self.model.PATH_COLUMN, max(300, self.columnWidth(self.model.PATH_COLUMN)))
            
        # 发出选中文件改变信号
        self.checked_files_changed.emit()

    def get_checked_files(self):
        """获取选中的文件列表"""
        return self.model.get_checked_files()

    def select_all(self):
        """全选所有文件"""
        self.model.select_all()
        self.checked_files_changed.emit()

    def deselect_all(self):
        """全不选所有文件"""
        self.model.deselect_all()
        self.checked_files_changed.emit()

    def invert_selection(self):
        """反选所有文件"""
        self.model.invert_selection()
        self.checked_files_changed.emit()





