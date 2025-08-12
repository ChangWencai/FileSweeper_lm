#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
生成应用程序图标
"""

import os
from PIL import Image, ImageDraw, ImageFont
import math

def generate_icon():
    # 创建多种尺寸的图标
    sizes = [16, 32, 48, 64, 128, 256, 512]
    
    # 创建图像列表
    images = []
    
    for size in sizes:
        # 创建新图像
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 绘制背景圆圈
        draw.ellipse([0, 0, size-1, size-1], fill=(70, 130, 180, 255))  # 钢蓝色背景
        
        # 绘制文件夹形状
        folder_color = (255, 255, 255, 220)  # 半透明白色
        
        # 文件夹主体
        folder_width = size * 0.7
        folder_height = size * 0.5
        folder_x = (size - folder_width) / 2
        folder_y = (size - folder_height) / 2 - size * 0.1
        
        # 绘制文件夹顶部标签
        tab_width = folder_width * 0.4
        tab_height = folder_height * 0.3
        draw.rectangle([
            folder_x, folder_y,
            folder_x + tab_width, folder_y + tab_height
        ], fill=folder_color)
        
        # 绘制文件夹主体
        draw.rectangle([
            folder_x, folder_y + tab_height/2,
            folder_x + folder_width, folder_y + folder_height
        ], fill=folder_color)
        
        # 绘制表示重复文件的线条
        line_color = (70, 130, 180, 255)  # 深蓝色
        line_width = max(1, size // 16)
        line_y_offset = folder_y + folder_height * 0.7
        
        # 绘制三条平行线表示文件
        for i in range(3):
            line_y = line_y_offset + i * (size * 0.08)
            draw.line([
                (folder_x + size * 0.1, line_y),
                (folder_x + folder_width - size * 0.1, line_y)
            ], fill=line_color, width=line_width)
        
        images.append(img)
    
    # 获取项目根目录
    project_root = os.path.dirname(__file__)
    
    # 确保icons目录存在
    icons_dir = os.path.join(project_root, 'icons')
    if not os.path.exists(icons_dir):
        os.makedirs(icons_dir)
    
    # 保存为ICO文件 (Windows)
    if images:
        ico_path = os.path.join(icons_dir, 'icon.ico')
        images[0].save(
            ico_path,
            format='ICO',
            sizes=[(size, size) for size in sizes if size <= 256],
            append_images=images[1:]
        )
        print(f"Windows图标已生成: {ico_path}")
    else:
        print("图标生成失败")
        
    # 保存为ICNS文件 (macOS) - 实际上需要特殊处理，这里我们只保存PNG文件
    icns_sizes = [16, 32, 64, 128, 256, 512]
    for size in icns_sizes:
        png_path = os.path.join(icons_dir, f'icon_{size}x{size}.png')
        # 找到对应尺寸的图像
        img = None
        for image in images:
            if image.size[0] == size:
                img = image
                break
        # 如果没有找到对应尺寸，缩放最接近的图像
        if img is None:
            # 使用最大尺寸图像进行缩放
            img = images[-1].resize((size, size), Image.LANCZOS)
        img.save(png_path, format='PNG')
        print(f"macOS图标已生成: {png_path}")
        
    # 保存Linux图标 (PNG格式)
    # Linux通常使用不同尺寸的PNG文件
    linux_sizes = [16, 24, 32, 48, 64, 128, 256]
    for size in linux_sizes:
        png_path = os.path.join(icons_dir, f'icon_linux_{size}x{size}.png')
        # 找到对应尺寸的图像
        img = None
        for image in images:
            if image.size[0] == size:
                img = image
                break
        # 如果没有找到对应尺寸，缩放最接近的图像
        if img is None:
            # 使用最大尺寸图像进行缩放
            img = images[-1].resize((size, size), Image.LANCZOS)
        img.save(png_path, format='PNG')
        print(f"Linux图标已生成: {png_path}")

if __name__ == "__main__":
    generate_icon()