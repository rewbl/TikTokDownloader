# 基于Notion的抖音视频监控系统

## 概述

这是一个基于Notion数据库的抖音视频监控系统，可以自动监控67个指定账号的新视频发布，并将视频信息保存到Notion数据库中，同时发送Slack通知。

## 主要特性

1. **从Notion获取监控账号列表**：直接从Notion数据库获取67个要监控的账号
2. **动态账号管理**：每分钟自动刷新账号列表，支持动态添加/移除监控账号
3. **智能重复检测**：每个账号只加载最新100个视频用于重复检查，提高效率
4. **自动视频记录**：新视频自动保存到Notion数据库，包含完整时间信息
5. **线程池处理**：使用线程池处理Notion记录创建和Slack通知，避免阻塞主循环
6. **自定义页面名称**：格式为"账号名 - 新视频 mm-dd hh:mm:ss"

## 数据库结构

### Douyin Accounts 数据库
- **ID**: `23e035de0731804aaf4ac18652c62393`
- **字段**:
  - `Name`: 账号昵称 (title类型)
  - `SecUid`: 账号的SecUid (rich_text类型)
  - `Tags`: 标签 (multi_select类型)
- **监控条件**: 包含"Monitor Posts"标签的账号

### Douyin Posts 数据库
- **ID**: `23e035de0731803c9609e369fdbcc16d`
- **字段**:
  - `Account`: 关联的抖音账号 (relation类型)
  - `Aweme Id`: 视频ID (text类型)
  - `Best Rate Url`: 最佳码率视频链接 (url类型)
  - `Caption`: 视频标题 (text类型)
  - `Description`: 视频描述 (text类型)
  - `Cover Url`: 封面图片链接 (url类型)
  - `Height`: 视频高度 (number类型)
  - `Width`: 视频宽度 (number类型)
  - `Duration`: 视频时长(秒) (number类型)
  - `Date`: 创建日期 (date类型)

## 核心组件

### NotionServices 模块
- `NotionDouyinAccountService`: 账号查询服务
- `NotionDouyinPostService`: 视频记录服务
- `process_new_video`: 简化的新视频处理函数

### PostMonitor 模块
- `NotionDouyinPostMonitor`: 主监控器，管理所有账号的监控任务
- `SingleUserNewPostMonitor`: 单个账号的监控器

## 使用方法

### 1. 正常运行监控器

```bash
# 启动完整监控器（持续运行）
poetry run python main_notion_monitor.py
```

### 2. 测试模式

```bash
# 测试模式（运行5分钟后自动停止）
poetry run python main_notion_monitor.py test
```

### 3. 程序化使用

```python
from PostMonitor.NotionDouyinPostMonitor import NotionDouyinPostMonitor

# 创建并启动监控器
monitor = NotionDouyinPostMonitor()
await monitor.run_forever()
```

## 工作流程

1. **账号获取**: 每分钟从Notion获取带"Monitor Posts"标签的账号
2. **动态管理**: 自动添加新账号监控，移除不再需要监控的账号
3. **视频检查**: 每个账号每20秒检查一次新视频
4. **新视频处理**: 
   - 检查视频是否已存在于Notion数据库
   - 如果是新视频，创建Notion记录
   - 发送Slack通知

## 配置要求

1. **99notion-base包**: 用于Notion数据库操作
2. **Slack配置**: 需要配置Slack Bot Token
3. **Notion权限**: 需要对指定数据库的读写权限

## 优化特性

- **智能查询**: 使用原始Notion API查询，按Date降序排列，只加载最新100个视频
- **线程池处理**: 使用5个工作线程处理Notion记录创建和Slack通知
- **内存优化**: 每个账号只在内存中维护最新100个视频ID用于重复检查
- **错误隔离**: 单个任务失败不影响其他任务，完善的异常处理
- **高效监控**: 动态账号管理，实时检测新视频

## 兼容性

系统保持与原有Excel文件方式的兼容性，可以通过参数选择使用Notion或Excel数据源：

```python
# 使用Notion数据源（默认）
monitor = DouyinPostMonitor(use_notion=True)

# 使用Excel文件
monitor = DouyinPostMonitor(use_notion=False)
```
