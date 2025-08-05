# LLM Flow DSL 执行引擎
# 核心组件导入

from .flow_engine import FlowEngine, flow_engine
from .builtin_functions import BUILTIN_FUNCTIONS
from .executor import Executor
from .executor_result import ExecutorResult
from .workflow import WorkFlow
from .dsl_loader import load_workflow_from_dsl
from .model_config import ModelConfigProvider, default_model_provider, get_model_config, list_supported_models

# 版本信息
__version__ = "1.0.0"
__author__ = "LLM Flow Team"
__description__ = "基于asyncio的LLM工作流DSL执行引擎"

# 公开API
__all__ = [
    'FlowEngine',    # 添加FlowEngine类
    'flow_engine',   # 默认实例
    'BUILTIN_FUNCTIONS',
    'Executor', 
    'ExecutorResult',
    'WorkFlow',
    'load_workflow_from_dsl',
    'ModelConfigProvider',
    'default_model_provider',
    'get_model_config',
    'list_supported_models',
    'execute_dsl',
    'quick_llm_call',
    'list_functions'
]

# 便捷接口
async def execute_dsl(dsl: str, inputs: dict = None, dsl_type: str = 'yaml'):
    """执行DSL的快捷方法"""
    return await flow_engine.execute_dsl(dsl, inputs, dsl_type)

async def quick_llm_call(user_input: str):
    """快速LLM调用的快捷方法"""
    return await flow_engine.execute_simple_flow(user_input)

def list_functions():
    """列出所有可用函数"""
    return list(BUILTIN_FUNCTIONS.keys())
