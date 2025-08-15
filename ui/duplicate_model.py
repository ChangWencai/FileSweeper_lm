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
        self.sort_column = -1  # 当前排序列
        self.sort_order = Qt.AscendingOrder  # 排序顺序
        
        # 筛选条件
        self.filter_text = ""
        self.min_size = 0
        self.max_size = 0
        self.filtered_items = []  # 筛选后的显示项目列表

    def sort_data(self, column):
        """根据指定列排序数据"""
        if column == self.CHECK_COLUMN:
            return  # 复选框列不排序
            
        self.beginResetModel()
        
        # 切换排序顺序
        if self.sort_column == column:
            self.sort_order = Qt.DescendingOrder if self.sort_order == Qt.AscendingOrder else Qt.AscendingOrder
        else:
            self.sort_column = column
            self.sort_order = Qt.AscendingOrder
            
        # 重新构建显示项目列表，按组处理
        sorted_items = []
        
        # 按哈希值分组
        groups = {}
        files = {}
        
        for item in self.display_items:
            if item['type'] == 'group':
                groups[item['hash']] = item
            else:
                if item['hash'] not in files:
                    files[item['hash']] = []
                files[item['hash']].append(item)
                
        # 对每组文件进行排序
        for hash_value, group_files in files.items():
            # 对组内文件排序
            sorted_files = sorted(group_files, key=lambda x: self._get_sort_key(x, column), reverse=(self.sort_order == Qt.DescendingOrder))
            
            # 添加组标题
            sorted_items.append(groups[hash_value])
            
            # 添加排序后的文件
            sorted_items.extend(sorted_files)
            
        self.display_items = sorted_items
        self.endResetModel()
        
    def _get_sort_key(self, item, column):
        """获取用于排序的键值"""
        if item['type'] != 'file':
            return ""
            
        file_path = item['path']
        
        if column == self.PATH_COLUMN:
            return file_path.lower()
        elif column == self.SIZE_COLUMN:
            try:
                return os.path.getsize(file_path)
            except:
                return 0
        elif column == self.MODIFIED_COLUMN:
            try:
                return os.path.getmtime(file_path)
            except:
                return 0
        else:
            return ""

    def rowCount(self, parent=QModelIndex()):
        """返回行数"""
        if self.filter_text or self.min_size > 0 or self.max_size < float('inf'):
            return len(self.filtered_items)
        return len(self.display_items)

    def columnCount(self, parent=QModelIndex()):
        """返回列数"""
        return self.COLUMN_COUNT

    def data(self, index, role=Qt.DisplayRole):
        """返回数据"""
        if self.filter_text or self.min_size > 0 or self.max_size < float('inf'):
            items = self.filtered_items
        else:
            items = self.display_items
            
        if not index.isValid() or index.row() >= len(items):
            return None

        item = items[index.row()]

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
            if index.column() == self.CHECK_COLUMN:
                # 复选框列
                if role == Qt.CheckStateRole:
                    return Qt.Checked if item['path'] in self.checked_files else Qt.Unchecked
                elif role == Qt.BackgroundRole and item['path'] in self.checked_files:
                    # 为选中的文件添加背景色
                    return QBrush(QColor(255, 200, 200, 100))  # 浅红色背景
            elif index.column() == self.PATH_COLUMN and role == Qt.DisplayRole:
                # 文件路径列
                return item['path']
            elif index.column() == self.SIZE_COLUMN and role == Qt.DisplayRole:
                # 文件大小列
                try:
                    size = os.path.getsize(item['path'])
                    return self._format_file_size(size)
                except:
                    return "未知"
            elif index.column() == self.MODIFIED_COLUMN and role == Qt.DisplayRole:
                # 修改时间列
                try:
                    mtime = os.path.getmtime(item['path'])
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
        if self.filter_text or self.min_size > 0 or self.max_size < float('inf'):
            items = self.filtered_items
        else:
            items = self.display_items
            
        if not index.isValid() or index.row() >= len(items):
            return Qt.NoItemFlags

        item = items[index.row()]

        # 组标题行
        if item['type'] == 'group':
            if index.column() == self.PATH_COLUMN:
                return Qt.ItemIsEnabled
            return Qt.NoItemFlags
            
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
            
            # 先收集所有文件项，避免在循环中频繁操作checked_files集合
            files_items = []
            for file_path in files:
                files_items.append({
                    'type': 'file',
                    'hash': hash_value,
                    'path': file_path
                })
                
                # 根据策略和设置决定是否选中文件（除了保留的文件）
                if self.auto_select_duplicates and file_path != keep_file:
                    self.checked_files.add(file_path)
                    
            # 批量添加文件项
            self.display_items.extend(files_items)
        
        # 应用当前筛选条件
        self.apply_filter(self.filter_text, self.min_size, self.max_size if self.max_size < float('inf') else 0)
        
        self.endResetModel()

    def get_file_info(self, row):
        """获取指定行的文件信息"""
        if self.filter_text or self.min_size > 0 or self.max_size < float('inf'):
            items = self.filtered_items
        else:
            items = self.display_items
            
        if 0 <= row < len(items):
            return items[row]
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

    def apply_filter(self, filter_text="", min_size=0, max_size=0):
        """应用筛选条件"""
        self.filter_text = filter_text.lower()
        self.min_size = min_size
        # 处理最大大小为0的情况（表示无限制）
        if max_size <= 0:
            self.max_size = float('inf')
        else:
            self.max_size = max_size
        
        # 重新构建筛选后的显示项目列表
        self.filtered_items = []
        
        # 应用筛选
        for item in self.display_items:
            if item['type'] == 'group':
                # 组标题总是显示
                self.filtered_items.append(item)
            else:
                # 筛选文件
                if self._matches_filter(item):
                    self.filtered_items.append(item)
        
        # 注意：这里不调用beginResetModel/endResetModel，因为这个方法是在update_data中调用的

    def _matches_filter(self, item):
        """检查文件是否匹配筛选条件"""
        file_path = item['path']
        try:
            file_size = os.path.getsize(file_path)
        except:
            file_size = 0
        
        # 检查文件路径是否包含筛选文本
        if self.filter_text and self.filter_text not in file_path.lower():
            return False
        
        # 检查文件大小是否在范围内
        if file_size < self.min_size or file_size > self.max_size:
            return False
        
        return True

    def _format_file_size(self, size):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} PB"
