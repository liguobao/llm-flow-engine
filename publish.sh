#!/bin/bash
# 快速发布脚本 - 简化版
# 使用方法: ./publish.sh [patch|minor|major]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🚀 LLM Flow Engine - 快速发布"
echo "============================"

# 1. 更新版本号（如果提供参数）
if [ $# -eq 1 ]; then
    echo -e "${YELLOW}🔢 更新版本号...${NC}"
    ./scripts/version.sh "$1"
fi

# 2. 构建
echo -e "${YELLOW}🔨 构建包...${NC}"
./scripts/build.sh

# 3. 询问是否测试发布
echo -e "${YELLOW}❓ 是否先测试发布到 TestPyPI? (y/N)${NC}"
read -r test_upload
if [[ $test_upload =~ ^[Yy]$ ]]; then
    ./scripts/test_publish.sh
    echo -e "${YELLOW}❓ 测试完成，继续正式发布? (y/N)${NC}"
    read -r continue_publish
    if [[ ! $continue_publish =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}⏸️  发布已暂停${NC}"
        exit 0
    fi
fi

# 4. 正式发布
./scripts/publish.sh

echo -e "${GREEN}🎉 发布完成!${NC}"
