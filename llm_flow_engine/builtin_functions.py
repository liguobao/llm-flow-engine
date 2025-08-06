"""
内置函数库 - 重构后的统一入口
注意：本文件已经重构，具体功能实现已拆分到 functions/ 目录下的各个模块中
"""

# 从新的模块化结构中导入所有函数
from .functions import BUILTIN_FUNCTIONS, _set_model_provider, register_tool

# 保持向后兼容性，直接导出常用函数
from .functions.core import (
    http_request_get, http_request_post_json, http_request,
    calculate, string_to_json, json_to_string, text_process, data_merge
)

from .functions.llm_api import (
    llm_api_call, llm_simple_call, llm_chat_call
)

# 为了保持完全的向后兼容性，也导出_set_model_provider函数
__all__ = [
    'BUILTIN_FUNCTIONS', 
    '_set_model_provider', 
    'register_tool',
    # 常用函数直接导出
    'http_request_get', 'http_request_post_json', 'http_request',
    'calculate', 'string_to_json', 'json_to_string', 
    'text_process', 'data_merge',
    'llm_api_call', 'llm_simple_call', 'llm_chat_call'
]
