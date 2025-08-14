#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
重复文件数据模型
"""

import os
from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex, QDateTime, Signal
from PySide6.QtGui import QBrush, QColor


class DuplicateModel(QAbstractTableModel):
    """重复文件数据模型类"""
    
    # 选中文件改变信号
    checked_files_changed = Signal()
    
    # 列定义
    CHECK_COLUMN = 0
    PATH_COLUMN = 1
    SIZE_COLUMN = 2
    MODIFIED_COLUMN = 3
    COLUMN_COUNT = 4

    def __init__(self):
        super().__init__()
        self.duplicates = {}  # {hash: [file_path, ...]}
        self.display_items = []  # 显示项目列表 [{type: 'group', hash: ..., text: ...} | {type: 'file', hash: ..., path: ...}]
        self.checked_files = set()  # 选中的文件集合
        self.auto_select_duplicates = True  # 是否默认选中重复文件
        self.auto_select_strategy = "first"  # 自动选择策略: first(保留第一个), newest(保留最新), folder(保留特定文件夹)
        self.auto_select_folder = ""         # 特定文件夹路径

    def rowCount(self, parent=QModelIndex()):
        """返回行数"""
        return len(self.display_items)

    def columnCount(self, parent=QModelIndex()):
        """返回列数"""
        return self.COLUMN_COUNT

    def data(self, index, role=Qt.DisplayRole):
        """返回数据"""
        if not index.isValid() or index.row() >= len(self.display_items):
            return None

        item = self.display_items[index.row()]

        # 组标题行
        if item['type'] == 'group':
            if index.column() == self.PATH_COLUMN and role == Qt.DisplayRole:
                return item['text']
            elif role == Qt.BackgroundRole:
                # 组标题使用特殊背景色
                return QBrush(QColor(200, 200, 200))
            elif role == Qt.FontRole:
                # 组标题使用粗体
                from PySide6.QtGui import QFont
                font = QFont()
                font.setBold(True)
                return font
            elif role == Qt.TextAlignmentRole:
                return Qt.AlignLeft | Qt.AlignVCenter

        # 文件行
        elif item['type'] == 'file':
            file_path = item['path']
            
            if index.column() == self.CHECK_COLUMN:
                if role == Qt.CheckStateRole:
                    return Qt.Checked if file_path in self.checked_files else Qt.Unchecked
                elif role == Qt.BackgroundRole:
                    # 为不同的重复组设置不同颜色背景
                    hue = (hash(item['hash']) % 360)
                    color = QColor.fromHsv(hue, 20, 255, 128)
                    return QBrush(color)
                    
            elif role == Qt.DisplayRole:
                if index.column() == self.PATH_COLUMN:
                    return file_path
                elif index.column() == self.SIZE_COLUMN:
                    try:
                        size = os.path.getsize(file_path)
                        return self._format_file_size(size)
                    except:
                        return "未知"
                elif index.column() == self.MODIFIED_COLUMN:
                    try:
                        mtime = os.path.getmtime(file_path)
                        return QDateTime.fromSecsSinceEpoch(int(mtime)).toString("yyyy-MM-dd hh:mm:ss")
                    except:
                        return "未知"

            elif role == Qt.TextAlignmentRole:
                if index.column() == self.SIZE_COLUMN:
                    return Qt.AlignRight | Qt.AlignVCenter
                return Qt.AlignLeft | Qt.AlignVCenter

        return None

    def setData(self, index, value, role=Qt.EditRole):
        """设置数据"""
        if not index.isValid() or index.row() >= len(self.display_items):
            return False

        item = self.display_items[index.row()]
        
        # 只处理文件行的复选框列
        if item['type'] == 'file' and index.column() == self.CHECK_COLUMN and role == Qt.CheckStateRole:
            file_path = item['path']
            if value == Qt.Checked:
                self.checked_files.add(file_path)
            else:
                self.checked_files.discard(file_path)
            
            # 发出数据改变信号
            self.dataChanged.emit(index, index, [Qt.CheckStateRole])
            
            # 发出选中文件改变信号
            self.checked_files_changed.emit()
            
            return True
            
        return False

    def flags(self, index):
        """返回项目标志"""
        if not index.isValid() or index.row() >= len(self.display_items):
            return Qt.NoItemFlags

        item = self.display_items[index.row()]
        
        # 组标题行不可选择和编辑
        if item['type'] == 'group':
            return Qt.ItemIsEnabled
            
        # 文件行
        elif item['type'] == 'file':
            if index.column() == self.CHECK_COLUMN:
                return Qt.ItemIsEnabled | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable

        return Qt.NoItemFlags

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """返回表头数据"""
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            if section == self.CHECK_COLUMN:
                return "选择"
            elif section == self.PATH_COLUMN:
                return "文件路径"
            elif section == self.SIZE_COLUMN:
                return "大小"
            elif section == self.MODIFIED_COLUMN:
                return "修改时间"

        return None

    def update_data(self, duplicates):
        """更新数据"""
        self.beginResetModel()
        self.duplicates = duplicates
        
        # 构建显示项目列表
        self.display_items = []
        self.checked_files.clear()
        
        # 为每组重复文件添加组标题和文件项
        for hash_value, files in duplicates.items():
            # 添加组标题
            group_text = f"重复文件组 (共{len(files)}个文件)"
            self.display_items.append({
                'type': 'group',
                'hash': hash_value,
                'text': group_text
            })
            
            # 根据策略确定保留的文件
            keep_file = self._determine_keep_file(files)
            
            # 添加文件项
            for file_path in files:
                self.display_items.append({
                    'type': 'file',
                    'hash': hash_value,
                    'path': file_path
                })
                
                # 根据策略和设置决定是否选中文件（除了保留的文件）
                if self.auto_select_duplicates and file_path != keep_file:
                    self.checked_files.add(file_path)
        
        self.endResetModel()

    def get_file_info(self, row):
        """获取指定行的文件信息"""
        if 0 <= row < len(self.display_items):
            return self.display_items[row]
        return None

    def get_duplicate_groups(self):
        """获取重复文件组"""
        return self.duplicates

    def get_checked_files(self):
        """获取选中的文件列表"""
        return list(self.checked_files)
        
    def set_auto_select_duplicates(self, auto_select):
        """设置是否默认选中重复文件"""
        self.auto_select_duplicates = auto_select
        
    def set_auto_select_strategy(self, strategy, folder=""):
        """设置自动选择策略"""
        self.auto_select_strategy = strategy
        self.auto_select_folder = folder

    def apply_auto_select_strategy(self):
        """应用自动选择策略到当前数据"""
        self.beginResetModel()
        
        # 清空当前选中文件
        self.checked_files.clear()
        
        # 为每组重复文件应用策略
        for hash_value, files in self.duplicates.items():
            if len(files) <= 1:
                # 只有一个文件或没有文件，不需要处理
                continue
                
            # 根据策略确定保留的文件
            keep_file = self._determine_keep_file(files)
            
            # 选择除保留文件外的所有文件
            for file_path in files:
                if file_path != keep_file:
                    self.checked_files.add(file_path)
        
        self.endResetModel()
        self.checked_files_changed.emit()

    def select_all(self):
        """全选所有文件"""
        self.beginResetModel()
        self.checked_files.clear()
        for item in self.display_items:
            if item['type'] == 'file':
                self.checked_files.add(item['path'])
        self.endResetModel()
        self.checked_files_changed.emit()

    def deselect_all(self):
        """全不选所有文件"""
        self.beginResetModel()
        self.checked_files.clear()
        self.endResetModel()
        self.checked_files_changed.emit()

    def invert_selection(self):
        """反选所有文件"""
        self.beginResetModel()
        current_checked = self.checked_files.copy()
        self.checked_files.clear()
        for item in self.display_items:
            if item['type'] == 'file':
                if item['path'] not in current_checked:
                    self.checked_files.add(item['path'])
        self.endResetModel()
        self.checked_files_changed.emit()

    def _determine_keep_file(self, files):
        """根据策略确定保留的文件"""
        if not files:
            return None
                
        # 如果只有一份文件，直接保留
        if len(files) == 1:
            return files[0]
                
        # 根据策略选择保留的文件
        if self.auto_select_strategy == "first":
            # 保留第一个文件
            return files[0]
                
        elif self.auto_select_strategy == "newest":
            # 保留最新修改的文件
            newest_file = files[0]
            newest_time = 0
            try:
                newest_time = os.path.getmtime(files[0])
            except:
                pass
                    
            for file_path in files[1:]:
                try:
                    file_time = os.path.getmtime(file_path)
                    if file_time > newest_time:
                        newest_time = file_time
                        newest_file = file_path
                except:
                    continue
                        
            return newest_file
                
        elif self.auto_select_strategy == "folder" and self.auto_select_folder:
            # 保留特定文件夹中的文件
            for file_path in files:
                try:
                    if self.auto_select_folder in file_path:
                        return file_path
                except:
                    continue
            # 如果没有文件在指定文件夹中，回退到保留第一个文件
            return files[0]
                
        else:
            # 默认保留第一个文件
            return files[0]
                
    def set_auto_select_strategy(self, strategy, folder=""):
        """设置自动选择策略"""
        self.auto_select_strategy = strategy
        self.auto_select_folder = folder
