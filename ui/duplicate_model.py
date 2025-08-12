#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
重复文件数据模型
"""

import os
from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex, QDateTime
from PySide6.QtGui import QBrush, QColor


class DuplicateModel(QAbstractTableModel):
    """重复文件数据模型类"""
    
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
        
        # 只有文件行可以设置选中状态
        if item['type'] == 'file' and role == Qt.CheckStateRole and index.column() == self.CHECK_COLUMN:
            file_path = item['path']
            
            # 正确处理勾选状态切换
            # 使用明确的数值比较，避免Qt枚举值比较问题
            if value == 2:  # Qt.Checked
                self.checked_files.add(file_path)
            elif value == 0:  # Qt.Unchecked
                self.checked_files.discard(file_path)
            
            # 修复dataChanged调用，提供有效的索引范围
            self.dataChanged.emit(index, index, [Qt.CheckStateRole])
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
            
            # 添加文件项
            for i, file_path in enumerate(files):
                self.display_items.append({
                    'type': 'file',
                    'hash': hash_value,
                    'path': file_path
                })
                
                # 根据设置决定是否默认选中重复文件
                if self.auto_select_duplicates and i > 0:
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

    def select_all(self):
        """全选所有文件"""
        self.beginResetModel()
        self.checked_files.clear()
        for item in self.display_items:
            if item['type'] == 'file':
                self.checked_files.add(item['path'])
        self.endResetModel()
        # 修复：不再手动触发dataChanged，beginResetModel/endResetModel会自动处理

    def deselect_all(self):
        """全不选所有文件"""
        self.beginResetModel()
        self.checked_files.clear()
        self.endResetModel()
        # 修复：不再手动触发dataChanged，beginResetModel/endResetModel会自动处理

    def select_by_group(self, hash_value, select=True):
        """按组选择文件"""
        self.beginResetModel()
        for item in self.display_items:
            if item['type'] == 'file' and item['hash'] == hash_value:
                if select:
                    self.checked_files.add(item['path'])
                else:
                    self.checked_files.discard(item['path'])
        self.endResetModel()
        # 修复：不再手动触发dataChanged，beginResetModel/endResetModel会自动处理

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
        # 修复：不再手动触发dataChanged，beginResetModel/endResetModel会自动处理

    def _format_file_size(self, size):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                if unit == 'B':
                    return f"{size:.0f} {unit}"
                else:
                    return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"