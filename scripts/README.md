# 构建脚本说明

本目录包含了项目构建、测试和发布的脚本工具。

## 脚本列表

### 🔨 构建相关

- **`build.sh`** - 构建Python包
  ```bash
  ./scripts/build.sh
  ```

- **`clean.sh`** - 清理构建文件和缓存
  ```bash
  ./scripts/clean.sh
  ```

### 🚀 发布相关

- **`test_publish.sh`** - 发布到TestPyPI进行测试
  ```bash
  ./scripts/test_publish.sh
  ```

- **`publish.sh`** - 发布到正式PyPI
  ```bash
  ./scripts/publish.sh
  ```

### 🔢 版本管理

- **`version.sh`** - 管理项目版本号
  ```bash
  # 版本类型升级
  ./scripts/version.sh patch  # 0.7.0 -> 0.7.1
  ./scripts/version.sh minor  # 0.7.0 -> 0.8.0
  ./scripts/version.sh major  # 0.7.0 -> 1.0.0
  
  # 直接设置版本
  ./scripts/version.sh 1.0.0
  ```

## 完整发布流程

1. **更新版本号**
   ```bash
   ./scripts/version.sh patch
   ```

2. **构建包**
   ```bash
   ./scripts/build.sh
   ```

3. **测试发布** (可选)
   ```bash
   ./scripts/test_publish.sh
   ```

4. **正式发布**
   ```bash
   ./scripts/publish.sh
   ```

## 快捷方式

也可以使用根目录的快捷脚本：

- `./publish.sh` - 完整的交互式发布流程
- `make help` - 查看所有Makefile命令

## 注意事项

- 发布前确保已配置PyPI token
- 建议先在TestPyPI测试
- 版本号应遵循语义化版本规范 (Semantic Versioning)
