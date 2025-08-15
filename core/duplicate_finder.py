#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
性能优化器模块
"""

import os
import hashlib
import mmap
import json
import time
import tempfile
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor


class PerformanceOptimizer:
    """性能优化器类，用于优化重复文件查找过程"""
    
    def __init__(self):
        """初始化性能优化器"""
        self.hash_cache = {}
        self.cache_file = os.path.join(tempfile.gettempdir(), 'filesweeper_hash_cache.json')
        self.config = {
            'cache_enabled': True,          # 是否启用缓存
            'use_mmap_threshold': 1024*1024*1024,  # 使用内存映射的文件大小阈值
            'max_cache_items': 1000         # 缓存最大条目数
        }
        
        self.load_cache()
    
    def update_config(self, **kwargs):
        """更新配置"""
        self.config.update(kwargs)
    
    def find_duplicates_parallel(self, files, fast_scan_mode=False, fast_scan_size=4, 
                              use_multiprocessing=False, progress_callback=None):
        """
        并行查找重复文件
        
        Args:
            files: 文件列表
            fast_scan_mode: 快速扫描模式
            fast_scan_size: 快速扫描大小(MB)
            use_multiprocessing: 是否使用多进程
            progress_callback: 进度回调函数
            
        Returns:
            包含重复文件的字典
        """
        # 第一阶段：按大小分组
        size_groups = defaultdict(list)
        total_files = len(files)
        
        for i, filepath in enumerate(files):
            if not os.path.isfile(filepath):
                continue
                
            try:
                size = os.path.getsize(filepath)
                size_groups[size].append(filepath)
                
                if progress_callback:
                    progress = int((i + 1) / total_files * 30)  # 前30%用于按大小分组
                    progress_callback(progress, f"正在分析文件大小: {filepath}")
            except Exception as e:
                print(f"Error getting file size for {filepath}: {e}")
                continue
        
        # 第二阶段：并行计算哈希
        duplicates = defaultdict(list)
        if use_multiprocessing and len(size_groups) > 0:
            with ProcessPoolExecutor(max_workers=self._get_optimal_worker_count()) as executor:
                futures = []
                for size, file_group in size_groups.items():
                    if len(file_group) <= 1:
                        continue
                        
                    future = executor.submit(
                        self._process_hash_group, 
                        file_group, 
                        fast_scan_mode,
                        fast_scan_size
                    )
                    futures.append((future, file_group))
                
                for idx, (future, file_group) in enumerate(futures):
                    try:
                        result = future.result()
                        if result:
                            hash_value, hash_files = result
                            if len(hash_files) > 1:
                                duplicates[hash_value] = hash_files
                    except Exception as e:
                        print(f"Error processing hash group: {e}")
                    
                    if progress_callback:
                        progress = 30 + int((idx + 1) / len(futures) * 60)  # 中间60%用于哈希计算
                        progress_callback(min(progress, 90), f"正在计算文件哈希: {len(file_group)} 个文件")
        
        # 第三阶段：保存缓存
        self.save_cache()
        
        return dict(duplicates)
    
    def _process_hash_group(self, files, fast_scan_mode, fast_scan_size):
        """
        处理单个文件组的哈希计算
        
        Args:
            files: 文件列表
            fast_scan_mode: 快速扫描模式
            fast_scan_size: 快速扫描大小(MB)
            
        Returns:
            (hash_value, files) 元组
        """
        hash_files = []
        
        for filepath in files:
            file_hash = self._calculate_file_hash(
                filepath, 
                fast_scan_mode, 
                fast_scan_size
            )
            
            if file_hash:
                hash_files.append(filepath)
        
        return (hash_files[0], hash_files) if hash_files else None
    
    def _calculate_file_hash(self, filepath, fast_scan_mode, fast_scan_size):
        """
        计算文件哈希值
        
        Args:
            filepath: 文件路径
            fast_scan_mode: 快速扫描模式
            fast_scan_size: 快速扫描大小(MB)
            
        Returns:
            文件哈希值或None
        """
        try:
            file_size = os.path.getsize(filepath)
            file_mtime = os.path.getmtime(filepath)
            
            # 检查缓存
            if self.config['cache_enabled']:
                cache_key = f"{file_size}_{file_mtime}"
                if cache_key in self.hash_cache:
                    cached_data = self.hash_cache[cache_key]
                    if cached_data.get('filepath') == filepath:
                        return cached_data['hash']
            
            hash_md5 = hashlib.md5()
            
            # 快速扫描模式 - 只读取文件前部分
            if fast_scan_mode and file_size > fast_scan_size * 1024 * 1024:
                read_size = fast_scan_size * 1024 * 1024
            else:
                read_size = file_size
                
            # 使用内存映射处理大文件
            if file_size > self.config['use_mmap_threshold']:
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
            if self.config['cache_enabled']:
                cache_key = f"{file_size}_{file_mtime}"
                self.hash_cache[cache_key] = {
                    'filepath': filepath,
                    'hash': file_hash,
                    'timestamp': time.time()
                }
                
                # 限制缓存大小
                if len(self.hash_cache) > self.config['max_cache_items']:
                    # 移除最旧的项
                    sorted_items = sorted(self.hash_cache.items(), 
                                        key=lambda x: x[1]['timestamp'])
                    self.hash_cache = dict(sorted_items[-self.config['max_cache_items']:])
            
            return file_hash
        except Exception as e:
            print(f"Error calculating hash for {filepath}: {e}")
            return None
    
    def load_cache(self):
        """加载哈希缓存"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.hash_cache = json.load(f)
        except Exception as e:
            print(f"Error loading hash cache: {e}")
            self.hash_cache = {}
    
    def save_cache(self):
        """保存哈希缓存"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.hash_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving hash cache: {e}")
    
    def _get_optimal_worker_count(self):
        """获取最佳工作进程数"""
        import multiprocessing
        return multiprocessing.cpu_count()  # 使用所有可用CPU核心
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
重复文件查找器
"""

import os
import hashlib
import mmap
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from PySide6.QtCore import QObject, Signal, QThread
try:
    from core.performance_optimizer import PerformanceOptimizer
    optimizer_available = True
except ImportError:
    optimizer_available = False


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
        
        # 初始化性能优化器
        self.optimizer = PerformanceOptimizer() if optimizer_available else None

    def set_optimization_settings(self, fast_scan_mode, fast_scan_size, use_multiprocessing, use_mmap, cache_hashes):
        """设置优化选项"""
        self.fast_scan_mode = fast_scan_mode
        self.fast_scan_size = fast_scan_size
        self.use_multiprocessing = use_multiprocessing
        self.use_mmap = use_mmap
        self.cache_hashes = cache_hashes
        
        # 更新性能优化器配置
        if self.optimizer:
            self.optimizer.update_config(
                cache_enabled=cache_hashes,
                use_mmap_threshold=1024*1024*1024 if use_mmap else float('inf')
            )

    def run(self):
        """线程执行函数"""
        try:
            self.find_started.emit()
            
            # 如果有性能优化器，使用新的并行处理方法
            if self.optimizer:
                duplicates = self.optimizer.find_duplicates_parallel(
                    self.files,
                    fast_scan_mode=self.fast_scan_mode,
                    fast_scan_size=self.fast_scan_size,
                    use_multiprocessing=self.use_multiprocessing,
                    progress_callback=self._progress_callback
                )
                
                # 保存哈希缓存
                if self.cache_hashes:
                    self.optimizer.save_cache()
                
                if not self._stop_flag:
                    self.find_finished.emit(duplicates)
            else:
                # 回退到原有实现
                self._legacy_run()
        except Exception as e:
            # 保存哈希缓存（即使出错也要保存）
            if self.cache_hashes and self.optimizer:
                self.optimizer.save_cache()
            self.find_error.emit(str(e))

    def stop(self):
        """停止查找"""
        self._stop_flag = True
        
    def _progress_callback(self, progress, message):
        """进度回调函数"""
        if not self._stop_flag:
            self.find_progress.emit(progress, message)
            
    def set_optimization_settings(self, fast_scan_mode, fast_scan_size, use_multiprocessing, use_mmap, cache_hashes):
        """设置优化选项"""
        self.fast_scan_mode = fast_scan_mode
        self.fast_scan_size = fast_scan_size
        self.use_multiprocessing = use_multiprocessing
        self.use_mmap = use_mmap
        self.cache_hashes = cache_hashes


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