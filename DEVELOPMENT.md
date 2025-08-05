# 🔧 开发指南

本项目提供了完整的开发、构建和发布工具链。

## 📁 项目结构

```
llm-flow-engine/
├── llm_flow_engine/       # 核心代码包
├── examples/              # 示例文件
├── docs/                  # 文档
├── scripts/               # 构建和发布脚本
│   ├── build.sh          # 构建包
│   ├── clean.sh          # 清理文件
│   ├── test_publish.sh   # 测试发布
│   ├── publish.sh        # 正式发布
│   ├── version.sh        # 版本管理
│   └── README.md         # 脚本说明
├── pyproject.toml         # 项目配置
├── Makefile              # 快捷命令
└── publish.sh            # 快速发布脚本
```

## 🛠️ 开发环境设置

### 1. 安装依赖

```bash
# 基础依赖
pip install -r requirements.txt

# 开发依赖
make dev-install
# 或
pip install -e ".[dev]"
```

### 2. 运行测试

```bash
make test
# 或直接运行验证脚本
python validate_project.py
```

## 📦 构建和发布

### 使用脚本（推荐）

```bash
# 1. 更新版本号
./scripts/version.sh patch    # 0.7.1 -> 0.7.2
./scripts/version.sh minor    # 0.7.1 -> 0.8.0
./scripts/version.sh major    # 0.7.1 -> 1.0.0

# 2. 构建包
./scripts/build.sh

# 3. 测试发布（可选）
./scripts/test_publish.sh

# 4. 正式发布
./scripts/publish.sh

# 5. 清理构建文件
./scripts/clean.sh
```

### 使用Makefile

```bash
make help           # 查看所有命令
make clean          # 清理文件
make build          # 构建包
make test-publish   # 测试发布
make publish        # 正式发布
```

## 🔄 完整发布流程

1. **开发完成** - 确保代码通过所有测试
2. **更新版本** - 使用 `./scripts/version.sh` 更新版本号
3. **构建包** - 运行 `./scripts/build.sh`
4. **测试发布** - 使用 `./scripts/test_publish.sh` 在TestPyPI测试
5. **正式发布** - 运行 `./scripts/publish.sh`
6. **创建Release** - 在GitHub上创建Release

## 📋 版本管理

项目遵循[语义化版本规范](https://semver.org/lang/zh-CN/)：

- **MAJOR** - 不兼容的API修改
- **MINOR** - 向后兼容的功能性新增
- **PATCH** - 向后兼容的问题修正

```bash
# 版本号格式：MAJOR.MINOR.PATCH
./scripts/version.sh major  # 重大更新
./scripts/version.sh minor  # 功能更新
./scripts/version.sh patch  # 修复更新
```

## 🔗 相关链接

- **PyPI包**: https://pypi.org/project/llm-flow-engine/
- **GitHub仓库**: https://github.com/liguobao/llm-flow-engine
- **中文文档**: https://github.com/liguobao/llm-flow-engine/blob/main/docs/README_zh.md
- **问题反馈**: https://github.com/liguobao/llm-flow-engine/issues

## 🚨 注意事项

- 发布前确保已配置PyPI token
- 建议先在TestPyPI测试发布
- 每次发布会自动创建Git标签
- 保持代码和文档的同步更新
