#!/bin/bash
# 版本管理脚本
# 使用方法: ./scripts/version.sh [patch|minor|major|<version>]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🔢 版本管理工具"
echo "==============="

# 获取当前版本
CURRENT_VERSION=$(python -c "
import re
with open('pyproject.toml', 'r') as f:
    content = f.read()
    match = re.search(r'version\s*=\s*[\"\'](.*?)[\"\']', content)
    if match:
        print(match.group(1))
")

echo -e "${GREEN}📋 当前版本: ${CURRENT_VERSION}${NC}"

if [ $# -eq 0 ]; then
    echo -e "${YELLOW}用法: $0 [patch|minor|major|<version>]${NC}"
    echo -e "${YELLOW}示例:${NC}"
    echo -e "${YELLOW}  $0 patch      # 0.7.0 -> 0.7.1${NC}"
    echo -e "${YELLOW}  $0 minor      # 0.7.0 -> 0.8.0${NC}"
    echo -e "${YELLOW}  $0 major      # 0.7.0 -> 1.0.0${NC}"
    echo -e "${YELLOW}  $0 0.8.0      # 直接设置版本${NC}"
    exit 0
fi

VERSION_TYPE=$1

# 计算新版本号
if [ "$VERSION_TYPE" = "patch" ] || [ "$VERSION_TYPE" = "minor" ] || [ "$VERSION_TYPE" = "major" ]; then
    NEW_VERSION=$(python -c "
import re
version = '$CURRENT_VERSION'
parts = version.split('.')
major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])

if '$VERSION_TYPE' == 'patch':
    patch += 1
elif '$VERSION_TYPE' == 'minor':
    minor += 1
    patch = 0
elif '$VERSION_TYPE' == 'major':
    major += 1
    minor = 0
    patch = 0

print(f'{major}.{minor}.{patch}')
")
else
    NEW_VERSION=$VERSION_TYPE
fi

echo -e "${GREEN}🎯 新版本: ${NEW_VERSION}${NC}"

# 确认更新
echo -e "${YELLOW}❓ 确认更新版本从 ${CURRENT_VERSION} 到 ${NEW_VERSION}? (y/N)${NC}"
read -r confirm
if [[ ! $confirm =~ ^[Yy]$ ]]; then
    echo -e "${RED}❌ 版本更新已取消${NC}"
    exit 1
fi

# 更新pyproject.toml中的版本号
echo -e "${YELLOW}📝 更新 pyproject.toml...${NC}"
sed -i.bak "s/version = \"${CURRENT_VERSION}\"/version = \"${NEW_VERSION}\"/" pyproject.toml
rm pyproject.toml.bak

# 更新__init__.py中的版本号（如果存在）
if [ -f "llm_flow_engine/__init__.py" ]; then
    echo -e "${YELLOW}📝 更新 __init__.py...${NC}"
    sed -i.bak "s/__version__ = \"${CURRENT_VERSION}\"/__version__ = \"${NEW_VERSION}\"/" llm_flow_engine/__init__.py
    rm llm_flow_engine/__init__.py.bak 2>/dev/null || true
fi

echo -e "${GREEN}✅ 版本已更新到 ${NEW_VERSION}${NC}"

# 询问是否提交到Git
if git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${YELLOW}❓ 是否提交版本更新到Git? (Y/n)${NC}"
    read -r commit_git
    if [[ ! $commit_git =~ ^[Nn]$ ]]; then
        git add pyproject.toml llm_flow_engine/__init__.py 2>/dev/null || git add pyproject.toml
        git commit -m "Bump version to ${NEW_VERSION}"
        echo -e "${GREEN}✅ 版本更新已提交到Git${NC}"
    fi
fi
