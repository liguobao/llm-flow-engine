#!/bin/bash
# 构建脚本
# 使用方法: ./scripts/build.sh

set -e

echo "🔨 构建 LLM Flow Engine"
echo "======================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 清理旧文件
echo -e "${YELLOW}🧹 清理构建文件...${NC}"
rm -rf build/ dist/ *.egg-info/

# 安装构建依赖
echo -e "${YELLOW}📦 安装构建依赖...${NC}"
pip install build twine --quiet

# 构建包
echo -e "${YELLOW}🔨 构建Python包...${NC}"
python -m build

# 检查包
echo -e "${YELLOW}🔍 检查包完整性...${NC}"
python -m twine check dist/*

echo -e "${GREEN}✅ 构建完成!${NC}"
echo -e "${GREEN}📦 生成的文件在 dist/ 目录中${NC}"
ls -la dist/
