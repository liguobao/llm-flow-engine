"""
文本和数据处理模块 - 正则表达式、字符串处理、数据验证转换
"""
import re
import base64
import hashlib
import uuid
from typing import Any, Dict, List, Union
from loguru import logger


# =============================================================================
# 字符串处理和正则表达式
# =============================================================================

async def regex_extract(text: str, pattern: str, group: int = 0) -> Union[str, List[str]]:
    """正则表达式提取"""
    matches = re.findall(pattern, text)
    if not matches:
        return ""
    return matches if len(matches) > 1 else matches[0]


async def regex_replace(text: str, pattern: str, replacement: str) -> str:
    """正则表达式替换"""
    return re.sub(pattern, replacement, text)


async def string_template(template: str, variables: Dict[str, Any]) -> str:
    """字符串模板格式化（支持更复杂的模板语法）"""
    try:
        return template.format(**variables)
    except KeyError as e:
        logger.warning(f"模板变量缺失: {e}")
        return template


async def text_similarity(text1: str, text2: str, method: str = "jaccard") -> float:
    """文本相似度计算"""
    if method == "jaccard":
        set1 = set(text1.split())
        set2 = set(text2.split())
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union > 0 else 0.0
    # 可以扩展其他相似度算法
    return 0.0


# =============================================================================
# 数据验证和转换
# =============================================================================

async def validate_email(email: str) -> bool:
    """邮箱格式验证"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


async def validate_url(url: str) -> bool:
    """URL格式验证"""
    pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.]*))?(?:#(?:[\w.]*))?)?$'
    return bool(re.match(pattern, url))


async def data_type_convert(value: Any, target_type: str) -> Any:
    """数据类型转换"""
    import json as pyjson
    
    try:
        if target_type == "int":
            return int(value)
        elif target_type == "float":
            return float(value)
        elif target_type == "str":
            return str(value)
        elif target_type == "bool":
            if isinstance(value, str):
                return value.lower() in ("true", "yes", "1", "on")
            return bool(value)
        elif target_type == "list":
            if isinstance(value, str):
                return pyjson.loads(value) if value.startswith('[') else value.split(',')
            return list(value)
        elif target_type == "dict":
            if isinstance(value, str):
                return pyjson.loads(value)
            return dict(value)
        else:
            return value
    except Exception as e:
        logger.error(f"类型转换失败: {value} -> {target_type}, 错误: {e}")
        return value


# =============================================================================
# 加密和编码
# =============================================================================

async def base64_encode(text: str) -> str:
    """Base64 编码"""
    return base64.b64encode(text.encode('utf-8')).decode('utf-8')


async def base64_decode(encoded_text: str) -> str:
    """Base64 解码"""
    return base64.b64decode(encoded_text).decode('utf-8')


async def hash_text(text: str, algorithm: str = "sha256") -> str:
    """文本哈希"""
    if algorithm == "md5":
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    elif algorithm == "sha1":
        return hashlib.sha1(text.encode('utf-8')).hexdigest()
    elif algorithm == "sha256":
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    else:
        raise ValueError(f"不支持的哈希算法: {algorithm}")


async def generate_uuid(version: int = 4) -> str:
    """生成UUID"""
    if version == 1:
        return str(uuid.uuid1())
    elif version == 4:
        return str(uuid.uuid4())
    else:
        raise ValueError(f"不支持的UUID版本: {version}")
