#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
重复文件查找器
"""

import os
import hashlib
import mmap
import json
import time
import tempfile
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from PySide6.QtCore import QObject, Signal, QThread


# 全局哈希缓存
_hash_cache = {}
_cache_file = os.path.join(tempfile.gettempdir(), 'filesweeper_hash_cache.json')


def load_hash_cache():
    """加载哈希缓存"""
    global _hash_cache
    try:
        if os.path.exists(_cache_file):
            with open(_cache_file, 'r', encoding='utf-8') as f:
                _hash_cache = json.load(f)
    except:
        _hash_cache = {}


def save_hash_cache():
    """保存哈希缓存"""
    try:
        # 只保留最近的1000个缓存项
        if len(_hash_cache) > 1000:
            # 移除最旧的项
            keys = list(_hash_cache.keys())
            for key in keys[:len(keys) - 1000]:
                del _hash_cache[key]
                
        with open(_cache_file, 'w', encoding='utf-8') as f:
            json.dump(_hash_cache, f, ensure_ascii=False, indent=2)
    except:
        pass


def calculate_file_hash(filepath, fast_scan_mode=False, fast_scan_size=4, use_mmap=False):
    """计算文件哈希值的独立函数，用于多进程处理"""
    try:
        file_size = os.path.getsize(filepath)
        file_mtime = os.path.getmtime(filepath)
        
        # 检查缓存
        cache_key = f"{file_size}_{file_mtime}"
        if cache_key in _hash_cache:
            cached_data = _hash_cache[cache_key]
            # 验证缓存是否仍然有效
            if cached_data.get('filepath') == filepath:
                return cached_data['hash']
        
        hash_md5 = hashlib.md5()
        
        # 快速扫描模式 - 只读取文件前部分
        if fast_scan_mode and file_size > fast_scan_size * 1024 * 1024:
            read_size = fast_scan_size * 1024 * 1024
        else:
            read_size = file_size
            
        # 对于极大文件（>1GB）使用内存映射
        if use_mmap and file_size > 1024 * 1024 * 1024:
            with open(filepath, 'rb') as f:
                mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
                hash_md5.update(mm[:read_size])
                mm.close()
        else:
            with open(filepath, 'rb') as f:
                remaining = read_size
                while remaining > 0:
                    chunk_size = min(65536, remaining)
                    data = f.read(chunk_size)
                    if not data:
                        break
                    hash_md5.update(data)
                    remaining -= len(data)
        
        file_hash = hash_md5.hexdigest()
        
        # 保存到缓存
        _hash_cache[cache_key] = {
            'filepath': filepath,
            'hash': file_hash,
            'timestamp': time.time()
        }
        
        return file_hash
    except:
        return None


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
        
        # 优化设置
        self.fast_scan_mode = False
        self.fast_scan_size = 4  # MB
        self.use_multiprocessing = False
        self.use_mmap = True
        self.cache_hashes = True
        
        # 加载哈希缓存
        if self.cache_hashes:
            load_hash_cache()

    def set_optimization_settings(self, fast_scan_mode, fast_scan_size, use_multiprocessing, use_mmap, cache_hashes):
        """设置优化选项"""
        self.fast_scan_mode = fast_scan_mode
        self.fast_scan_size = fast_scan_size
        self.use_multiprocessing = use_multiprocessing
        self.use_mmap = use_mmap
        self.cache_hashes = cache_hashes

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
                    
                    # 使用多线程/多进程计算哈希值
                    if self.use_multiprocessing and len(files) > 2:
                        # 对于大量文件使用多进程
                        with ProcessPoolExecutor(max_workers=4) as executor:
                            futures = []
                            for filepath in files:
                                if self._stop_flag:
                                    break
                                future = executor.submit(
                                    calculate_file_hash, 
                                    filepath, 
                                    self.fast_scan_mode, 
                                    self.fast_scan_size,
                                    self.use_mmap
                                )
                                futures.append((future, filepath))
                            
                            for future, filepath in futures:
                                if self._stop_flag:
                                    break
                                try:
                                    file_hash = future.result()
                                    if file_hash:
                                        hash_groups[file_hash].append(filepath)
                                except:
                                    continue
                    else:
                        # 使用单线程计算哈希值
                        for filepath in files:
                            if self._stop_flag:
                                break
                                
                            try:
                                file_hash = calculate_file_hash(
                                    filepath, 
                                    self.fast_scan_mode, 
                                    self.fast_scan_size,
                                    self.use_mmap
                                )
                                if file_hash:
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
            
            # 保存哈希缓存
            if self.cache_hashes:
                save_hash_cache()
            
            if not self._stop_flag:
                self.find_finished.emit(duplicates)
        except Exception as e:
            # 保存哈希缓存（即使出错也要保存）
            if self.cache_hashes:
                save_hash_cache()
            self.find_error.emit(str(e))

    def stop(self):
        """停止查找"""
        self._stop_flag = True

    def _calculate_hash(self, filepath):
        """计算文件的MD5哈希值（保持兼容性）"""
        return calculate_file_hash(filepath, self.fast_scan_mode, self.fast_scan_size, self.use_mmap)


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
        # 优化设置
        self.fast_scan_mode = False
        self.fast_scan_size = 4  # MB
        self.use_multiprocessing = False
        self.use_mmap = True
        self.cache_hashes = True

    def start_find(self, files):
        """开始查找重复文件"""
        # 如果已有查找线程在运行，则先停止
        if self.find_thread and self.find_thread.isRunning():
            self.stop_find()
            
        # 创建新的查找线程
        self.find_thread = DuplicateFinderThread(files)
        
        # 设置优化选项
        self.find_thread.set_optimization_settings(
            self.fast_scan_mode,
            self.fast_scan_size,
            self.use_multiprocessing,
            self.use_mmap,
            self.cache_hashes
        )
        
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
            
    def set_optimization_settings(self, fast_scan_mode, fast_scan_size, use_multiprocessing, use_mmap, cache_hashes):
        """设置优化选项"""
        self.fast_scan_mode = fast_scan_mode
        self.fast_scan_size = fast_scan_size
        self.use_multiprocessing = use_multiprocessing
        self.use_mmap = use_mmap
        self.cache_hashes = cache_hashes