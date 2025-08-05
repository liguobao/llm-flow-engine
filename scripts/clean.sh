#!/bin/bash
# 清理构建文件脚本
# 使用方法: ./scripts/clean.sh

echo "🧹 清理构建文件"
echo "==============="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🗑️  删除构建文件...${NC}"

# 清理Python构建文件
rm -rf build/
rm -rf dist/
rm -rf *.egg-info/
rm -rf **/*.egg-info/

# 清理Python缓存
find . -type d -name "__pycache__" -delete
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete

# 清理临时文件
rm -rf .pytest_cache/
rm -rf .coverage
rm -rf htmlcov/
rm -rf .mypy_cache/

echo -e "${GREEN}✅ 清理完成!${NC}"
