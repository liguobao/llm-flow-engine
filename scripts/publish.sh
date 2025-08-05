#!/bin/bash
# 正式发布脚本 - 发布到 PyPI
# 使用方法: ./scripts/publish.sh

set -e

echo "🚀 正式发布到 PyPI"
echo "=================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 检查dist目录
if [ ! -d "dist" ] || [ -z "$(ls -A dist/)" ]; then
    echo -e "${RED}❌ dist目录不存在或为空，请先运行构建${NC}"
    echo -e "${YELLOW}💡 运行: ./scripts/build.sh${NC}"
    exit 1
fi

# 获取版本号
VERSION=$(python -c "
import re
with open('pyproject.toml', 'r') as f:
    content = f.read()
    match = re.search(r'version\s*=\s*[\"\'](.*?)[\"\']', content)
    if match:
        print(match.group(1))
")

echo -e "${GREEN}📋 准备发布版本: ${VERSION}${NC}"

# 发布确认
echo -e "${YELLOW}❓ 确认发布版本 ${VERSION} 到 PyPI? (y/N)${NC}"
read -r confirm_publish
if [[ ! $confirm_publish =~ ^[Yy]$ ]]; then
    echo -e "${RED}❌ 发布已取消${NC}"
    exit 1
fi

# 上传到PyPI
echo -e "${YELLOW}🚀 上传到 PyPI...${NC}"
python -m twine upload dist/*

echo -e "${GREEN}✅ 发布成功!${NC}"
echo -e "${GREEN}🎉 版本 ${VERSION} 已发布到 PyPI${NC}"
echo -e "${GREEN}📦 安装命令: pip install llm-flow-engine==${VERSION}${NC}"
echo -e "${GREEN}🔗 PyPI 链接: https://pypi.org/project/llm-flow-engine/${VERSION}/${NC}"

# 创建Git标签
echo -e "${YELLOW}❓ 是否创建Git标签 v${VERSION}? (Y/n)${NC}"
read -r create_tag
if [[ ! $create_tag =~ ^[Nn]$ ]]; then
    if git rev-parse --git-dir > /dev/null 2>&1; then
        git tag -a "v${VERSION}" -m "Release version ${VERSION}"
        echo -e "${GREEN}✅ Git标签 v${VERSION} 已创建${NC}"
        
        echo -e "${YELLOW}❓ 是否推送标签到远程仓库? (Y/n)${NC}"
        read -r push_tag
        if [[ ! $push_tag =~ ^[Nn]$ ]]; then
            git push origin "v${VERSION}"
            echo -e "${GREEN}✅ Git标签已推送到远程仓库${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  不是Git仓库，跳过标签创建${NC}"
    fi
fi
