# LLM Flow Engine

[🇨🇳 中文版本](https://github.com/liguobao/llm-flow-engine/blob/main/docs/README_zh.md) | 🇺🇸 English

A DSL-based LLM workflow engine that supports multi-model collaboration, dependency management, and result aggregation. Define complex AI workflows through YAML configuration files and enable collaborative work between multiple LLM models.

## ✨ Key Features

- **🔧 DSL Workflow Definition** - Define complex LLM workflows using YAML format
- **📊 DAG Dependency Management** - Support directed acyclic graph node dependencies and parallel execution
- **🔗 Placeholder Resolution** - Use `${node.output}` syntax for inter-node data passing
- **🤖 Multi-Model Support** - Support calling different LLM models and result aggregation
- **⚙️ Flexible Configuration** - Custom model configuration and parameter management
- **⚡ Async Execution** - Efficient asynchronous task processing and error retry
- **📈 Result Aggregation** - Built-in various result merging and analysis functions
- **🔧 Extensible Architecture** - Support custom functions and model adapters

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- aiohttp >= 3.8.0
- pyyaml >= 6.0
- loguru >= 0.7.0

### Installation

```bash
pip install llm-flow-engine
```

### Basic Usage

```python
import asyncio
from llm_flow_engine import FlowEngine, ModelConfigProvider

async def main():
    # 1. Configure models (auto-discovery)
    provider = await ModelConfigProvider.from_host_async(
        api_host="http://127.0.0.1:11434", 
        platform="ollama"
    )
    
    # 2. Create engine
    engine = FlowEngine(provider)
    
    # 3. Execute workflow
    dsl_content = """
    metadata:
      version: "1.0"
      description: "Simple Q&A workflow"
    
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
        inputs={"workflow_input": {"question": "What is AI?"}}
    )
    
    print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 📋 Project Structure

```text
llm_flow_engine/
├── __init__.py           # Main package initialization
├── flow_engine.py        # Main engine entry point
├── dsl_loader.py         # DSL parser
├── workflow.py           # Unified workflow management
├── executor.py           # Task executor
├── executor_result.py    # Execution result wrapper
├── builtin_functions.py  # Built-in function library
├── model_config.py       # Model configuration management
└── utils.py             # Utility functions

examples/
├── demo_example.py       # Complete example demo
├── demo_qa.yaml          # Workflow DSL example
└── model_config_demo.py  # Model configuration demo
```

## 🔧 Model Configuration

### Method 1: Auto-Discovery (Recommended)

```python
# Auto-discover Ollama models
provider = await ModelConfigProvider.from_host_async(
    api_host="http://127.0.0.1:11434",
    platform="ollama"
)
```

### Method 2: Manual Configuration

```python
# Create provider and add models manually
provider = ModelConfigProvider()

# Add OpenAI model
provider.add_single_model(
    model_name="gpt-4",
    platform="openai",
    api_url="https://api.openai.com/v1/chat/completions",
    api_key="your-api-key",
    max_tokens=4096
)

# Add custom model
provider.add_single_model(
    model_name="custom-llm",
    platform="openai_compatible",
    api_url="https://your-api.com/v1/chat/completions",
    api_key="your-api-key",
    max_tokens=2048
)
```

## 📝 DSL Workflow Format

### Basic Structure

```yaml
metadata:
  version: "1.0"
  description: "Workflow description"

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
    depends_on: []  # Dependencies
    timeout: 30     # Timeout in seconds
    retry: 2        # Retry count

output:
  type: "end"
  name: "workflow_output"
  data:
    result: "${task1.output}"
```

### Multi-Model Workflow Example

```yaml
metadata:
  version: "1.0"
  description: "Multi-model Q&A with analysis"

input:
  type: "start"
  name: "workflow_input"
  data:
    question: ""

executors:
  # Parallel model calls
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

  # Analysis step (depends on both models)
  - name: analysis
    type: task
    func: llm_simple_call
    custom_vars:
      user_input: "Compare these answers: 1) ${model1_answer.output} 2) ${model2_answer.output}"
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

## 🔌 Built-in Functions

- **`llm_simple_call`** - Basic LLM model call
- **`text_process`** - Text preprocessing and formatting
- **`result_summary`** - Multi-result summarization
- **`data_transform`** - Data format transformation

## 🧪 Running Examples

```bash
# Basic usage demo
python examples/demo_example.py

# Model configuration demo  
python examples/model_config_demo.py

# Package usage demo
python examples/package_demo.py
```

## 📊 Supported Platforms

- **Ollama** - Local LLM models
- **OpenAI** - GPT series models
- **OpenAI Compatible** - Any OpenAI-compatible API
- **Anthropic** - Claude series models
- **Custom** - Custom API endpoints

## 🛠️ Development

### Setup Development Environment

```bash
git clone https://github.com/liguobao/llm-flow-engine.git
cd llm-flow-engine

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .
```

### Project Validation

```bash
# Validate project structure and configuration
python validate_project.py
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

- 🐛 Issues: [GitHub Issues](https://github.com/liguobao/llm-flow-engine/issues)
- 📖 Documentation: [GitHub Wiki](https://github.com/liguobao/llm-flow-engine/wiki)

## 🌟 Star History

If you find this project helpful, please consider giving it a star! ⭐

---

Made with ❤️ by the LLM Flow Engine Team
