#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：验证文件复制工具核心功能
"""

import os
import shutil
import sys

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from file_copy_tool import ConfigManager, DirectoryMatcher, IncrementalCopier

def test_file_copy():
    """测试文件复制功能"""
    print("=== 测试文件复制工具 ===")
    
    # 1. 准备测试数据
    print("\n1. 准备测试数据...")
    
    # 定义测试路径
    test_dir = os.path.join(os.getcwd(), "test")
    source_dir = os.path.join(test_dir, "source")
    target_dir = os.path.join(test_dir, "target")
    
    # 2. 测试配置管理
    print("\n2. 测试配置管理...")
    config_manager = ConfigManager("test_config.ini")
    
    # 更新配置
    config_manager.update_config(
        source_dir=source_dir,
        target_dir=target_dir,
        file_extension=".txt"
    )
    
    # 获取配置
    config = config_manager.get_config()
    print(f"配置已更新：{config}")
    
    # 验证配置
    is_valid, msg = config_manager.validate_config(config)
    print(f"配置验证：{is_valid} - {msg}")
    
    # 3. 测试目录遍历与匹配
    print("\n3. 测试目录遍历与匹配...")
    matcher = DirectoryMatcher(config["target_dir"])
    matcher.build_file_index()
    print(f"目标文件索引：{matcher.file_index}")
    
    match_results = matcher.match_files(config["source_dir"], config["file_extension"])
    print(f"匹配结果：{match_results}")
    
    # 4. 测试增量复制
    print("\n4. 测试增量复制...")
    copier = IncrementalCopier()
    copied_count, skipped_count = copier.copy_files(match_results)
    print(f"复制结果：成功 {copied_count} 个，跳过 {skipped_count} 个")
    print(f"操作日志：")
    for log in copier.logs:
        print(f"  {log}")
    
    # 5. 验证复制结果
    print("\n5. 验证复制结果...")
    
    # 检查文件是否已复制到目标位置
    for source_path, target_path in match_results:
        if os.path.exists(target_path):
            print(f"✓ 验证成功：{os.path.basename(source_path)} 已复制到 {os.path.dirname(target_path)}")
        else:
            print(f"✗ 验证失败：{os.path.basename(source_path)} 未复制到 {os.path.dirname(target_path)}")
    
    # 6. 测试重复复制（应该跳过）
    print("\n6. 测试重复复制...")
    copier2 = IncrementalCopier()
    copied_count2, skipped_count2 = copier2.copy_files(match_results)
    print(f"重复复制结果：成功 {copied_count2} 个，跳过 {skipped_count2} 个")
    print(f"操作日志：")
    for log in copier2.logs:
        print(f"  {log}")
    
    print("\n=== 测试完成 ===")
    
    # 清理测试配置文件
    if os.path.exists("test_config.ini"):
        os.remove("test_config.ini")

if __name__ == "__main__":
    test_file_copy()
