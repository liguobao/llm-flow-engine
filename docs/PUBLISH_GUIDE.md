# PyPI 发布指南

本文档提供了将 `llm-flow-engine` 发布到 PyPI 的详细步骤。

## 📋 发布前检查清单

- ✅ 项目结构完整（README.md、LICENSE、pyproject.toml）
- ✅ 版本号已更新
- ✅ 依赖项已正确配置
- ✅ 包可以正常导入
- ✅ 测试通过
- ✅ 包构建成功
- ✅ 包通过 twine 检查

## 🚀 发布步骤

### 1. 安装发布工具

```bash
pip install build twine
```

### 2. 运行项目检查

```bash
python check_pypi_ready.py
```

确保所有检查项都通过。

### 3. 构建包

```bash
python -m build
```

这将在 `dist/` 目录下生成两个文件：
- `llm_flow_engine-x.x.x.tar.gz` (源码包)
- `llm_flow_engine-x.x.x-py3-none-any.whl` (wheel包)

### 4. 验证包

```bash
python -m twine check dist/*
```

确保所有包都通过检查。

### 5. 测试发布 (推荐)

首先发布到 TestPyPI 进行测试：

```bash
# 注册 TestPyPI 账号: https://test.pypi.org/account/register/
python -m twine upload --repository testpypi dist/*
```

测试安装：

```bash
pip install --index-url https://test.pypi.org/simple/ llm-flow-engine
```

### 6. 正式发布

确认测试无误后，发布到正式 PyPI：

```bash
# 注册 PyPI 账号: https://pypi.org/account/register/
python -m twine upload dist/*
```

### 7. 验证发布

访问 https://pypi.org/project/llm-flow-engine/ 确认包已成功发布。

测试安装：

```bash
pip install llm-flow-engine
```

## 🔧 版本管理

### 更新版本号

在 `pyproject.toml` 中更新版本号：

```toml
[project]
version = "1.0.1"  # 更新这里
```

### 版本号规范

- **主版本号 (Major)**: 不兼容的 API 修改
- **次版本号 (Minor)**: 向下兼容的功能性新增
- **修订号 (Patch)**: 向下兼容的问题修正

例如：`1.2.3`

## 🔐 安全配置

### 使用 API Token (推荐)

1. 在 PyPI 创建 API Token
2. 配置 `.pypirc` 文件：

```ini
[pypi]
username = __token__
password = pypi-your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-token-here
```

### 使用环境变量

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your-api-token-here
```

## 📝 发布后事项

1. **创建 Git 标签**:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **更新文档**: 确保 README 和文档与发布版本一致

3. **发布说明**: 在 GitHub 创建 Release 说明

4. **清理构建文件**:
   ```bash
   rm -rf build/ dist/ *.egg-info/
   ```

## ❗ 常见问题

### 包名冲突
如果包名已存在，需要选择不同的名称或联系现有包的维护者。

### 上传失败
- 检查网络连接
- 确认 API Token 正确
- 检查包大小是否超过限制 (100MB)

### 版本号已存在
PyPI 不允许重复上传相同版本号，需要增加版本号。

## 🔄 持续集成

考虑使用 GitHub Actions 自动化发布流程：

```yaml
name: Publish to PyPI
on:
  release:
    types: [published]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.x'
    - name: Install dependencies
      run: |
        pip install build twine
    - name: Build package
      run: python -m build
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

## 📞 获取帮助

- PyPI 官方文档: https://packaging.python.org/
- Twine 文档: https://twine.readthedocs.io/
- 项目问题: https://github.com/liguobao/llm-flow-engine/issues
