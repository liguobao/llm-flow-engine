# LLM Flow Engine

一个基于 DSL（领域特定语言）的 LLM 工作流引擎，支持多模型协作、依赖管理和结果汇总。通过 YAML 配置文件定义复杂的 AI 工作流，实现多个 LLM 模型的协同工作。

## 核心特性

- **DSL 工作流定义** - 使用 YAML 格式定义复杂的 LLM 工作流
- **DAG 依赖管理** - 支持有向无环图的节点依赖关系和并行执行
- **占位符解析** - 使用 `${node.output}` 语法实现节点间数据传递  
- **多模型支持** - 支持不同 LLM 模型的调用和结果汇总
- **灵活配置** - 自定义模型配置和参数管理
- **异步执行** - 高效的异步任务处理和错误重试
- **结果汇总** - 内置多种结果合并和分析函数
- **可扩展架构** - 支持自定义函数和模型适配器

## 项目结构

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
└── package_demo.py       # 包使用方式演示
```

## 快速开始

### 环境要求

- Python 3.8+
- aiohttp >= 3.8.0
- pyyaml >= 6.0
- loguru >= 0.7.0

### 安装依赖

```bash
# 克隆项目
git clone https://github.com/your-org/llm-flow-engine.git
cd llm-flow-engine

# 安装依赖
pip install -r requirements.txt

# 开发模式安装
pip install -e .
```

### 配置Ollama（推荐）

本项目默认使用本地Ollama模型，请先安装和配置：

```bash
# 1. 安装Ollama
brew install ollama  # macOS
# 或访问 https://ollama.ai 下载

# 2. 启动Ollama服务
ollama serve

# 3. 下载推荐的小模型
ollama pull gemma3:1b       # 1B参数，轻量级
ollama pull qwen2.5:0.5b    # 0.5B参数，快速响应
ollama pull gemma3:4b       # 4B参数，性能均衡
ollama pull deepseek-r1:7b  # 7B参数，深度分析
```

### 运行演示

```bash
# 运行完整示例（需要Ollama服务）
python examples/demo_example.py

# 运行包使用演示
python examples/package_demo.py
```

演示将展示：

- 多模型协同问答
- 结果汇总分析  
- DAG依赖执行
- 占位符数据传递

## API 使用

### 基础用法

```python
import asyncio
from llm_flow_engine import FlowEngine, ModelConfigProvider

async def main():
    # 使用默认配置
    engine = FlowEngine()
    
    # 执行简单DSL
    result = await engine.execute_simple_flow("什么是人工智能？")
    print(result)

# 运行
asyncio.run(main())
```

### 高级用法

```python
import asyncio
from llm_flow_engine import FlowEngine, ModelConfigProvider

async def advanced_example():
    # 创建自定义模型配置
    custom_models = {
        "my_model": {
            "api_url": "http://localhost:11434/api/generate",
            "api_key": "",
            "temperature": 0.7
        }
    }
    
    # 创建配置提供者
    provider = ModelConfigProvider(custom_models)
    
    # 使用自定义配置创建引擎
    engine = FlowEngine(model_provider=provider)
    
    # 执行DSL文件
    result = await engine.execute_dsl_file(
        "examples/demo_qa.yaml", 
        {"question": "解释量子计算"}
    )
    
    print("工作流结果:", result)

asyncio.run(advanced_example())
```

### 自定义模型配置

```python
from llm_flow_engine import ModelConfigProvider

# 方法1：直接创建配置
custom_models = {
    "gpt-4": {
        "api_url": "https://api.openai.com/v1/chat/completions",
        "api_key": "your-api-key",
        "model_name": "gpt-4"
    },
    "local_model": {
        "api_url": "http://localhost:11434/api/generate", 
        "api_key": ""
    }
}

# 方法2：从JSON文件加载
config = ModelConfigProvider.from_file("models_config.json")

# 创建配置提供者
provider = ModelConfigProvider(custom_models)

# 使用自定义配置创建引擎
engine = FlowEngine(model_provider=provider)
```

## 工作流DSL详解

### 基本结构

```yaml
metadata:
  version: "1.1"
  description: "工作流描述"

input:
  type: "start"
  name: "workflow_input"
  data:
    question: "输入问题"

executors:
  - name: "step1"
    type: "task"
    func: "llm_simple_call"
    custom_vars:
      user_input: "${workflow_input.question}"
      model: "gemma3:1b"
    depends_on: []

  - name: "step2"
    type: "task"
    func: "combine_outputs"
    custom_vars:
      inputs: ["${step1.output}"]
    depends_on: ["step1"]

output:
  result: "${step2.output}"
```

### 复杂示例：多模型协作

```yaml
metadata:
  version: "1.1"
  description: "多模型问答汇总工作流"

input:
  type: "start"
  name: "workflow_input"
  data:
    question: ""

executors:
  # 文本预处理
  - name: "text_processing"
    type: "task"
    func: "text_process"
    custom_vars:
      text: "${workflow_input.question}"

  # 三个模型并行回答
  - name: "model1_answer"
    type: "task"
    func: "llm_simple_call"
    custom_vars:
      user_input: "${text_processing.output}"
      model: "gemma3:1b"
    depends_on: ["text_processing"]

  - name: "model2_answer"
    type: "task"
    func: "llm_simple_call"
    custom_vars:
      user_input: "${text_processing.output}"
      model: "qwen2.5:0.5b"
    depends_on: ["text_processing"]

  - name: "model3_answer"
    type: "task"
    func: "llm_simple_call"
    custom_vars:
      user_input: "${text_processing.output}"
      model: "gemma3:4b"
    depends_on: ["text_processing"]

  # 深度分析
  - name: "deep_analysis"
    type: "task"
    func: "llm_simple_call"
    custom_vars:
      user_input: "分析以下回答: ${model1_answer.output}, ${model2_answer.output}, ${model3_answer.output}"
      model: "gemma3:4b"
    depends_on: ["model1_answer", "model2_answer", "model3_answer"]

  # 最终汇总
  - name: "summary_step"
    type: "task"
    func: "llm_simple_call"
    custom_vars:
      user_input: "总结分析: ${deep_analysis.output}"
      model: "deepseek-r1:7b"
    depends_on: ["deep_analysis"]

output:
  original_question: "${workflow_input.question}"
  processed_question: "${text_processing.output}"
  model_answers:
    gemma3_1b: "${model1_answer.output}"
    qwen2_5_0_5b: "${model2_answer.output}"
    gemma3_4b: "${model3_answer.output}"
  deep_analysis: "${deep_analysis.output}"
  final_result: "${summary_step.output}"
```

## 自定义配置

### 1. 模型配置文件

创建 `models_config.json` 文件：

```json
{
  "gemma3:1b": {
    "api_url": "http://localhost:11434/api/generate",
    "api_key": "your_api_key_here"
  },
  "openai-gpt-4": {
    "api_url": "https://api.openai.com/v1/chat/completions", 
    "api_key": "sk-your-openai-key",
    "model_name": "gpt-4"
  },
  "custom-model": {
    "api_url": "https://your-custom-api.com/v1/generate",
    "api_key": "your-custom-key",
    "temperature": 0.7,
    "max_tokens": 2048
  }
}
```

### 2. 工作流执行器配置

```python
from llm_flow_engine import ModelConfigProvider, FlowEngine

# 使用配置文件
config = ModelConfigProvider.from_file("models_config.json")

# 或者直接在代码中配置
config = ModelConfigProvider({
    "gemma3:1b": {
        "api_url": "http://localhost:11434/api/generate",
        "api_key": "",
        "temperature": 0.8,
        "max_tokens": 1024,
        "stream": False
    }
})

# 创建工作流引擎
engine = FlowEngine(config)
result = await engine.execute_dsl_file("workflow.yaml", {"question": "用户问题"})
```

### 3. 内置函数参数说明

#### `llm_simple_call` 参数

- **必需参数**：
  - `user_input`: 用户输入文本
  - `model`: 模型标识符（需在config中配置）

- **可选参数**：
  - `prompt`: 系统提示词（默认：空）
  - `temperature`: 温度参数（默认：从config获取）
  - `max_tokens`: 最大token数（默认：从config获取）
  - `stream`: 是否流式输出（默认：false）

#### `llm_api_call` 参数

- **必需参数**：
  - `user_input`: 用户输入
  - `model`: 模型配置键

- **可选参数**：
  - `prompt`: 系统提示（可选）
  - 其他参数从模型配置中自动提取

### 4. 错误处理配置

```python
from llm_flow_engine import FlowEngine
import logging

# 启用详细日志
logging.basicConfig(level=logging.DEBUG)

# 创建引擎并处理异常
try:
    engine = FlowEngine(config)
    result = await engine.execute_dsl_file("workflow.yaml", input_data)
    print(f"执行成功: {result}")
except Exception as e:
    print(f"执行失败: {e}")
```

## 内置模型配置详情

### 默认支持的模型

```python
# model_config.py 内置配置
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
        'max_tokens': 4096,  # 更大模型的token限制
        'supports': ['temperature', 'top_k', 'top_p']
    },
    'deepseek-r1:7b': {
        'platform': 'ollama',
        'api_url': 'http://localhost:11434/api/chat',
        'auth_header': None,
        'message_format': 'ollama',
        'max_tokens': 8192,  # 大模型支持更多token
        'supports': ['temperature', 'top_k', 'top_p', 'repetition_penalty']
    }
}
```

### 占位符语法

- `${workflow_input.key}` - 引用工作流输入数据
- `${node_name.output}` - 引用前置节点的输出结果
- `${node_name.property}` - 引用节点的特定属性
- 支持嵌套引用和复杂表达式

### DSL语法规则

1. **metadata**: 工作流元数据（版本、描述等）
2. **input**: 定义输入数据结构和初始值
3. **executors**: 执行器列表，按依赖关系执行
4. **output**: 定义最终输出格式

## 贡献指南

欢迎提交PR和Issues！请遵循以下步骤：

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

本项目基于 MIT 许可证开源 - 查看 [LICENSE](LICENSE) 文件了解详情
