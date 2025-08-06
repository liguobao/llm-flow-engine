"""
LLM API调用模块 - 处理各种LLM平台的API调用
"""
import aiohttp
import asyncio
from typing import Any, Dict, List
from loguru import logger

# 全局模型配置提供者 - 会在引擎初始化时注入
_current_model_provider = None


def _get_model_config(model: str) -> dict:
    """获取模型配置 - 内部使用"""
    if _current_model_provider:
        return _current_model_provider.get_model_config(model)
    else:
        # 后备方案：使用默认全局配置
        from ..model_config import get_model_config
        return get_model_config(model)


def _set_model_provider(provider):
    """设置当前模型配置提供者 - 由引擎调用"""
    global _current_model_provider
    _current_model_provider = provider


async def llm_api_call(user_input: str = None, prompt: str = None, model: str = "gemma3:4b", **kwargs) -> str:
    """
    通用LLM API调用 - 使用DataProvider模式支持预配置模型
    
    Args:
        user_input: 用户原始输入内容（会作为 role="user" 的消息）
        prompt: 系统提示词（会作为 role="system" 的消息）
        model: 模型名称
        **kwargs: 其他参数
    
    支持的模型请调用 list_supported_models() 查看
    """
    # 获取模型配置
    config = _get_model_config(model)
    platform = config["platform"]
    
    # 从配置中提取api_url和api_key
    api_url = config['api_url']
    api_key = config.get('api_key', None)
    
    # 构建消息格式
    if "messages" in kwargs:
        # 如果直接提供了messages，使用它
        messages = kwargs["messages"]
    else:
        # 构建消息列表
        messages = []
        
        # 添加系统提示词（如果有）
        if prompt:
            messages.append({"role": "system", "content": prompt})
        
        # 添加用户输入（如果有）
        if user_input:
            messages.append({"role": "user", "content": user_input})
        
        # 如果都没有提供，报错
        if not messages:
            raise ValueError("必须提供 user_input、prompt 或 messages 参数")
    
    # 过滤支持的参数
    filtered_kwargs = {}
    for key, value in kwargs.items():
        if key in config.get("supports", []) or key in ["messages", "max_tokens"]:
            filtered_kwargs[key] = value
    
    # 根据平台调用对应API
    if platform == 'openai' or platform == 'openai_compatible':
        return await _call_openai_api(api_url, model, messages, api_key, config, **filtered_kwargs)
    elif platform == 'anthropic':
        return await _call_anthropic_api(api_url, model, messages, api_key, config, **filtered_kwargs)
    elif platform == 'ollama':
        return await _call_ollama_api(api_url, model, messages, api_key, config, **filtered_kwargs)
    elif platform == 'google':
        return await _call_google_api(api_url, model, messages, api_key, config, **filtered_kwargs)
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


async def llm_simple_call(user_input: str, model: str = "gemma3:4b", **kwargs) -> str:
    """
    简化的LLM调用
    
    Args:
        user_input: 用户输入
        model: 模型名称
        **kwargs: 其他参数
    """
    logger.debug(f"llm_simple_call 被调用，user_input: '{user_input}' (type: {type(user_input)}), model: {model}")
    logger.debug(f"llm_simple_call 收到的 kwargs: {kwargs}")
    
    # 如果 user_input 是 None 或空，尝试从 kwargs 中获取
    if not user_input:
        if 'user_input' in kwargs:
            user_input = kwargs['user_input']
            logger.debug(f"从 kwargs 中获取到 user_input: '{user_input}'")
    
    if not user_input:
        logger.warning("llm_simple_call 没有收到有效的 user_input")
        return "Error: No valid user input provided to llm_simple_call"
    
    # 获取模型配置
    config = _get_model_config(model)
    
    # 对于本地模型（如Ollama），直接调用API
    if config["platform"] == "ollama":
        return await llm_api_call(
            user_input=user_input,
            model=model,
            max_tokens=500,
            temperature=0.7
        )
    
    # 对于需要API key的平台，检查配置中是否有有效的key
    if config["platform"] in ["openai", "anthropic", "google", "openai_compatible"]:
        api_key = config.get('api_key')
        # 如果没有配置API key或配置的是占位符，返回模拟响应
        if not api_key or api_key in ["your-api-key", "demo-key", ""]:
            await asyncio.sleep(0.5)
            return f"AI回复: 我理解了您的输入 '{user_input}'，这是一个模拟响应（需要在模型配置中设置真实API key）。"
        
        # 有有效API key，调用真实API
        return await llm_api_call(
            user_input=user_input,
            model=model,
            max_tokens=500,
            temperature=0.7
        )
    
    # 其他情况，尝试调用API
    return await llm_api_call(
        user_input=user_input,
        model=model,
        max_tokens=500,
        temperature=0.7
    )


async def llm_chat_call(messages: list, model: str = "gemma3:4b", 
                       system_prompt: str = None, **kwargs) -> str:
    """高级LLM对话调用 - 支持多轮对话和系统提示"""
    # 如果提供了系统提示，将其作为prompt参数传递
    if system_prompt:
        return await llm_api_call(
            prompt=system_prompt,
            model=model,
            messages=messages,
            **kwargs
        )
    else:
        return await llm_api_call(
            model=model,
            messages=messages,
            **kwargs
        )
