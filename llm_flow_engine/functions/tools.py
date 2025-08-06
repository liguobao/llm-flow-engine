"""
工具执行模块 - 工具注册、执行和智能调用
"""
import asyncio
import json as pyjson
from typing import Any, Dict, List
from loguru import logger


# 工具注册表
_tool_registry = {}


def register_tool(name: str, func: callable, description: str, parameters: Dict = None):
    """注册工具"""
    _tool_registry[name] = {
        "function": func,
        "description": description,
        "parameters": parameters or {},
        "name": name
    }
    logger.info(f"工具已注册: {name}")


async def list_available_tools() -> List[Dict]:
    """列出可用工具"""
    tools = []
    for name, tool_info in _tool_registry.items():
        tools.append({
            "name": name,
            "description": tool_info["description"],
            "parameters": tool_info["parameters"]
        })
    return tools


async def execute_tool(tool_name: str, **kwargs) -> Any:
    """执行指定工具"""
    try:
        if tool_name not in _tool_registry:
            raise ValueError(f"未找到工具: {tool_name}")
        
        tool_info = _tool_registry[tool_name]
        func = tool_info["function"]
        
        logger.info(f"执行工具: {tool_name}, 参数: {kwargs}")
        
        # 执行工具函数
        if asyncio.iscoroutinefunction(func):
            result = await func(**kwargs)
        else:
            result = func(**kwargs)
        
        logger.success(f"工具执行成功: {tool_name}")
        return result
    except Exception as e:
        logger.error(f"工具执行失败 {tool_name}: {e}")
        raise


async def llm_tool_call(user_input: str, model: str = "gemma3:4b", auto_execute: bool = True) -> str:
    """LLM工具调用 - 智能选择和执行工具"""
    from .llm_api import llm_api_call
    
    try:
        # 1. 获取可用工具列表
        available_tools = await list_available_tools()
        
        if not available_tools:
            return "当前没有可用工具"
        
        # 2. 构建工具选择提示词
        tools_desc = "\n".join([
            f"- {tool['name']}: {tool['description']}"
            for tool in available_tools
        ])
        
        prompt = f"""你是一个智能助手，可以使用以下工具来帮助用户:

可用工具:
{tools_desc}

用户请求: {user_input}

请分析用户的请求，如果需要使用工具，请按以下格式回复:
TOOL_CALL: 工具名称
PARAMETERS: 参数JSON

如果不需要使用工具，直接回答用户问题。"""

        # 3. 让LLM选择工具
        llm_response = await llm_api_call(prompt=prompt, model=model)
        
        # 4. 解析LLM响应，看是否需要调用工具
        if "TOOL_CALL:" in llm_response and auto_execute:
            lines = llm_response.split('\n')
            tool_name = None
            parameters = {}
            
            for line in lines:
                if line.startswith("TOOL_CALL:"):
                    tool_name = line.replace("TOOL_CALL:", "").strip()
                elif line.startswith("PARAMETERS:"):
                    param_str = line.replace("PARAMETERS:", "").strip()
                    try:
                        parameters = pyjson.loads(param_str)
                    except:
                        parameters = {}
            
            if tool_name:
                # 执行工具
                tool_result = await execute_tool(tool_name, **parameters)
                
                # 让LLM基于工具结果生成最终回答
                final_prompt = f"""用户请求: {user_input}

我使用了工具 {tool_name} 获得以下结果:
{tool_result}

请基于这个结果给用户一个完整的回答:"""
                
                final_answer = await llm_api_call(prompt=final_prompt, model=model)
                return final_answer
        
        return llm_response
        
    except Exception as e:
        logger.error(f"LLM工具调用失败: {e}")
        return f"工具调用失败: {str(e)}"


# 注册一些基础工具
def _initialize_basic_tools():
    """初始化基础工具"""
    from .core import calculate
    
    register_tool(
        "get_current_weather",
        lambda location: f"{location}的天气：晴朗，温度25°C",
        "获取指定地点的当前天气信息",
        {"location": {"type": "string", "description": "地点名称"}}
    )
    
    register_tool(
        "calculate_math",
        calculate,
        "计算数学表达式",
        {"expression": {"type": "string", "description": "数学表达式"}}
    )
    
    register_tool(
        "search_web",
        lambda query: f"搜索'{query}'的结果：这是一个模拟的网络搜索结果",
        "在网络上搜索信息",
        {"query": {"type": "string", "description": "搜索查询"}}
    )


# 初始化基础工具
_initialize_basic_tools()
