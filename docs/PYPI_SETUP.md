# PyPI 发布配置指南

本文档详细说明如何配置和使用项目的发布脚本将 `llm-flow-engine` 发布到 PyPI。

## 🔧 发布工具概览

项目提供了多种发布方式：

| 工具 | 用途 | 推荐度 | 使用场景 |
|------|------|--------|----------|
| `scripts/` | 模块化脚本集合 | ⭐⭐⭐⭐⭐ | 日常发布 |
| `publish.sh` | 快速发布脚本 | ⭐⭐⭐⭐⭐ | 日常发布 |
| `Makefile` | Make命令 | ⭐⭐⭐ | 开发环境 |
| GitHub Actions | 自动化CI/CD | ⭐⭐⭐⭐⭐ | 持续集成 |

## 🚀 快速发布 (推荐)

### 1. 使用快速发布脚本

```bash
# 一键发布到PyPI（补丁版本）
./publish.sh patch

# 一键发布到PyPI（小版本）
./publish.sh minor

# 一键发布到PyPI（大版本）
./publish.sh major
```

这个脚本会：
- ✅ 自动更新版本号
- ✅ 构建Python包
- ✅ 可选择测试发布到TestPyPI
- ✅ 发布到正式PyPI
- ✅ 可选测试发布到TestPyPI
- ✅ 发布到正式PyPI
- ✅ 创建Git标签
- ✅ 清理构建文件

### 2. 使用Make命令

```bash
# 查看所有可用命令
make help

# 快速发布
make quick-publish

# 分步骤发布
make clean        # 清理构建文件
make test         # 运行测试
make build        # 构建包
make check        # 检查包
make publish      # 发布到PyPI

# 测试发布
make test-publish # 发布到TestPyPI
```

## 🔐 PyPI 认证配置

### 方法1: API Token (推荐)

1. **获取PyPI API Token**:
   - 登录 [PyPI](https://pypi.org/)
   - 进入 Account Settings → API tokens
   - 创建新的 API token

2. **配置环境变量**:
```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your-api-token-here
```

3. **或者创建 ~/.pypirc 文件**:
```ini
[pypi]
username = __token__
password = pypi-your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-token-here
```

### 方法2: 用户名密码

```ini
[pypi]
username = your-username
password = your-password
```

## 🛠️ 完整自动化发布

### 使用Python脚本

```bash
# 运行完整的自动化发布流程
python publish_to_pypi.py
```

这个脚本提供更详细的检查和控制：
- 🔍 Git状态检查
- 🔐 PyPI认证验证
- 🧪 完整的测试套件
- 📦 包构建和验证
- 🚀 分步骤发布流程
- 🏷️ Git标签管理
- 📝 发布说明生成

## 🤖 GitHub Actions 自动发布

### 设置GitHub Secrets

1. 在GitHub仓库中，进入 Settings → Secrets and variables → Actions
2. 添加以下secrets：
   - `PYPI_API_TOKEN`: 你的PyPI API token

### 自动发布触发

发布会在以下情况自动触发：
- 创建新的GitHub Release时
- 手动触发workflow

### 手动触发发布

1. 进入GitHub仓库的Actions页面
2. 选择"Publish to PyPI"工作流
3. 点击"Run workflow"

## 📋 发布前检查清单

在发布前，确保完成以下检查：

- [ ] 代码已提交并推送到main分支
- [ ] 版本号已在`pyproject.toml`中更新
- [ ] 更新了README.md和文档
- [ ] 运行了所有测试
- [ ] 检查了包的完整性
- [ ] 配置了PyPI认证

## 🔄 版本管理策略

### 语义化版本控制

遵循 [语义化版本控制](https://semver.org/) 规范：

- **主版本号 (MAJOR)**: 不兼容的API更改
- **次版本号 (MINOR)**: 向后兼容的功能添加
- **修订号 (PATCH)**: 向后兼容的问题修复

示例：`1.2.3` → `1.2.4` (修复) → `1.3.0` (新功能) → `2.0.0` (重大更改)

### 更新版本号

在`pyproject.toml`中更新版本：

```toml
[project]
version = "1.0.1"  # 更新这里
```

## 🧪 测试发布流程

### 1. 发布到TestPyPI

```bash
# 使用脚本
./quick_publish.sh  # 会询问是否测试发布

# 或手动发布
python -m twine upload --repository testpypi dist/*
```

### 2. 测试安装

```bash
# 从TestPyPI安装
pip install --index-url https://test.pypi.org/simple/ llm-flow-engine==1.0.0

# 测试导入
python -c "import llm_flow_engine; print('OK')"
```

### 3. 正式发布

确认测试无误后，发布到正式PyPI。

## 📝 发布后流程

### 1. 创建GitHub Release

- 在GitHub上创建新的Release
- 使用标签格式：`v1.0.0`
- 添加发布说明

### 2. 更新文档

- 更新README.md中的版本信息
- 更新安装说明
- 更新变更日志

### 3. 通知用户

- 在项目主页发布公告
- 更新社交媒体
- 发送邮件通知（如适用）

## ❗ 常见问题解决

### 包名已存在

如果包名冲突，需要：
1. 选择不同的包名
2. 在`pyproject.toml`中更新name字段
3. 更新所有相关文档

### 上传失败

常见原因和解决方法：
- **认证失败**: 检查API token是否正确
- **网络问题**: 检查网络连接，可能需要重试
- **包大小**: 确保包大小不超过100MB限制
- **版本冲突**: PyPI不允许重复上传相同版本

### 构建失败

检查：
- Python版本兼容性
- 依赖项是否正确安装
- `pyproject.toml`配置是否正确

## 🔧 高级配置

### 自定义构建配置

在`pyproject.toml`中可以配置：

```toml
[tool.setuptools.packages.find]
include = ["llm_flow_engine*"]
exclude = ["tests*"]

[tool.setuptools.package-data]
llm_flow_engine = ["*.yaml", "*.json"]
```

### 发布脚本定制

你可以修改发布脚本来适应特定需求：
- 添加额外的测试步骤
- 自定义Git标签格式
- 集成其他工具

## 📞 获取帮助

如果在发布过程中遇到问题：

1. 查看PyPI官方文档
2. 检查项目的GitHub Issues
3. 运行`python check_pypi_ready.py`进行诊断
4. 查看详细的错误信息和日志

---

**记住**: 发布到PyPI是不可逆的操作，请在发布前充分测试！
