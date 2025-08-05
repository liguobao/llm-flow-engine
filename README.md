# LLM Flow Engine

一个基于 DSL（领域特定语言）的 LLM 工作流引擎，支持多模型协作、依赖管理和结果汇总。

## 核心特性

- **DSL 工作流定义** - 使用 YAML 格式定义复杂的 LLM 工作流
- **DAG 依赖管理** - 支持节点依赖关系和并行执行
- **占位符解析** - 使用 `${node.output}` 语法实现节点间数据传递
- **多模型支持** - 支持不同 LLM 模型的调用和结果汇总
- **灵活配置** - 自定义模型配置和参数管理
- **异步执行** - 高效的异步任务处理和错误重试

## 项目结构

```text
llm_flow_engine/
├── flow_engine.py        # 主引擎入口
├── dsl_loader.py         # DSL 解析器
├── dag_workflow.py       # DAG 工作流管理
├── executor.py           # 任务执行器
├── builtin_functions.py  # 内置函数库
├── model_config.py       # 模型配置管理
└── utils.py             # 工具函数
```

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置Ollama（推荐）

本项目默认使用本地Ollama模型，请先安装和配置：

```bash
# 1. 安装Ollama
brew install ollama  # macOS
# 或访问 https://ollama.ai 下载

# 2. 启动Ollama服务
ollama serve

# 3. 下载推荐模型
ollama pull gemma3:4b    # 主力模型
ollama pull qwen2.5      # 中文优化
ollama pull gemma2       # 轻量级
ollama pull phi3         # 代码理解
```

详细配置说明请参考 `ollama_config.md`

### 运行演示

```bash

# 安装
pip install -e .

# 运行演示脚本
python examples/demo_example.py
```

## API 使用

```python
from llm_flow_engine import FlowEngine

engine = FlowEngine()
result = await engine.run_workflow_from_dsl(
    "demo_qa.yaml", 
    question="什么是人工智能？"
)
```

## 工作流DSL示例

```yaml
metadata:
  version: "1.0"
  description: "多模型问答汇总工作流"

input:
  type: "start"
  name: "workflow_input"
  data:
    question: "用户输入的原始问题"

executors:
  - name: model1_answer
    type: "task"
    func: llm_simple_call
    custom_vars:
      user_input: "${workflow_input.question}"
      model: "gemma3:4b"

  - name: summary_step
    type: "task"
    func: llm_simple_call
    custom_vars:
      user_input: "请汇总: ${model1_answer.output}"
      model: "qwen2.5"
    depends_on: ["model1_answer"]

output:
  result: "${summary_step.output}"
```

## 模型配置说明

```python
# model_config.py
{
        'gemma3:1b': {
            'platform': 'ollama', 
            'api_url': 'http://localhost:11434/api/chat',
            'auth_header': None,
            'message_format': 'ollama',
            'max_tokens': 2048,  # 适合1B模型的token限制
            'supports': ['temperature', 'top_k', 'top_p']
        },
        'qwen2.5:0.5b': {
            'platform': 'ollama', 
            'api_url': 'http://localhost:11434/api/chat',
            'auth_header': None,
            'message_format': 'ollama',
            'max_tokens': 4096,  # 1.5B模型可以处理更多token
            'supports': ['temperature', 'top_k', 'top_p']
        },
        'gemma3:4b': {
            'platform': 'ollama', 
            'api_url': 'http://localhost:11434/api/chat',
            'auth_header': None,
            'message_format': 'ollama',
            'max_tokens': 4096,  # 4B模型性能更好
            'supports': ['temperature', 'top_k', 'top_p']
        }
    }

```

### 占位符语法

- `${workflow_input.key}` - 引用工作流输入
- `${node_name.output}` - 引用节点输出

## 许可证

MIT License
