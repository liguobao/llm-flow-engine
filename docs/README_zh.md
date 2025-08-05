# LLM Flow Engine

🇨🇳 中文版本 | [🇺🇸 English](../README.md)

一个基于 DSL（领域特定语言）的 LLM 工作流引擎，支持多模型协作、依赖管理和结果汇总。通过 YAML 配置文件定义复杂的 AI 工作流，实现多个 LLM 模型的协同工作。

## ✨ 核心特性

- **🔧 DSL 工作流定义** - 使用 YAML 格式定义复杂的 LLM 工作流
- **📊 DAG 依赖管理** - 支持有向无环图的节点依赖关系和并行执行
- **🔗 占位符解析** - 使用 `${node.output}` 语法实现节点间数据传递  
- **🤖 多模型支持** - 支持不同 LLM 模型的调用和结果汇总
- **⚙️ 灵活配置** - 自定义模型配置和参数管理
- **⚡ 异步执行** - 高效的异步任务处理和错误重试
- **📈 结果汇总** - 内置多种结果合并和分析函数
- **🔧 可扩展架构** - 支持自定义函数和模型适配器

## 🚀 快速开始

### 环境要求

- Python 3.8+
- aiohttp >= 3.8.0
- pyyaml >= 6.0
- loguru >= 0.7.0

### 安装

```bash
pip install llm-flow-engine
```

### 基础用法

```python
import asyncio
from llm_flow_engine import FlowEngine, ModelConfigProvider

async def main():
    # 第1步: 配置模型（自动发现）
    provider = await ModelConfigProvider.from_host_async(
        api_host="http://127.0.0.1:11434", 
        platform="ollama"
    )
    
    # 第2步: 创建引擎
    engine = FlowEngine(provider)
    
    # 第3步: 执行工作流
    dsl_content = """
    metadata:
      version: "1.0"
      description: "简单问答工作流"
    
    input:
      type: "start"
      name: "workflow_input"
      data:
        question: ""
    
    executors:
      - name: answer_step
        type: task
        func: llm_simple_call
        custom_vars:
          user_input: "${workflow_input.question}"
          model: "llama2"
    
    output:
      type: "end"
      name: "workflow_output"
      data:
        answer: "${answer_step.output}"
    """
    
    result = await engine.execute_dsl(
        dsl_content, 
        inputs={"workflow_input": {"question": "什么是人工智能？"}}
    )
    
    print(f"结果: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 📋 项目结构

```text
llm_flow_engine/
├── __init__.py           # 主包初始化和便捷接口
├── flow_engine.py        # 主引擎入口
├── dsl_loader.py         # DSL 解析器
├── workflow.py           # 统一工作流管理(支持DAG和简单模式)
├── executor.py           # 任务执行器
├── executor_result.py    # 执行结果封装
├── builtin_functions.py  # 内置函数库
├── model_config.py       # 模型配置管理
└── utils.py             # 工具函数

examples/
├── demo_example.py       # 完整示例演示
├── demo_qa.yaml          # 工作流DSL示例
└── model_config_demo.py  # 模型配置演示
```

## 🔧 模型配置

### 方式1: 自动发现（推荐）

```python
# 自动发现 Ollama 模型
provider = await ModelConfigProvider.from_host_async(
    api_host="http://127.0.0.1:11434",
    platform="ollama"
)
```

### 方式2: 手动配置

```python
# 创建提供者并手动添加模型
provider = ModelConfigProvider()

# 添加 OpenAI 模型
provider.add_single_model(
    model_name="gpt-4",
    platform="openai",
    api_url="https://api.openai.com/v1/chat/completions",
    api_key="your-api-key",
    max_tokens=4096
)

# 添加自定义模型
provider.add_single_model(
    model_name="custom-llm",
    platform="openai_compatible",
    api_url="https://your-api.com/v1/chat/completions",
    api_key="your-api-key",
    max_tokens=2048
)
```

## 📝 DSL 工作流格式

### 基础结构

```yaml
metadata:
  version: "1.0"
  description: "工作流描述"

input:
  type: "start"
  name: "workflow_input"
  data:
    key: "value"

executors:
  - name: task1
    type: task
    func: function_name
    custom_vars:
      param1: "${input.key}"
      param2: "static_value"
    depends_on: []  # 依赖关系
    timeout: 30     # 超时时间（秒）
    retry: 2        # 重试次数

output:
  type: "end"
  name: "workflow_output"
  data:
    result: "${task1.output}"
```

### 多模型工作流示例

```yaml
metadata:
  version: "1.0"
  description: "多模型问答与分析"

input:
  type: "start"
  name: "workflow_input"
  data:
    question: ""

executors:
  # 并行模型调用
  - name: model1_answer
    type: task
    func: llm_simple_call
    custom_vars:
      user_input: "${workflow_input.question}"
      model: "llama2"
    timeout: 30

  - name: model2_answer
    type: task
    func: llm_simple_call
    custom_vars:
      user_input: "${workflow_input.question}"
      model: "mistral"
    timeout: 30

  # 分析步骤（依赖两个模型）
  - name: analysis
    type: task
    func: llm_simple_call
    custom_vars:
      user_input: "比较这些回答: 1) ${model1_answer.output} 2) ${model2_answer.output}"
      model: "llama2"
    depends_on: ["model1_answer", "model2_answer"]

output:
  type: "end"
  name: "workflow_output"
  data:
    original_question: "${workflow_input.question}"
    model1_response: "${model1_answer.output}"
    model2_response: "${model2_answer.output}"
    analysis: "${analysis.output}"
```

## 🔌 内置函数

- **`llm_simple_call`** - 基础 LLM 模型调用
- **`text_process`** - 文本预处理和格式化
- **`result_summary`** - 多结果汇总
- **`data_transform`** - 数据格式转换

## 🧪 运行示例

```bash
# 基础用法演示
python examples/demo_example.py

# 模型配置演示
python examples/model_config_demo.py

# 包使用方式演示
python examples/package_demo.py
```

## 📊 支持的平台

- **Ollama** - 本地 LLM 模型
- **OpenAI** - GPT 系列模型
- **OpenAI Compatible** - 任何 OpenAI 兼容的 API
- **Anthropic** - Claude 系列模型
- **Custom** - 自定义 API 端点

## 🛠️ 开发

### 搭建开发环境

```bash
git clone https://github.com/liguobao/llm-flow-engine.git
cd llm-flow-engine

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码格式化
black .
```

### 项目验证

```bash
# 验证项目结构和配置
python validate_project.py
```

## 📄 许可证

本项目采用 MIT 许可证 - 详情请查看 [LICENSE](../LICENSE) 文件。

## 🤝 贡献

欢迎贡献！请随时提交 Pull Request。

## 📞 支持

- 🐛 Issues: [GitHub Issues](https://github.com/liguobao/llm-flow-engine/issues)
- 📖 文档: [GitHub Wiki](https://github.com/liguobao/llm-flow-engine/wiki)

## 🌟 Star 历史

如果您觉得这个项目有帮助，请考虑给它一个 star！⭐

---

由 LLM Flow Engine 团队用 ❤️ 制作
