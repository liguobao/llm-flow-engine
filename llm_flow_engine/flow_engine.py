"""
LLM Flow DSL 执行引擎 - 核心入口
支持用户输入 -> DSL执行 -> 输出结果
"""
import asyncio
import json
from typing import Dict, Any, List
from .dsl_loader import load_workflow_from_dsl
from .builtin_functions import BUILTIN_FUNCTIONS, _set_model_provider
from .model_config import ModelConfigProvider, default_model_provider

class FlowEngine:
    def __init__(self, model_provider: ModelConfigProvider = None):
        """
        初始化Flow引擎
        
        Args:
            model_provider: 自定义模型配置提供者，如果不提供则使用全局默认配置
        """
        self.builtin_functions = BUILTIN_FUNCTIONS.copy()
        self.model_provider = model_provider or default_model_provider
        
        # 设置全局模型配置提供者，供内置函数使用
        _set_model_provider(self.model_provider)
        
        # 将模型配置相关函数注入到内置函数中
        self.builtin_functions.update({
            'get_model_config': self.model_provider.get_model_config,
            'list_supported_models': self.model_provider.list_supported_models,
        })
        
    def register_function(self, name: str, func):
        """注册自定义函数"""
        self.builtin_functions[name] = func
    
    def set_model_provider(self, provider: ModelConfigProvider):
        """设置模型配置提供者"""
        self.model_provider = provider
        # 设置全局模型配置提供者
        _set_model_provider(provider)
        # 更新内置函数中的模型配置函数
        self.builtin_functions.update({
            'get_model_config': provider.get_model_config,
            'list_supported_models': provider.list_supported_models,
        })
    
    def add_model(self, model_name: str, config: dict):
        """添加新模型配置到当前引擎"""
        self.model_provider.add_model(model_name, config)
    
    async def execute_dsl(self, dsl: str, inputs: Dict[str, Any] = None, dsl_type: str = 'yaml') -> Dict[str, Any]:
        """
        执行DSL流程
        Args:
            dsl: DSL定义字符串
            inputs: 用户输入参数
            dsl_type: DSL类型 ('yaml' 或 'json')
        Returns:
            包含执行结果和元信息的字典
        """
        try:
            # 解析并创建工作流
            workflow = load_workflow_from_dsl(dsl, self.builtin_functions, dsl_type)
            
            # 执行工作流
            if inputs:
                results = await workflow.run(**inputs)
            else:
                results = await workflow.run()
            
            return {
                'success': True,
                'dsl': dsl,
                'inputs': inputs or {},
                'results': results,
                'error': None
            }
        except Exception as e:
            return {
                'success': False,
                'dsl': dsl,
                'inputs': inputs or {},
                'results': None,
                'error': str(e)
            }
    
    async def execute_simple_flow(self, user_input: str) -> Dict[str, Any]:
        """
        执行简单的用户输入 -> LLM处理 -> 输出流程
        """
        simple_dsl = f"""
executors:
  - name: llm_process
    func: llm_simple_call
    custom_vars:
      user_input: "{user_input}"
"""
        return await self.execute_dsl(simple_dsl, {'input': user_input})

# 全局引擎实例
flow_engine = FlowEngine()
