#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
重复文件查找器
"""

import os
import hashlib
from collections import defaultdict
from PySide6.QtCore import QObject, Signal, QThread


class DuplicateFinderThread(QThread):
    """查找重复文件线程类"""
    # 定义信号
    find_started = Signal()
    find_progress = Signal(int, str)  # 进度百分比和消息
    find_finished = Signal(dict)      # 查找完成，传递重复文件字典
    find_error = Signal(str)          # 查找出错，传递错误消息

    def __init__(self, files):
        super().__init__()
        self.files = files
        self._stop_flag = False

    def run(self):
        """线程执行函数"""
        try:
            self.find_started.emit()
            
            # 按文件大小分组
            size_groups = defaultdict(list)
            total_files = len(self.files)
            
            for i, filepath in enumerate(self.files):
                if self._stop_flag:
                    break
                    
                try:
                    size = os.path.getsize(filepath)
                    size_groups[size].append(filepath)
                    
                    progress = int((i + 1) / total_files * 50)  # 前50%用于按大小分组
                    self.find_progress.emit(progress, f"正在分析文件大小: {filepath}")
                except:
                    continue
            
            # 查找重复文件（相同大小的文件进一步比较哈希值）
            duplicates = defaultdict(list)
            group_count = len([group for group in size_groups.values() if len(group) > 1])
            processed_groups = 0
            
            for size, files in size_groups.items():
                if self._stop_flag:
                    break
                    
                # 只有相同大小的文件超过1个才需要进一步比较
                if len(files) > 1:
                    hash_groups = defaultdict(list)
                    
                    for filepath in files:
                        if self._stop_flag:
                            break
                            
                        try:
                            file_hash = self._calculate_hash(filepath)
                            hash_groups[file_hash].append(filepath)
                        except:
                            continue
                    
                    # 将哈希值相同的文件（真正的重复文件）添加到结果中
                    for file_hash, hash_files in hash_groups.items():
                        if len(hash_files) > 1:
                            duplicates[file_hash] = hash_files
                    
                    processed_groups += 1
                    progress = int(50 + (processed_groups / group_count * 50)) if group_count > 0 else 100
                    self.find_progress.emit(progress, f"正在比较文件内容: {len(files)} 个相同大小的文件")
            
            if not self._stop_flag:
                self.find_finished.emit(duplicates)
        except Exception as e:
            self.find_error.emit(str(e))

    def stop(self):
        """停止查找"""
        self._stop_flag = True

    def _calculate_hash(self, filepath, block_size=65536):
        """计算文件的MD5哈希值"""
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for block in iter(lambda: f.read(block_size), b""):
                hash_md5.update(block)
        return hash_md5.hexdigest()


class DuplicateFinder(QObject):
    """重复文件查找器类"""
    # 定义信号
    find_started = Signal()
    find_progress = Signal(int, str)  # 进度百分比和消息
    find_finished = Signal(dict)      # 查找完成，传递重复文件字典
    find_error = Signal(str)          # 查找出错，传递错误消息

    def __init__(self):
        super().__init__()
        self.find_thread = None

    def start_find(self, files):
        """开始查找重复文件"""
        # 如果已有查找线程在运行，则先停止
        if self.find_thread and self.find_thread.isRunning():
            self.stop_find()
            
        # 创建新的查找线程
        self.find_thread = DuplicateFinderThread(files)
        
        # 连接信号
        self.find_thread.find_started.connect(self.find_started)
        self.find_thread.find_progress.connect(self.find_progress)
        self.find_thread.find_finished.connect(self.find_finished)
        self.find_thread.find_error.connect(self.find_error)
        
        # 启动线程
        self.find_thread.start()

    def stop_find(self):
        """停止查找"""
        if self.find_thread and self.find_thread.isRunning():
            self.find_thread.stop()
            self.find_thread.wait()