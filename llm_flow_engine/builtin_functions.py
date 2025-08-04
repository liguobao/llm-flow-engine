"""
内置函数库 - 包含HTTP请求、LLM调用、数据转换等
"""
import aiohttp
import json as pyjson
import asyncio
from typing import Any, Dict, List, Optional
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

# 全局模型配置提供者 - 会在引擎初始化时注入
_current_model_provider = None

def _get_model_config(model: str) -> dict:
    """获取模型配置 - 内部使用"""
    if _current_model_provider:
        return _current_model_provider.get_model_config(model)
    else:
        # 后备方案：使用默认全局配置
        from .model_config import get_model_config
        return get_model_config(model)

def _set_model_provider(provider):
    """设置当前模型配置提供者 - 由引擎调用"""
    global _current_model_provider
    _current_model_provider = provider

async def llm_api_call(prompt: str, model: str = "gemma3:4b", api_key: str = None, 
                      api_url: str = None, **kwargs) -> str:
    """
    通用LLM API调用 - 使用DataProvider模式支持预配置模型
    
    支持的模型请调用 list_supported_models() 查看
    """
    # 获取模型配置
    config = _get_model_config(model)
    platform = config["platform"]
    
    # 使用自定义URL或模型配置的URL
    final_api_url = api_url or config['api_url']
    
    # 构建消息格式
    messages = kwargs.get("messages", [{"role": "user", "content": prompt}])
    if "messages" not in kwargs and isinstance(prompt, str):
        messages = [{"role": "user", "content": prompt}]
    
    # 过滤支持的参数
    filtered_kwargs = {}
    for key, value in kwargs.items():
        if key in config.get("supports", []) or key in ["messages", "max_tokens"]:
            filtered_kwargs[key] = value
    
    # 根据平台调用对应API
    if platform == 'openai' or platform == 'openai_compatible':
        return await _call_openai_api(final_api_url, model, messages, api_key, config, **filtered_kwargs)
    elif platform == 'anthropic':
        return await _call_anthropic_api(final_api_url, model, messages, api_key, config, **filtered_kwargs)
    elif platform == 'ollama':
        return await _call_ollama_api(final_api_url, model, messages, api_key, config, **filtered_kwargs)
    elif platform == 'google':
        return await _call_google_api(final_api_url, model, messages, api_key, config, **filtered_kwargs)
    else:
        return f"Error: Unsupported platform {platform} for model {model}"

async def _call_openai_api(api_url: str, model: str, messages: list, api_key: str, config: dict, **kwargs) -> str:
    """调用OpenAI格式的API"""
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": kwargs.get("max_tokens", 150),
        "temperature": kwargs.get("temperature", 0.7),
        "stream": False
    }
    
    # 添加OpenAI特有参数
    for key in ["top_p", "frequency_penalty", "presence_penalty", "stop"]:
        if key in kwargs:
            payload[key] = kwargs[key]
    
    async with aiohttp.ClientSession() as session:
        async with session.post(api_url, json=payload, headers=headers) as resp:
            if resp.status == 200:
                result = await resp.json()
                return result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            else:
                return f"OpenAI API Error: {resp.status} - {await resp.text()}"

async def _call_anthropic_api(api_url: str, model: str, messages: list, api_key: str, config: dict, **kwargs) -> str:
    """调用Anthropic Claude API"""
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key or "",
        "anthropic-version": "2023-06-01"
    }
    
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": kwargs.get("max_tokens", 150)
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(api_url, json=payload, headers=headers) as resp:
            if resp.status == 200:
                result = await resp.json()
                return result.get("content", [{}])[0].get("text", "").strip()
            else:
                return f"Anthropic API Error: {resp.status} - {await resp.text()}"

async def _call_ollama_api(api_url: str, model: str, messages: list, api_key: str, config: dict, **kwargs) -> str:
    """调用Ollama本地API"""
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "model": model,
        "messages": messages,
        "stream": False
    }
    
    # Ollama支持的参数
    for key in ["temperature", "top_p", "top_k"]:
        if key in kwargs:
            payload[key] = kwargs[key]
    
    async with aiohttp.ClientSession() as session:
        async with session.post(api_url, json=payload, headers=headers) as resp:
            if resp.status == 200:
                result = await resp.json()
                return result.get("message", {}).get("content", "").strip()
            else:
                return f"Ollama API Error: {resp.status} - {await resp.text()}"

async def _call_google_api(api_url: str, model: str, messages: list, api_key: str, config: dict, **kwargs) -> str:
    """调用Google Gemini API"""
    headers = {"Content-Type": "application/json"}
    if api_key:
        api_url += f"?key={api_key}"
    
    # 转换消息格式为Google格式
    contents = []
    for msg in messages:
        contents.append({
            "parts": [{"text": msg["content"]}],
            "role": "user" if msg["role"] == "user" else "model"
        })
    
    payload = {
        "contents": contents,
        "generationConfig": {
            "maxOutputTokens": kwargs.get("max_tokens", 150),
            "temperature": kwargs.get("temperature", 0.7)
        }
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(api_url, json=payload, headers=headers) as resp:
            if resp.status == 200:
                result = await resp.json()
                candidates = result.get("candidates", [])
                if candidates:
                    return candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                return ""
            else:
                return f"Google API Error: {resp.status} - {await resp.text()}"

async def llm_simple_call(user_input: str, model: str = "gemma3:4b", api_key: str = None) -> str:
    """
    简化的LLM调用
    
    Args:
        user_input: 用户输入
        model: 模型名称
        api_key: API密钥（可选，优先级高于模型配置中的默认值）
    """
    logger.debug(f"llm_simple_call 被调用，user_input: {user_input}, model: {model}, api_key: {api_key}")
    
    # 获取模型配置
    config = _get_model_config(model)
    
    # 对于本地模型（如Ollama），直接调用API
    if config["platform"] == "ollama":
        return await llm_api_call(
            prompt=user_input,
            api_key=None,  # Ollama不需要API key
            model=model,
            max_tokens=500,
            temperature=0.7
        )
    
    # 对于需要API key的平台，检查是否提供了有效的key
    if config["platform"] in ["openai", "anthropic", "google", "openai_compatible"]:
        # 如果没有提供API key或提供的是占位符，返回模拟响应
        if not api_key or api_key in ["your-api-key", "demo-key", ""]:
            await asyncio.sleep(0.5)
            return f"AI回复: 我理解了您的输入 '{user_input}'，这是一个模拟响应（需要真实API key）。"
        
        # 有有效API key，调用真实API
        return await llm_api_call(
            prompt=user_input,
            api_key=api_key,
            model=model,
            max_tokens=500,
            temperature=0.7
        )
    
    # 其他情况，尝试调用API
    return await llm_api_call(
        prompt=user_input,
        api_key=api_key,
        model=model,
        max_tokens=500,
        temperature=0.7
    )

async def llm_chat_call(messages: list, api_key: str, model: str = "gemma3:4b", 
                       system_prompt: str = None, **kwargs) -> str:
    """高级LLM对话调用 - 支持多轮对话和系统提示"""
    if system_prompt:
        messages = [{"role": "system", "content": system_prompt}] + messages
    
    return await llm_api_call(
        prompt="",  # 将被忽略，因为使用messages参数
        api_key=api_key,
        model=model,
        messages=messages,
        **kwargs
    )

async def string_to_json(s: str) -> Dict:
    """字符串转JSON"""
    return pyjson.loads(s)

async def json_to_string(obj: Any) -> str:
    """JSON转字符串"""
    return pyjson.dumps(obj, ensure_ascii=False, indent=2)

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
    # 优先从 workflow_input 中获取文本
    if workflow_input and isinstance(workflow_input, dict):
        text = workflow_input.get('question', text)
    
    # 如果输入是字典,尝试从 text 字段获取文本
    if isinstance(text, dict):
        text = text.get('text', str(text))
    elif text is None:
        # 如果没有提供任何有效输入,返回空字符串
        text = ""
    else:
        text = str(text)
        
    # 进行文本处理
    if operation == "upper":
        return text.upper()
    elif operation == "lower":
        return text.lower()
    elif operation == "reverse":
        return text[::-1]
    return text

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
        import ast
        import operator
        
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

# 基础内置函数映射（不包含模型配置相关函数，这些由引擎注入）
async def combine_outputs(*args, prompt_template: str = None, combine_method: str = "template", 
                         input_mapping: Dict[str, str] = None, **kwargs) -> str:
    """
    组合多个输出，支持灵活的参数传递和组合方式
    
    Args:
        *args: 上游节点的输出
        prompt_template: 格式化模板，使用 {input_name} 等占位符
        combine_method: 组合方式 ('template', 'json', 'structured', 'custom')
        input_mapping: 输入映射，将位置参数映射到具名参数 {0: 'model1_result', 1: 'model2_result'}
        **kwargs: 其他参数，包括自定义组合逻辑
    """
    if not args:
        return ""
    
    logger.debug(f"combine_outputs: 接收到 {len(args)} 个输入参数，组合方式: {combine_method}")
    
    # 构建输入参数字典
    inputs = {}
    
    # 使用input_mapping映射参数名
    if input_mapping:
        for i, arg in enumerate(args):
            if i in input_mapping:
                inputs[input_mapping[i]] = str(arg)
            else:
                inputs[f'input{i+1}'] = str(arg)
    else:
        # 默认命名方式
        for i, arg in enumerate(args):
            inputs[f'input{i+1}'] = str(arg)
            inputs[f'output{i+1}'] = str(arg)  # 保持向后兼容
    
    # 添加kwargs中的参数
    for key, value in kwargs.items():
        if key not in ['prompt_template', 'combine_method', 'input_mapping']:
            inputs[key] = str(value)
    
    logger.debug(f"combine_outputs: 构建的输入字典: {list(inputs.keys())}")
    
    # 根据combine_method选择组合方式
    if combine_method == "template" and prompt_template:
        try:
            result = prompt_template.format(**inputs)
            logger.debug(f"combine_outputs: 模板格式化成功")
            return result
        except KeyError as e:
            logger.warning(f"模板格式化失败，缺少占位符: {e}")
            logger.warning(f"可用的占位符: {list(inputs.keys())}")
            return str(args[0]) if args else ""
    
    elif combine_method == "json":
        # 返回JSON格式的组合结果
        result = {
            "combined_inputs": inputs,
            "input_count": len(args),
            "timestamp": kwargs.get("timestamp", ""),
            "metadata": kwargs.get("metadata", {})
        }
        return pyjson.dumps(result, ensure_ascii=False, indent=2)
    
    elif combine_method == "structured":
        # 结构化组合，适用于多模型结果汇总
        sections = []
        for i, arg in enumerate(args, 1):
            section_name = input_mapping.get(i-1, f"输入{i}") if input_mapping else f"输入{i}"
            sections.append(f"## {section_name}\n{str(arg)}")
        
        if prompt_template:
            header = prompt_template.format(**inputs)
            return f"{header}\n\n" + "\n\n".join(sections)
        else:
            return "\n\n".join(sections)
    
    elif combine_method == "custom":
        # 自定义组合逻辑
        separator = kwargs.get("separator", "\n\n")
        prefix = kwargs.get("prefix", "")
        suffix = kwargs.get("suffix", "")
        
        combined = separator.join(str(arg) for arg in args)
        return f"{prefix}{combined}{suffix}"
    
    else:
        # 默认简单拼接
        return "\n\n".join(str(arg) for arg in args)

async def smart_parameter_pass(*args, target_function: str = None, parameter_mapping: Dict = None, 
                              context_data: Dict = None, **kwargs) -> Any:
    """
    智能参数传递函数 - 替代简单的combine_outputs
    
    Args:
        *args: 上游节点的输出
        target_function: 目标函数名称
        parameter_mapping: 参数映射规则 {'arg0': 'user_input', 'arg1': 'context'}
        context_data: 上下文数据
        **kwargs: 其他参数
    """
    logger.debug(f"smart_parameter_pass: 目标函数={target_function}, 映射={parameter_mapping}")
    
    # 构建目标函数的参数
    target_params = {}
    
    # 应用参数映射
    if parameter_mapping:
        for i, arg in enumerate(args):
            arg_key = f'arg{i}'
            if arg_key in parameter_mapping:
                target_param_name = parameter_mapping[arg_key]
                target_params[target_param_name] = arg
                logger.debug(f"映射参数: {arg_key} -> {target_param_name}")
    
    # 添加上下文数据
    if context_data:
        target_params.update(context_data)
    
    # 添加其他参数
    target_params.update(kwargs)
    
    # 如果指定了目标函数，尝试调用
    if target_function and target_function in BUILTIN_FUNCTIONS:
        func = BUILTIN_FUNCTIONS[target_function]
        logger.debug(f"调用目标函数 {target_function}，参数: {target_params}")
        return await func(**target_params)
    else:
        # 否则返回构建好的参数字典
        return target_params

async def data_flow_transform(*args, transform_rules: List[Dict] = None, **kwargs) -> Any:
    """
    数据流转换函数 - 提供更灵活的数据处理
    
    Args:
        *args: 输入数据
        transform_rules: 转换规则列表 [{'type': 'extract', 'field': 'content'}, {'type': 'format', 'template': '...'}]
        **kwargs: 其他参数
    """
    if not args:
        return {}
    
    current_data = list(args)
    
    if transform_rules:
        for rule in transform_rules:
            rule_type = rule.get('type')
            
            if rule_type == 'extract':
                # 提取字段
                field = rule.get('field')
                if field:
                    current_data = [
                        item.get(field, item) if isinstance(item, dict) else str(item)
                        for item in current_data
                    ]
            
            elif rule_type == 'filter':
                # 过滤数据
                condition = rule.get('condition', lambda x: True)
                current_data = [item for item in current_data if condition(item)]
            
            elif rule_type == 'format':
                # 格式化数据
                template = rule.get('template', '{data}')
                current_data = [
                    template.format(data=item) for item in current_data
                ]
            
            elif rule_type == 'aggregate':
                # 聚合数据
                method = rule.get('method', 'join')
                if method == 'join':
                    separator = rule.get('separator', '\n')
                    current_data = [separator.join(str(item) for item in current_data)]
                elif method == 'count':
                    current_data = [len(current_data)]
    
    return current_data[0] if len(current_data) == 1 else current_data

BUILTIN_FUNCTIONS = {
    "http_request_get": http_request_get,
    "http_request_post_json": http_request_post_json,
    "http_request": http_request,
    "calculate": calculate,
    "llm_api_call": llm_api_call,
    "llm_simple_call": llm_simple_call,
    "llm_chat_call": llm_chat_call,
    "string_to_json": string_to_json,
    "json_to_string": json_to_string,
    "text_process": text_process,
    "data_merge": data_merge,
    "combine_outputs": combine_outputs,
    "smart_parameter_pass": smart_parameter_pass,
    "data_flow_transform": data_flow_transform,
}
