# LLM Flow Engine - Makefile
# 提供便捷的开发和发布命令

.PHONY: help install dev-install test clean build check publish test-publish version

help:  ## 显示帮助信息
	@echo "🚀 LLM Flow Engine - 可用命令:"
	@echo "================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## 安装项目依赖
	pip install -r requirements.txt

dev-install:  ## 安装开发依赖
	pip install -e ".[dev]"
	pip install build twine

test:  ## 运行测试
	@echo "🧪 运行项目测试..."
	@if [ -f "validate_project.py" ]; then python validate_project.py; fi

clean:  ## 清理构建文件
	./scripts/clean.sh

build:  ## 构建Python包
	./scripts/build.sh

check: build  ## 检查包完整性
	@echo "🔍 检查包完整性..."
	python -m twine check dist/*

test-publish:  ## 发布到TestPyPI
	./scripts/test_publish.sh

publish:  ## 发布到正式PyPI
	./scripts/publish.sh

version:  ## 显示和管理版本
	./scripts/version.sh

check-git:  ## 检查Git状态

auto-publish:  ## 自动化发布 (完整流程)
	@echo "🤖 执行自动化发布流程..."
	python publish_to_pypi.py

version:  ## 显示当前版本
	@echo "当前版本: $$(python get_version.py)"

check-git:  ## 检查Git状态
		@echo "📊 Git状态检查..."
	@git status --porcelain | head -10
	@echo "当前分支: $$(git branch --show-current)"
	@echo "最新提交: $$(git log -1 --oneline)"

# 发布前完整检查
pre-publish: clean test check check-git  ## 发布前完整检查
	@echo "✅ 发布前检查完成"

# 开发环境设置
setup-dev:  ## 设置开发环境
	@echo "🛠️  设置开发环境..."
	pip install -e ".[dev]"
	pip install build twine
	@echo "✅ 开发环境设置完成"

# 发布前完整检查
pre-publish: clean test check check-git  ## 发布前完整检查
	@echo "✅ 发布前检查完成"

# 开发环境设置
setup-dev:  ## 设置开发环境
	@echo "🛠️  设置开发环境..."
	pip install -e ".[dev]"
	pip install build twine
	@echo "✅ 开发环境设置完成"

# 显示项目信息
info:  ## 显示项目信息
	@python project_info.py

# PyPI相关
pypi-info:  ## 显示PyPI发布信息
	@python project_info.py pypi
