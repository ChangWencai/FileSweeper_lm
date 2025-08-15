#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
重复文件表格视图
"""

import os
from PySide6.QtWidgets import (QTableView, QAbstractItemView, QHeaderView, 
                               QMenu, QMessageBox)
from PySide6.QtGui import QAction, QDesktopServices, QContextMenuEvent
from PySide6.QtCore import Qt, QModelIndex, Signal, QUrl
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
        
        # 查看模式
        self.view_mode = "details"  # details, list, grid

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
        self.setSortingEnabled(True)

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
            # 连接表头点击信号用于排序
            self.horizontalHeader().sectionClicked.connect(self.on_header_clicked)

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

    def on_header_clicked(self, logical_index):
        """处理表头点击事件用于排序"""
        if logical_index == self.model.CHECK_COLUMN:
            return  # 复选框列不排序
            
        # 实现排序逻辑
        self.model.sort_data(logical_index)
        
    def contextMenuEvent(self, event: QContextMenuEvent):
        """右键菜单事件"""
        menu = QMenu(self)
        
        # 获取选中的行
        selected_rows = self.selectionModel().selectedRows()
        
        if selected_rows:
            # 获取第一个选中行的数据
            index = selected_rows[0]
            file_info = self.model.get_file_info(index.row())
            
            if file_info and file_info['type'] == 'file':
                # 文件操作菜单项
                open_action = QAction("打开文件", self)
                open_action.triggered.connect(lambda: self.open_file(file_info['path']))
                menu.addAction(open_action)
                
                open_folder_action = QAction("在文件夹中显示", self)
                open_folder_action.triggered.connect(lambda: self.open_file_folder(file_info['path']))
                menu.addAction(open_folder_action)
                
                menu.addSeparator()
                
                # 文件选择操作
                select_all_action = QAction("全选", self)
                select_all_action.triggered.connect(self.select_all)
                menu.addAction(select_all_action)
                
                select_none_action = QAction("全不选", self)
                select_none_action.triggered.connect(self.deselect_all)
                menu.addAction(select_none_action)
                
                invert_selection_action = QAction("反选", self)
                invert_selection_action.triggered.connect(self.invert_selection)
                menu.addAction(invert_selection_action)
                
                menu.addSeparator()
                
                # 删除操作
                delete_action = QAction("删除选中文件", self)
                delete_action.triggered.connect(self.request_delete_selected)
                menu.addAction(delete_action)
        else:
            # 没有选中行时的菜单项
            select_all_action = QAction("全选", self)
            select_all_action.triggered.connect(self.select_all)
            menu.addAction(select_all_action)
            
        menu.exec(event.globalPos())
        
    def open_file(self, file_path):
        """打开文件"""
        try:
            QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开文件: {str(e)}")
            
    def open_file_folder(self, file_path):
        """在文件夹中显示文件"""
        try:
            folder_path = os.path.dirname(file_path)
            QDesktopServices.openUrl(QUrl.fromLocalFile(folder_path))
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开文件夹: {str(e)}")
            
    def request_delete_selected(self):
        """请求删除选中文件"""
        # 发送信号让主窗口处理删除操作
        self.checked_files_changed.emit()

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
        
    def deselect_all(self):
        """全不选所有文件"""
        self.model.deselect_all()
        
    def invert_selection(self):
        """反选所有文件"""
        self.model.invert_selection()
        
    def set_view_mode(self, mode):
        """设置查看模式"""
        self.view_mode = mode
        # 根据模式调整界面显示
        if mode == "details":
            self.set_view_details()
        elif mode == "list":
            self.set_view_list()
        elif mode == "grid":
            self.set_view_grid()
            
    def set_view_details(self):
        """设置详细信息视图"""
        self.setShowGrid(True)
        self.setAlternatingRowColors(True)
        
    def set_view_list(self):
        """设置列表视图"""
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)
        
    def set_view_grid(self):
        """设置网格视图"""
        self.setShowGrid(False)
        self.setAlternatingRowColors(False)
        # 网格视图下可以调整图标大小等





