"""
文件和时间处理模块 - 文件操作和时间日期处理
"""
import os
import fnmatch
from datetime import datetime, timedelta
from typing import List, Union
from loguru import logger


# =============================================================================
# 文件和存储操作
# =============================================================================

async def file_read(file_path: str, encoding: str = 'utf-8', **kwargs) -> str:
    """读取文件内容"""
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            content = f.read()
        logger.debug(f"成功读取文件: {file_path}")
        return content
    except Exception as e:
        logger.error(f"读取文件失败 {file_path}: {e}")
        raise


async def file_write(file_path: str, content: str, encoding: str = 'utf-8', mode: str = 'w', **kwargs) -> str:
    """写入文件内容"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, mode, encoding=encoding) as f:
            f.write(content)
        logger.debug(f"成功写入文件: {file_path}")
        return f"文件已写入: {file_path}"
    except Exception as e:
        logger.error(f"写入文件失败 {file_path}: {e}")
        raise


async def file_append(file_path: str, content: str, encoding: str = 'utf-8') -> str:
    """追加文件内容"""
    return await file_write(file_path, content, encoding, 'a')


async def file_exists(file_path: str) -> bool:
    """检查文件是否存在"""
    return os.path.exists(file_path)


async def list_directory(dir_path: str, pattern: str = None) -> List[str]:
    """列出目录内容，可选择性过滤"""
    try:
        files = os.listdir(dir_path)
        if pattern:
            files = [f for f in files if fnmatch.fnmatch(f, pattern)]
        return files
    except Exception as e:
        logger.error(f"列出目录失败 {dir_path}: {e}")
        raise


# =============================================================================
# 时间和日期处理
# =============================================================================

async def get_current_time(format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """获取当前时间"""
    return datetime.now().strftime(format_str)


async def date_calculate(base_date: str = None, days: int = 0, hours: int = 0, 
                        minutes: int = 0, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """日期计算"""
    if base_date:
        base = datetime.strptime(base_date, format_str)
    else:
        base = datetime.now()
    
    result = base + timedelta(days=days, hours=hours, minutes=minutes)
    return result.strftime(format_str)


async def timestamp_to_date(timestamp: Union[int, float], format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """时间戳转日期"""
    return datetime.fromtimestamp(timestamp).strftime(format_str)


async def date_to_timestamp(date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> float:
    """日期转时间戳"""
    return datetime.strptime(date_str, format_str).timestamp()
