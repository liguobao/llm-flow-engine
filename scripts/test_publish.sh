#!/bin/bash
# 测试发布脚本 - 发布到 TestPyPI
# 使用方法: ./scripts/test_publish.sh

set -e

echo "🧪 测试发布到 TestPyPI"
echo "====================="

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

echo -e "${GREEN}📋 测试发布版本: ${VERSION}${NC}"

# 上传到TestPyPI
echo -e "${YELLOW}🚀 上传到 TestPyPI...${NC}"
python -m twine upload --repository testpypi dist/*

echo -e "${GREEN}✅ TestPyPI 上传成功!${NC}"
echo -e "${GREEN}🔗 TestPyPI 链接: https://test.pypi.org/project/llm-flow-engine/${VERSION}/${NC}"
echo -e "${YELLOW}💡 测试安装命令:${NC}"
echo -e "${YELLOW}   pip install --index-url https://test.pypi.org/simple/ llm-flow-engine==${VERSION}${NC}"
