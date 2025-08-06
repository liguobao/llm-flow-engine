"""
函数模块初始化文件 - 导入所有函数并创建统一的BUILTIN_FUNCTIONS字典
"""

# 导入所有模块的函数
from .core import (
    http_request_get, http_request_post_json, http_request,
    string_to_json, json_to_string, calculate, text_process, data_merge
)

from .llm_api import (
    llm_api_call, llm_simple_call, llm_chat_call, _set_model_provider
)

from .data_flow import (
    combine_outputs, smart_parameter_pass, data_flow_transform
)

from .file_time import (
    file_read, file_write, file_append, file_exists, list_directory,
    get_current_time, date_calculate, timestamp_to_date, date_to_timestamp
)

from .text_data import (
    regex_extract, regex_replace, string_template, text_similarity,
    validate_email, validate_url, data_type_convert,
    base64_encode, base64_decode, hash_text, generate_uuid
)

from .control_network import (
    conditional_execute, switch_case, loop_execute,
    cache_set, cache_get, cache_clear,
    http_request_with_retry, webhook_call
)

from .analysis_llm import (
    data_statistics, data_filter, data_sort,
    llm_extract_json, llm_summarize, llm_translate
)

from .rag import (
    embedding_text, vector_store_add, vector_search, rag_retrieve, rag_qa
)

from .tools import (
    list_available_tools, execute_tool, llm_tool_call, register_tool
)

from .knowledge_base import (
    knowledge_base_create, knowledge_base_add_document, knowledge_base_search,
    knowledge_base_qa, knowledge_base_list, knowledge_base_get_info
)

from .agent import agent_process


# 统一的内置函数字典
BUILTIN_FUNCTIONS = {
    # 核心功能
    "http_request_get": http_request_get,
    "http_request_post_json": http_request_post_json,
    "http_request": http_request,
    "calculate": calculate,
    "string_to_json": string_to_json,
    "json_to_string": json_to_string,
    "text_process": text_process,
    "data_merge": data_merge,
    
    # LLM API调用
    "llm_api_call": llm_api_call,
    "llm_simple_call": llm_simple_call,
    "llm_chat_call": llm_chat_call,
    
    # 数据流处理
    "combine_outputs": combine_outputs,
    "smart_parameter_pass": smart_parameter_pass,
    "data_flow_transform": data_flow_transform,
    
    # 文件和时间操作
    "file_read": file_read,
    "file_write": file_write,
    "file_append": file_append,
    "file_exists": file_exists,
    "list_directory": list_directory,
    "get_current_time": get_current_time,
    "date_calculate": date_calculate,
    "timestamp_to_date": timestamp_to_date,
    "date_to_timestamp": date_to_timestamp,
    
    # 文本和数据处理
    "regex_extract": regex_extract,
    "regex_replace": regex_replace,
    "string_template": string_template,
    "text_similarity": text_similarity,
    "validate_email": validate_email,
    "validate_url": validate_url,
    "data_type_convert": data_type_convert,
    "base64_encode": base64_encode,
    "base64_decode": base64_decode,
    "hash_text": hash_text,
    "generate_uuid": generate_uuid,
    
    # 流程控制和网络
    "conditional_execute": conditional_execute,
    "switch_case": switch_case,
    "loop_execute": loop_execute,
    "cache_set": cache_set,
    "cache_get": cache_get,
    "cache_clear": cache_clear,
    "http_request_with_retry": http_request_with_retry,
    "webhook_call": webhook_call,
    
    # 数据分析和LLM增强
    "data_statistics": data_statistics,
    "data_filter": data_filter,
    "data_sort": data_sort,
    "llm_extract_json": llm_extract_json,
    "llm_summarize": llm_summarize,
    "llm_translate": llm_translate,
    
    # RAG检索功能
    "embedding_text": embedding_text,
    "vector_store_add": vector_store_add,
    "vector_search": vector_search,
    "rag_retrieve": rag_retrieve,
    "rag_qa": rag_qa,
    
    # 工具执行功能
    "list_available_tools": list_available_tools,
    "execute_tool": execute_tool,
    "llm_tool_call": llm_tool_call,
    
    # 知识库功能
    "knowledge_base_create": knowledge_base_create,
    "knowledge_base_add_document": knowledge_base_add_document,
    "knowledge_base_search": knowledge_base_search,
    "knowledge_base_qa": knowledge_base_qa,
    "knowledge_base_list": knowledge_base_list,
    "knowledge_base_get_info": knowledge_base_get_info,
    
    # 智能Agent功能
    "agent_process": agent_process,
}

# 导出模型提供者设置函数
__all__ = ['BUILTIN_FUNCTIONS', '_set_model_provider', 'register_tool']
