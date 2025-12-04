#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件复制工具
功能：按文件名（不含后缀）一致规则，将指定文件夹内特定后缀文件，复制到目标文件夹对应子文件夹
"""

import os
import shutil
import configparser
import sys
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

class ConfigManager:
    """配置管理模块"""
    def __init__(self, config_file='config.ini'):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self._init_config()
    
    def _init_config(self):
        """初始化配置文件"""
        if not os.path.exists(self.config_file):
            self._create_default_config()
        self.config.read(self.config_file, encoding='utf-8')
    
    def _create_default_config(self):
        """创建默认配置文件"""
        self.config['DEFAULT'] = {
            'source_dir': '',
            'target_dir': '',
            'file_extension': ''
        }
        with open(self.config_file, 'w', encoding='utf-8') as f:
            self.config.write(f)
    
    def get_config(self):
        """获取配置"""
        return {
            'source_dir': self.config['DEFAULT']['source_dir'],
            'target_dir': self.config['DEFAULT']['target_dir'],
            'file_extension': self.config['DEFAULT']['file_extension']
        }
    
    def update_config(self, source_dir=None, target_dir=None, file_extension=None):
        """更新配置"""
        if source_dir is not None:
            self.config['DEFAULT']['source_dir'] = source_dir
        if target_dir is not None:
            self.config['DEFAULT']['target_dir'] = target_dir
        if file_extension is not None:
            self.config['DEFAULT']['file_extension'] = file_extension
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            self.config.write(f)
    
    def validate_config(self, config):
        """验证配置有效性"""
        if not config['source_dir'] or not os.path.isdir(config['source_dir']):
            return False, "源目录无效"
        if not config['target_dir'] or not os.path.isdir(config['target_dir']):
            return False, "目标目录无效"
        if not config['file_extension']:
            return False, "文件后缀不能为空"
        return True, "配置有效"

class DirectoryMatcher:
    """目录遍历与匹配模块"""
    def __init__(self, target_dir):
        self.target_dir = target_dir
        self.file_index = {}
    
    def build_file_index(self):
        """构建目标文件夹文件索引"""
        for root, dirs, files in os.walk(self.target_dir):
            for file in files:
                # 获取无后缀文件名
                file_name_without_ext = os.path.splitext(file)[0]
                # 保存文件路径
                self.file_index[file_name_without_ext] = root
    
    def match_files(self, source_dir, file_extension):
        """匹配源文件与目标路径"""
        match_results = []
        
        # 遍历源目录
        for file in os.listdir(source_dir):
            # 检查文件后缀
            if file.endswith(file_extension):
                # 获取无后缀文件名
                file_name_without_ext = os.path.splitext(file)[0]
                # 查找匹配的目标路径
                if file_name_without_ext in self.file_index:
                    source_path = os.path.join(source_dir, file)
                    target_path = os.path.join(self.file_index[file_name_without_ext], file)
                    match_results.append((source_path, target_path))
        
        return match_results

class IncrementalCopier:
    """增量复制模块"""
    def __init__(self):
        self.logs = []
    
    def copy_files(self, match_results):
        """增量复制文件"""
        copied_count = 0
        skipped_count = 0
        
        for source_path, target_path in match_results:
            # 检查目标文件是否已存在
            if os.path.exists(target_path):
                # 文件已存在，跳过
                log = f"跳过：{os.path.basename(source_path)} 已存在于 {os.path.dirname(target_path)}"
                self.logs.append(log)
                skipped_count += 1
            else:
                # 文件不存在，执行复制
                try:
                    shutil.copy2(source_path, target_path)
                    log = f"复制成功：{os.path.basename(source_path)} -> {os.path.dirname(target_path)}"
                    self.logs.append(log)
                    copied_count += 1
                except Exception as e:
                    log = f"复制失败：{os.path.basename(source_path)} -> {os.path.dirname(target_path)}，错误：{str(e)}"
                    self.logs.append(log)
        
        return copied_count, skipped_count
    
    def save_logs(self, log_file='copy_log.txt'):
        """保存操作日志"""
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*50}\n")
            f.write(f"操作时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            for log in self.logs:
                f.write(f"{log}\n")

class MainController:
    """主控制模块"""
    def __init__(self):
        self.config_manager = ConfigManager()
    
    def run(self):
        """主程序入口"""
        while True:
            print("\n=== 文件复制工具 ===")
            print("1. 查看当前配置")
            print("2. 修改配置")
            print("3. 执行文件复制")
            print("4. 退出")
            
            choice = input("请输入选择（1-4）：")
            
            if choice == '1':
                self._show_config()
            elif choice == '2':
                self._modify_config()
            elif choice == '3':
                self._execute_copy()
            elif choice == '4':
                print("感谢使用，再见！")
                break
            else:
                print("无效选择，请重新输入！")
    
    def _show_config(self):
        """显示当前配置"""
        config = self.config_manager.get_config()
        print("\n当前配置：")
        print(f"源目录：{config['source_dir']}")
        print(f"目标目录：{config['target_dir']}")
        print(f"文件后缀：{config['file_extension']}")
    
    def _modify_config(self):
        """修改配置"""
        current_config = self.config_manager.get_config()
        
        print("\n修改配置（直接回车保持当前值）：")
        source_dir = input(f"源目录 [{current_config['source_dir']}]：").strip() or current_config['source_dir']
        target_dir = input(f"目标目录 [{current_config['target_dir']}]：").strip() or current_config['target_dir']
        file_extension = input(f"文件后缀 [{current_config['file_extension']}]：").strip() or current_config['file_extension']
        
        # 更新配置
        self.config_manager.update_config(source_dir, target_dir, file_extension)
        print("配置已更新！")
    
    def _execute_copy(self):
        """执行文件复制"""
        # 获取配置
        config = self.config_manager.get_config()
        
        # 验证配置
        is_valid, msg = self.config_manager.validate_config(config)
        if not is_valid:
            print(f"\n配置错误：{msg}")
            print("请先修改配置！")
            return
        
        print("\n开始执行文件复制...")
        
        # 1. 构建目标文件索引
        print("正在构建目标文件索引...")
        matcher = DirectoryMatcher(config['target_dir'])
        matcher.build_file_index()
        print(f"共索引到 {len(matcher.file_index)} 个文件")
        
        # 2. 匹配源文件
        print("正在匹配源文件...")
        match_results = matcher.match_files(config['source_dir'], config['file_extension'])
        print(f"共匹配到 {len(match_results)} 个文件")
        
        if not match_results:
            print("没有找到匹配的文件，无需复制！")
            return
        
        # 3. 执行增量复制
        print("正在执行增量复制...")
        copier = IncrementalCopier()
        copied_count, skipped_count = copier.copy_files(match_results)
        
        # 4. 保存日志
        copier.save_logs()
        
        # 5. 输出结果
        print("\n复制完成！")
        print(f"成功复制：{copied_count} 个文件")
        print(f"跳过已存在：{skipped_count} 个文件")
        print(f"日志已保存到 copy_log.txt")

class GUIController:
    """图形界面控制模块"""
    def __init__(self):
        self.config_manager = ConfigManager()
        self.root = tk.Tk()
        self.root.title("文件复制工具")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # 初始化界面
        self._init_ui()
        # 加载配置
        self._load_config()
    
    def _init_ui(self):
        """初始化界面"""
        # 创建主框架
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 配置区域
        config_frame = tk.LabelFrame(main_frame, text="配置信息", padx=10, pady=10)
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 源目录
        tk.Label(config_frame, text="源目录：").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.source_dir_var = tk.StringVar()
        self.source_dir_entry = tk.Entry(config_frame, textvariable=self.source_dir_var, width=50)
        self.source_dir_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(config_frame, text="浏览", command=self._browse_source_dir).grid(row=0, column=2, padx=5, pady=5)
        
        # 目标目录
        tk.Label(config_frame, text="目标目录：").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.target_dir_var = tk.StringVar()
        self.target_dir_entry = tk.Entry(config_frame, textvariable=self.target_dir_var, width=50)
        self.target_dir_entry.grid(row=1, column=1, padx=5, pady=5)
        tk.Button(config_frame, text="浏览", command=self._browse_target_dir).grid(row=1, column=2, padx=5, pady=5)
        
        # 文件后缀
        tk.Label(config_frame, text="文件后缀：").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.file_ext_var = tk.StringVar()
        self.file_ext_entry = tk.Entry(config_frame, textvariable=self.file_ext_var, width=10)
        self.file_ext_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        # 操作按钮区域
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Button(button_frame, text="保存配置", command=self._save_config, width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="执行复制", command=self._execute_copy, width=15, bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="清空日志", command=self._clear_log, width=15).pack(side=tk.LEFT, padx=5)
        
        # 日志显示区域
        log_frame = tk.LabelFrame(main_frame, text="操作日志", padx=10, pady=10)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)
    
    def _browse_source_dir(self):
        """浏览源目录"""
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.source_dir_var.set(dir_path)
    
    def _browse_target_dir(self):
        """浏览目标目录"""
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.target_dir_var.set(dir_path)
    
    def _load_config(self):
        """加载配置"""
        config = self.config_manager.get_config()
        self.source_dir_var.set(config['source_dir'])
        self.target_dir_var.set(config['target_dir'])
        self.file_ext_var.set(config['file_extension'])
    
    def _save_config(self):
        """保存配置"""
        source_dir = self.source_dir_var.get().strip()
        target_dir = self.target_dir_var.get().strip()
        file_ext = self.file_ext_var.get().strip()
        
        # 验证配置
        config = {'source_dir': source_dir, 'target_dir': target_dir, 'file_extension': file_ext}
        is_valid, msg = self.config_manager.validate_config(config)
        
        if is_valid:
            self.config_manager.update_config(source_dir, target_dir, file_ext)
            messagebox.showinfo("成功", "配置已保存！")
        else:
            messagebox.showerror("错误", f"配置无效：{msg}")
    
    def _execute_copy(self):
        """执行文件复制"""
        # 获取配置
        source_dir = self.source_dir_var.get().strip()
        target_dir = self.target_dir_var.get().strip()
        file_ext = self.file_ext_var.get().strip()
        
        # 验证配置
        config = {'source_dir': source_dir, 'target_dir': target_dir, 'file_extension': file_ext}
        is_valid, msg = self.config_manager.validate_config(config)
        
        if not is_valid:
            messagebox.showerror("错误", f"配置无效：{msg}")
            return
        
        # 更新配置
        self.config_manager.update_config(source_dir, target_dir, file_ext)
        
        # 显示开始信息
        self._add_log("开始执行文件复制...")
        self.root.update()
        
        try:
            # 1. 构建目标文件索引
            self._add_log("正在构建目标文件索引...")
            self.root.update()
            
            matcher = DirectoryMatcher(target_dir)
            matcher.build_file_index()
            self._add_log(f"共索引到 {len(matcher.file_index)} 个文件")
            self.root.update()
            
            # 2. 匹配源文件
            self._add_log("正在匹配源文件...")
            self.root.update()
            
            match_results = matcher.match_files(source_dir, file_ext)
            self._add_log(f"共匹配到 {len(match_results)} 个文件")
            self.root.update()
            
            if not match_results:
                self._add_log("没有找到匹配的文件，无需复制！")
                messagebox.showinfo("提示", "没有找到匹配的文件，无需复制！")
                return
            
            # 3. 执行增量复制
            self._add_log("正在执行增量复制...")
            self.root.update()
            
            copier = IncrementalCopier()
            copied_count, skipped_count = copier.copy_files(match_results)
            
            # 添加复制结果到日志
            for log in copier.logs:
                self._add_log(log)
            
            # 4. 保存日志
            copier.save_logs()
            
            # 5. 显示结果
            result_msg = f"复制完成！\n成功复制：{copied_count} 个文件\n跳过已存在：{skipped_count} 个文件\n日志已保存到 copy_log.txt"
            self._add_log(result_msg)
            messagebox.showinfo("成功", result_msg)
            
        except Exception as e:
            error_msg = f"复制过程中发生错误：{str(e)}"
            self._add_log(error_msg)
            messagebox.showerror("错误", error_msg)
    
    def _add_log(self, message):
        """添加日志信息"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def _clear_log(self):
        """清空日志"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def run(self):
        """运行图形界面"""
        self.root.mainloop()

def main():
    """主程序入口"""
    # 如果没有命令行参数，运行图形界面
    if len(sys.argv) == 1:
        try:
            gui_controller = GUIController()
            gui_controller.run()
        except Exception as e:
            print(f"图形界面启动失败：{str(e)}")
            print("正在启动命令行界面...")
            controller = MainController()
            controller.run()
    else:
        # 有命令行参数，运行命令行界面
        controller = MainController()
        controller.run()

if __name__ == "__main__":
    main()
