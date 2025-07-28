# Poetry 使用指南

本项目已成功切换到使用 Poetry 进行包管理。以下是常用的 Poetry 命令和使用方法。

## 项目状态

✅ **迁移完成**
- 已创建 `pyproject.toml` 配置文件
- 已生成 `poetry.lock` 锁定文件
- 所有依赖已成功安装
- Python 版本要求：3.10+

## 常用 Poetry 命令

### 环境管理

```bash
# 激活虚拟环境
poetry shell

# 查看环境信息
poetry env info

# 查看已安装的包
poetry show

# 查看依赖树
poetry show --tree
```

### 依赖管理

```bash
# 安装所有依赖
poetry install

# 添加新依赖
poetry add package_name

# 添加开发依赖
poetry add --group dev package_name

# 移除依赖
poetry remove package_name

# 更新依赖
poetry update

# 更新特定包
poetry update package_name
```

### 运行项目

```bash
# 在 Poetry 环境中运行 Python 脚本
poetry run python main_downloader.py
poetry run python main_douyin_following.py
poetry run python main_douyin_discovers.py

# 或者先激活环境再运行
poetry shell
python main_downloader.py
```

### 构建和发布

```bash
# 构建项目
poetry build

# 发布到 PyPI（如果需要）
poetry publish
```

## 项目配置

### pyproject.toml 主要配置

- **项目名称**: tiktok-downloader
- **版本**: 0.1.0
- **Python 版本**: ^3.10
- **包含的模块**: app, DouyinEndpoints, FileDownload, StudioY, Slack

### 主要依赖

- **Web 框架**: Flask 3.1.1
- **HTTP 客户端**: aiohttp 3.12.14, requests 2.32.4
- **数据处理**: pandas 2.3.1, numpy 2.3.2
- **数据库**: pymongo 4.13.2, motor 3.7.1
- **AWS**: boto3 1.35.99
- **私有包**: 99notion-base 0.1.5 (从私有 PyPI 源)
- **其他**: slack-sdk 3.36.0, qrcode 8.2, lxml 5.4.0

### 私有 PyPI 源配置

项目配置了私有 PyPI 源来安装 `99notion-base` 包：

- **源名称**: private-pypi
- **URL**: https://pypi.9zma.com/simple/
- **优先级**: primary

使用方法：
```python
import notion_base  # 导入 99notion-base 包
print(notion_base.__version__)  # 查看版本
```

## 迁移说明

### 从 requirements.txt 迁移的变化

1. **版本约束更灵活**: 使用 `^` 符号允许兼容的版本更新
2. **自动依赖解析**: Poetry 自动解决依赖冲突
3. **锁定文件**: `poetry.lock` 确保环境一致性
4. **虚拟环境管理**: Poetry 自动创建和管理虚拟环境

### 旧的 requirements.txt

原始的 `requirements.txt` 文件仍然保留，但建议使用 Poetry 进行依赖管理。

## 开发工作流

1. **克隆项目后**:
   ```bash
   poetry install
   ```

2. **添加新功能需要新依赖时**:
   ```bash
   poetry add new_package
   ```

3. **运行项目**:
   ```bash
   poetry run python main_downloader.py
   ```

4. **更新依赖**:
   ```bash
   poetry update
   ```

## 注意事项

- 不要手动编辑 `poetry.lock` 文件
- 提交代码时包含 `pyproject.toml` 和 `poetry.lock`
- 如果遇到依赖冲突，使用 `poetry update` 重新解析
- 建议定期运行 `poetry check` 检查配置文件

## 故障排除

### 常见问题

1. **Python 版本不兼容**:
   确保系统 Python 版本 >= 3.10

2. **依赖冲突**:
   ```bash
   poetry lock --no-update
   poetry install
   ```

3. **虚拟环境问题**:
   ```bash
   poetry env remove python
   poetry install
   ```

## 更多信息

- [Poetry 官方文档](https://python-poetry.org/docs/)
- [依赖规范说明](https://python-poetry.org/docs/dependency-specification/)
