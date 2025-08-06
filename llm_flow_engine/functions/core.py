"""
核心基础功能模块 - HTTP请求、数据转换、数学计算等
"""
import aiohttp
import json as pyjson
import asyncio
import ast
import operator
from typing import Any, Dict, List, Union
from loguru import logger


async def http_request_get(url: str, params: Dict = None, headers: Dict = None) -> str:
    """HTTP GET请求"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers=headers) as resp:
            return await resp.text()


async def http_request_post_json(url: str, data: Dict = None, headers: Dict = None) -> str:
    """HTTP POST JSON请求"""
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data, headers=headers) as resp:
            return await resp.text()


async def http_request(url: str, method: str = 'GET', **kwargs):
    """
    HTTP请求函数 - 通用版本
    
    Args:
        url: 请求URL
        method: 请求方法
        **kwargs: 其他参数
    Returns:
        响应数据
    """
    if method.upper() == 'GET':
        return await http_request_get(url, **kwargs)
    elif method.upper() == 'POST':
        return await http_request_post_json(url, **kwargs)
    else:
        raise ValueError(f"不支持的HTTP方法: {method}")


async def string_to_json(s: str) -> Dict:
    """字符串转JSON"""
    return pyjson.loads(s)


async def json_to_string(obj: Any) -> str:
    """JSON转字符串"""
    return pyjson.dumps(obj, ensure_ascii=False, indent=2)


async def calculate(expression: str):
    """
    计算数学表达式
    
    Args:
        expression: 数学表达式字符串
    Returns:
        计算结果
    """
    try:
        # 安全的数学表达式计算
        # 支持的操作
        ops = {
            ast.Add: operator.add,
            ast.Sub: operator.sub, 
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.Mod: operator.mod,
            ast.USub: operator.neg,
            ast.UAdd: operator.pos,
        }
        
        def eval_expr(node):
            if isinstance(node, ast.Num):  # 数字
                return node.n
            elif isinstance(node, ast.Constant):  # Python 3.8+
                return node.value
            elif isinstance(node, ast.BinOp):  # 二元操作
                return ops[type(node.op)](eval_expr(node.left), eval_expr(node.right))
            elif isinstance(node, ast.UnaryOp):  # 一元操作
                return ops[type(node.op)](eval_expr(node.operand))
            else:
                raise TypeError(node)
        
        result = eval_expr(ast.parse(expression, mode='eval').body)
        logger.success(f"计算表达式 '{expression}' = {result}")
        return result
        
    except Exception as e:
        logger.error(f"计算表达式失败: {str(e)}")
        raise


async def text_process(text: str = None, operation: str = "upper", workflow_input: dict = None, **kwargs) -> str:
    """文本处理函数
    
    Args:
        text: 要处理的文本
        operation: 操作类型, "upper"/"lower"/"reverse"
        workflow_input: 工作流输入参数
        **kwargs: 其他参数
    
    Returns:
        str: 处理后的文本
    """
    logger.debug(f"text_process 被调用，text={text}, workflow_input={workflow_input}, kwargs={kwargs}")
    
    # 首先尝试从 kwargs 中的 workflow_input 获取
    if 'workflow_input' in kwargs and isinstance(kwargs['workflow_input'], dict):
        workflow_input = kwargs['workflow_input']
        logger.debug(f"从 kwargs 中获取到 workflow_input: {workflow_input}")
    
    # 优先从 workflow_input 中获取文本
    if workflow_input and isinstance(workflow_input, dict):
        if 'question' in workflow_input:
            text = workflow_input['question']
            logger.debug(f"从 workflow_input.question 获取到文本: {text}")
        elif 'text' in workflow_input:
            text = workflow_input['text']
            logger.debug(f"从 workflow_input.text 获取到文本: {text}")
    
    # 如果输入是字典,尝试从 text 字段获取文本
    if isinstance(text, dict):
        text = text.get('text', str(text))
    elif text is None or text == "":
        # 如果没有提供任何有效输入,返回空字符串
        text = ""
        logger.debug(f"text_process 最终处理的文本为空")
    else:
        text = str(text)
        
    logger.debug(f"text_process 最终处理文本: '{text}'")
        
    # 进行文本处理
    if operation == "upper":
        result = text.upper()
    elif operation == "lower":
        result = text.lower()
    elif operation == "reverse":
        result = text[::-1]
    else:
        result = text
        
    logger.debug(f"text_process 返回结果: '{result}'")
    return result


async def data_merge(*args, **kwargs) -> Dict:
    """
    合并多个数据
    
    Args:
        *args: 位置参数数据
        **kwargs: 关键字参数数据
    Returns:
        包含合并数据的字典
    """
    merged_data = {}
    
    # 处理位置参数
    if args:
        for i, arg in enumerate(args):
            merged_data[f"arg_{i}"] = arg
    
    # 处理关键字参数  
    if kwargs:
        merged_data.update(kwargs)
    
    result = {
        "merged_data": merged_data,
        "args_count": len(args),
        "kwargs_count": len(kwargs),
        "total_count": len(args) + len(kwargs)
    }
    return result
