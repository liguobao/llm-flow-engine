"""
流程控制和网络模块 - 条件控制、缓存管理、网络请求增强
"""
import time
import asyncio
import aiohttp
from typing import Any, Dict, List, Union
from loguru import logger


# =============================================================================
# 条件控制和流程控制
# =============================================================================

async def conditional_execute(condition: Any, true_value: Any = None, false_value: Any = None) -> Any:
    """条件执行"""
    if condition:
        return true_value
    return false_value


async def switch_case(value: Any, cases: Dict[Any, Any], default: Any = None) -> Any:
    """Switch-Case 逻辑"""
    return cases.get(value, default)


async def loop_execute(items: List[Any], operation: str, **kwargs) -> List[Any]:
    """循环执行操作"""
    results = []
    for item in items:
        # 这里可以根据operation参数执行不同的操作
        if operation == "upper" and isinstance(item, str):
            results.append(item.upper())
        elif operation == "lower" and isinstance(item, str):
            results.append(item.lower())
        elif operation == "multiply" and isinstance(item, (int, float)):
            multiplier = kwargs.get("multiplier", 2)
            results.append(item * multiplier)
        else:
            results.append(item)
    return results


# =============================================================================
# 缓存和状态管理
# =============================================================================

# 简单内存缓存
_memory_cache = {}


async def cache_set(key: str, value: Any, ttl: int = 3600) -> str:
    """设置缓存"""
    expire_time = time.time() + ttl
    _memory_cache[key] = {"value": value, "expire": expire_time}
    return f"缓存已设置: {key}"


async def cache_get(key: str, default: Any = None) -> Any:
    """获取缓存"""
    if key in _memory_cache:
        cache_item = _memory_cache[key]
        if time.time() < cache_item["expire"]:
            return cache_item["value"]
        else:
            # 清理过期缓存
            del _memory_cache[key]
    return default


async def cache_clear(key: str = None) -> str:
    """清理缓存"""
    if key:
        _memory_cache.pop(key, None)
        return f"缓存已清理: {key}"
    else:
        _memory_cache.clear()
        return "所有缓存已清理"


# =============================================================================
# 网络和API增强功能
# =============================================================================

async def http_request_with_retry(url: str, method: str = "GET", max_retries: int = 3, 
                                 retry_delay: float = 1.0, **kwargs) -> str:
    """带重试的HTTP请求"""
    from .core import http_request_get, http_request_post_json
    
    last_error = None
    
    for attempt in range(max_retries):
        try:
            if method.upper() == "GET":
                return await http_request_get(url, **kwargs)
            elif method.upper() == "POST":
                return await http_request_post_json(url, **kwargs)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                logger.warning(f"HTTP请求失败，第{attempt + 1}次重试: {e}")
                await asyncio.sleep(retry_delay)
            else:
                logger.error(f"HTTP请求最终失败: {e}")
                raise last_error


async def webhook_call(webhook_url: str, data: Dict, headers: Dict = None) -> str:
    """Webhook调用"""
    from .core import http_request_post_json
    
    default_headers = {"Content-Type": "application/json"}
    if headers:
        default_headers.update(headers)
    
    return await http_request_post_json(webhook_url, data=data, headers=default_headers)
