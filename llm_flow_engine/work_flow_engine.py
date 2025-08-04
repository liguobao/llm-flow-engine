


# LLM Flow DSL 执行引擎入口文件
# 主要功能已整合到 flow_engine.py
# 运行演示请使用: python demo.py

from .flow_engine import flow_engine
from .builtin_functions import BUILTIN_FUNCTIONS

# 导出主要接口供其他模块使用
__all__ = ['flow_engine', 'BUILTIN_FUNCTIONS']

def get_engine():
    """获取LLM流程引擎实例"""
    return flow_engine

def list_functions():
    """列出所有可用函数"""
    return list(BUILTIN_FUNCTIONS.keys())

async def execute_dsl(dsl: str, inputs: dict = None, dsl_type: str = 'yaml'):
    """执行DSL的快捷方法"""
    return await flow_engine.execute_dsl(dsl, inputs, dsl_type)

async def quick_llm_call(user_input: str, api_key: str = None):
    """快速LLM调用的快捷方法"""
    return await flow_engine.execute_simple_flow(user_input, api_key)
