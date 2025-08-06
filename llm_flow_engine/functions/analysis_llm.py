"""
数据分析和LLM增强模块 - 数据统计分析和LLM增强功能
"""
import json as pyjson
import re
from typing import Dict, List, Union
from loguru import logger


# =============================================================================
# 数据分析和统计
# =============================================================================

async def data_statistics(data: List[Union[int, float]]) -> Dict[str, float]:
    """数据统计分析"""
    if not data:
        return {}
    
    sorted_data = sorted(data)
    n = len(data)
    
    stats = {
        "count": n,
        "sum": sum(data),
        "mean": sum(data) / n,
        "min": min(data),
        "max": max(data),
        "median": sorted_data[n // 2] if n % 2 == 1 else (sorted_data[n // 2 - 1] + sorted_data[n // 2]) / 2
    }
    
    # 标准差
    variance = sum((x - stats["mean"]) ** 2 for x in data) / n
    stats["std_dev"] = variance ** 0.5
    
    return stats


async def data_filter(data: List[Dict], conditions: Dict[str, any]) -> List[Dict]:
    """数据过滤"""
    filtered_data = []
    for item in data:
        match = True
        for key, expected_value in conditions.items():
            if key not in item or item[key] != expected_value:
                match = False
                break
        if match:
            filtered_data.append(item)
    return filtered_data


async def data_sort(data: List[Dict], sort_key: str, reverse: bool = False) -> List[Dict]:
    """数据排序"""
    return sorted(data, key=lambda x: x.get(sort_key, 0), reverse=reverse)


# =============================================================================
# LLM 增强功能
# =============================================================================

async def llm_extract_json(user_input: str, model: str = "gemma3:4b", 
                          schema_description: str = None) -> Dict:
    """LLM提取JSON数据"""
    from .llm_api import llm_api_call
    
    prompt = f"请从以下文本中提取结构化信息，以JSON格式返回"
    if schema_description:
        prompt += f"，按照以下schema：{schema_description}"
    prompt += f"\n\n文本：{user_input}\n\n只返回JSON，不要其他文字："
    
    result = await llm_api_call(prompt=prompt, model=model, max_tokens=500)
    
    try:
        # 尝试提取JSON部分
        json_match = re.search(r'\{.*\}', result, re.DOTALL)
        if json_match:
            return pyjson.loads(json_match.group())
        else:
            return pyjson.loads(result.strip())
    except Exception as e:
        logger.error(f"JSON解析失败: {e}")
        return {"raw_response": result, "error": str(e)}


async def llm_summarize(text: str, max_length: int = 200, model: str = "gemma3:4b") -> str:
    """LLM文本摘要"""
    from .llm_api import llm_api_call
    
    prompt = f"请将以下文本总结为不超过{max_length}字的摘要：\n\n{text}"
    
    return await llm_api_call(prompt=prompt, model=model, max_tokens=max_length + 50)


async def llm_translate(text: str, target_language: str = "中文", 
                       model: str = "gemma3:4b") -> str:
    """LLM文本翻译"""
    from .llm_api import llm_api_call
    
    prompt = f"请将以下文本翻译为{target_language}：\n\n{text}"
    
    return await llm_api_call(prompt=prompt, model=model)
