#!/usr/bin/env python3
"""
TikTok Downloader - 一键打包脚本
将 main_notion_monitor.py 打包成可执行文件

使用方法:
    python build.py

输出:
    dist/notion_monitor.exe - 可执行文件
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_environment():
    """检查环境"""
    print("检查环境...")
    
    # 检查入口文件
    if not os.path.exists('main_notion_monitor.py'):
        print("❌ 找不到 main_notion_monitor.py")
        return False
    
    # 检查 Poetry 项目
    if not os.path.exists('pyproject.toml'):
        print("❌ 找不到 pyproject.toml")
        return False
    
    # 检查 Poetry 命令
    try:
        result = subprocess.run(['poetry', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Poetry: {result.stdout.strip()}")
        else:
            print("❌ Poetry 不可用")
            return False
    except FileNotFoundError:
        print("❌ 找不到 Poetry 命令")
        return False
    
    # 检查 notion_base 包
    try:
        result = subprocess.run([
            'poetry', 'run', 'python', '-c', 
            'import notion_base; from notion_base import get_database; print("OK")'
        ], capture_output=True, text=True, check=True)
        print("✅ notion_base 包正常")
    except subprocess.CalledProcessError:
        print("❌ notion_base 包有问题，请运行: poetry install")
        return False
    
    return True

def install_pyinstaller():
    """安装 PyInstaller"""
    print("安装 PyInstaller...")
    try:
        # 检查是否已安装
        result = subprocess.run(['poetry', 'run', 'python', '-c', 'import PyInstaller'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ PyInstaller 已安装")
            return True
        
        # 安装 PyInstaller
        subprocess.run(['poetry', 'run', 'pip', 'install', 'pyinstaller'], 
                      capture_output=True, text=True, check=True)
        print("✅ PyInstaller 安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ PyInstaller 安装失败: {e}")
        return False

def create_spec_file():
    """创建 PyInstaller 配置文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

hiddenimports = [
    # Notion 相关
    'notion_base',
    'notion_base.database',
    'notion_base.client',
    'notion_base.config',
    'notion_base.main',
    'notion_base.page_meta',
    'notion_base.pages',
    'notion_base.pages.project',
    'notion_base.pages.task',
    'notion_base.pages.post_schedule',
    'notion_client',
    'notion_client.client',
    
    # 异步相关
    'asyncio',
    'concurrent.futures',
    
    # HTTP 客户端
    'aiohttp',
    'aiohttp.client',
    'aiohttp.connector',
    'requests',
    
    # 数据库
    'motor',
    'pymongo',
    
    # 通知
    'slack_sdk',
    'slack_sdk.web',
    'slack_sdk.web.client',
    
    # 数据处理
    'pandas',
    'numpy',
    'openpyxl',
    
    # 其他
    'pytz',
    'emoji',
    'qrcode',
    'lxml',
    
    # 本地模块
    'PostMonitor',
    'PostMonitor.NotionDouyinPostMonitor',
    'PostMonitor.SingleUserNewPostMonitor',
    'PostMonitor.DouyinPostPage',
    'PostMonitor.douyin_post_service',
    'PostMonitor.new_video_notification',
    
    'DouyinEndpoints',
    'DouyinEndpoints.Posts',
    'DouyinEndpoints.Posts.UserPostVideos',
    'DouyinEndpoints.Posts.UserPostPrivateApi',
    'DouyinEndpoints.Posts.UserPostRequest',
    
    'StudioY',
    'StudioY.FavoriteVideoDto',
    'StudioY.DouyinSession',
    'StudioY.StudioYClient',
    
    'Slack',
    'Slack.SlackDouyinMonitor',
    
    'NotionServices',
    'NotionServices.douyin_account_service',
    'NotionServices.douyin_post_service',
    
    'FileDownload',
    'FileDownload.DouyinFileDownloadServiceClient',
    
    'Parameter',
]

a = Analysis(
    ['main_notion_monitor.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='notion_monitor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    cofile=None,
    icon=None,
)
'''
    
    with open('build.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ 创建配置文件: build.spec")

def build_executable():
    """构建可执行文件"""
    print("开始构建可执行文件...")
    
    try:
        cmd = ['poetry', 'run', 'pyinstaller', '--clean', 'build.spec']
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            exe_path = Path('dist/notion_monitor.exe')
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"✅ 构建成功!")
                print(f"   文件: {exe_path.absolute()}")
                print(f"   大小: {size_mb:.1f} MB")
                return True
            else:
                print("❌ 构建失败: 找不到输出文件")
                return False
        else:
            print("❌ 构建失败!")
            if result.stderr:
                print(f"错误: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 构建异常: {e}")
        return False

def cleanup():
    """清理临时文件"""
    print("清理临时文件...")
    
    # 清理目录
    for dir_name in ['build', '__pycache__']:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
    
    # 清理文件
    for file_name in ['build.spec']:
        if os.path.exists(file_name):
            os.remove(file_name)
    
    print("✅ 清理完成")

def main():
    """主函数"""
    print("=" * 50)
    print("TikTok Downloader - 一键打包工具")
    print("=" * 50)
    
    # 检查环境
    if not check_environment():
        print("\n❌ 环境检查失败")
        return False
    
    # 安装 PyInstaller
    if not install_pyinstaller():
        print("\n❌ PyInstaller 安装失败")
        return False
    
    # 清理旧文件
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')
    
    # 创建配置
    create_spec_file()
    
    # 构建
    if not build_executable():
        print("\n❌ 构建失败")
        return False
    
    # 清理
    cleanup()
    
    print("\n" + "=" * 50)
    print("🎉 打包完成!")
    print("=" * 50)
    print("运行程序: dist/notion_monitor.exe")
    print("注意: 确保目标机器有网络连接和正确配置")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
