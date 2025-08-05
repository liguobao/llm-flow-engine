"""
LLM模型配置数据提供者
支持多平台模型的统一配置管理
支持两种配置格式：
1. 简化配置：api_host + api_key，自动发现模型
2. 完整配置：详细的模型配置信息
"""
import asyncio
import aiohttp
import json
from typing import Dict, List, Optional, Union
from loguru import logger

# 默认模型配置 - 精简版，主要使用本地ollama模型
DEFAULT_MODEL_PROVIDERS = {
    # Ollama本地模型配置 - 主要模型
    "gemma3:4b": {
        "platform": "ollama",
        "api_url": "http://localhost:11434/api/chat",
        "api_key": None,  # Ollama本地模型不需要API key
        "auth_header": None,
        "message_format": "ollama",
        "max_tokens": 8192,
        "supports": ["temperature", "top_p", "top_k"]
    },
    "qwen2.5": {
        "platform": "ollama",
        "api_url": "http://localhost:11434/api/chat",
        "api_key": None,  # Ollama本地模型不需要API key
        "auth_header": None,
        "message_format": "ollama",
        "max_tokens": 8192,
        "supports": ["temperature", "top_p", "top_k"]
    },
    "gemma2": {
        "platform": "ollama",
        "api_url": "http://localhost:11434/api/chat",
        "api_key": None,  # Ollama本地模型不需要API key
        "auth_header": None,
        "message_format": "ollama",
        "max_tokens": 8192,
        "supports": ["temperature", "top_p", "top_k"]
    },
    # 备用轻量级模型
    "phi3": {
        "platform": "ollama",
        "api_url": "http://localhost:11434/api/chat",
        "api_key": None,  # Ollama本地模型不需要API key
        "auth_header": None,
        "message_format": "ollama",
        "max_tokens": 4096,
        "supports": ["temperature", "top_p", "top_k"]
    }
}

class ModelConfigProvider:
    """模型配置提供者"""
    
    def __init__(self, custom_providers: dict = None):
        """
        初始化模型配置提供者
        
        Args:
            custom_providers: 自定义模型配置，支持两种格式：
                1. 简化格式: {"api_host": "http://...", "api_key": "key", "platform": "..."}
                2. 完整格式: {"model_name": {"platform": "...", "api_url": "...", ...}}
        """
        self.providers = DEFAULT_MODEL_PROVIDERS.copy()
        if custom_providers:
            # 检查是否为简化配置格式
            if self._is_simple_config(custom_providers):
                # 简化配置暂时跳过网络请求，需要调用 load_models_from_simple_config
                logger.info("检测到简化配置格式，请调用 load_models_from_simple_config() 方法加载模型")
                self._simple_config = custom_providers
            else:
                # 完整配置格式 - 直接添加单个模型
                self.providers.update(custom_providers)
    
    async def load_models_from_simple_config(self):
        """异步加载简化配置中的模型"""
        if hasattr(self, '_simple_config'):
            models = await self._load_models_from_host(self._simple_config)
            self.providers.update(models)
            delattr(self, '_simple_config')
    
    @classmethod
    async def from_host_async(cls, api_host: str, api_key: str = "", platform: str = "openai_compatible"):
        """
        异步方式从API主机创建模型配置提供者（自动发现模型）
        
        Args:
            api_host: API主机地址
            api_key: API密钥
            platform: 平台类型
        """
        config = {
            "api_host": api_host,
            "api_key": api_key,
            "platform": platform
        }
        provider = cls()
        models = await provider._load_models_from_host(config)
        provider.providers.update(models)
        return provider
    
    @classmethod
    def from_host(cls, api_host: str, api_key: str = "", platform: str = "openai_compatible"):
        """
        从API主机创建模型配置提供者（需要手动调用load_models_from_simple_config）
        
        Args:
            api_host: API主机地址
            api_key: API密钥
            platform: 平台类型
        """
        config = {
            "api_host": api_host,
            "api_key": api_key,
            "platform": platform
        }
        return cls(config)
    
    def add_single_model(self, model_name: str, platform: str, api_url: str, 
                        api_key: str = None, auth_header: str = "Bearer", 
                        message_format: str = "openai", max_tokens: int = 4096,
                        supports: list = None):
        """
        添加单个模型的完整配置
        
        Args:
            model_name: 模型名称
            platform: 平台类型
            api_url: API地址
            api_key: API密钥
            auth_header: 认证头类型
            message_format: 消息格式
            max_tokens: 最大token数
            supports: 支持的参数列表
        """
        if supports is None:
            supports = ["temperature", "top_p"]
        
        config = {
            "platform": platform,
            "api_url": api_url,
            "api_key": api_key,
            "auth_header": auth_header,
            "message_format": message_format,
            "max_tokens": max_tokens,
            "supports": supports
        }
        
        self.providers[model_name] = config
        logger.info(f"已添加模型配置: {model_name} ({platform})")
    

    
    def _is_simple_config(self, config: dict) -> bool:
        """判断是否为简化配置格式"""
        return "api_host" in config and ("api_key" in config or "platform" in config)
    
    async def _load_models_from_host(self, config: dict) -> dict:
        """
        从API主机加载模型列表
        
        Args:
            config: 包含api_host、api_key等信息的配置
        """
        api_host = config["api_host"]
        api_key = config.get("api_key", "")
        platform = config.get("platform", "openai_compatible")
        
        try:
            # 构建请求头
            headers = {}
            if api_key:
                if platform == "ollama":
                    # Ollama通常不需要认证头
                    pass
                else:
                    # 默认使用Bearer认证
                    headers["Authorization"] = f"Bearer {api_key}"
            
            # 请求模型列表
            models_url = f"{api_host.rstrip('/')}/v1/models"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(models_url, headers=headers) as resp:
                    if resp.status != 200:
                        logger.error(f"获取模型列表失败，状态码: {resp.status}")
                        return {}
                    
                    resp_data = await resp.json()
                    model_items = resp_data.get("data", [])
            
            logger.info(f"成功获取 {len(model_items)} 个可用模型")
            
            # 根据平台生成基础配置
            base_config = self._get_base_config_for_platform(platform, api_host, api_key)
            
            # 为每个模型生成配置
            custom_models = {}
            for model_item in model_items:
                model_name = model_item.get("id", model_item.get("name", ""))
                if model_name:
                    model_config = base_config.copy()
                    # 添加模型特定信息
                    if "model" not in model_config:
                        model_config["model"] = model_name
                    custom_models[model_name] = model_config
            
            return custom_models
            
        except Exception as e:
            logger.error(f"加载模型配置失败: {str(e)}")
            return {}
    
    def _get_base_config_for_platform(self, platform: str, api_host: str, api_key: str) -> dict:
        """根据平台获取基础配置"""
        base_configs = {
            "ollama": {
                "platform": "ollama",
                "api_url": f"{api_host.rstrip('/')}/api/chat",
                "api_key": None,
                "auth_header": None,
                "message_format": "ollama",
                "max_tokens": 4096,
                "supports": ["temperature", "top_k", "top_p"]
            },
            "openai_compatible": {
                "platform": "openai_compatible",
                "api_url": f"{api_host.rstrip('/')}/v1/chat/completions",
                "api_key": api_key,
                "auth_header": "Bearer",
                "message_format": "openai",
                "max_tokens": 4096,
                "supports": ["temperature", "top_p", "frequency_penalty", "presence_penalty", "stop"]
            },
            "openai": {
                "platform": "openai",
                "api_url": f"{api_host.rstrip('/')}/v1/chat/completions",
                "api_key": api_key,
                "auth_header": "Bearer", 
                "message_format": "openai",
                "max_tokens": 4096,
                "supports": ["temperature", "top_p", "frequency_penalty", "presence_penalty", "stop"]
            }
        }
        
        return base_configs.get(platform, base_configs["openai_compatible"])
    
    async def add_models_from_host(self, api_host: str, api_key: str = "", platform: str = "openai_compatible"):
        """
        从API主机添加模型配置
        
        Args:
            api_host: API主机地址
            api_key: API密钥
            platform: 平台类型
        """
        config = {
            "api_host": api_host,
            "api_key": api_key,
            "platform": platform
        }
        models = await self._load_models_from_host(config)
        self.providers.update(models)
    
    def get_model_config(self, model: str) -> dict:
        """获取模型配置"""
        if model in self.providers:
            return self.providers[model]
        else:
            # 如果模型不在配置中，返回OpenAI兼容的默认配置
            return {
                "platform": "openai_compatible",
                "api_url": "https://api.openai.com/v1/chat/completions",
                "api_key": None,  # 需要用户自行配置
                "auth_header": "Bearer",
                "message_format": "openai",
                "max_tokens": 4096,
                "supports": ["temperature", "top_p", "frequency_penalty", "presence_penalty", "stop"]
            }
    
    def list_supported_models(self) -> dict:
        """列出所有支持的模型，按平台分组"""
        models_by_platform = {}
        for model, config in self.providers.items():
            platform = config["platform"]
            if platform not in models_by_platform:
                models_by_platform[platform] = []
            models_by_platform[platform].append(model)
        return models_by_platform
    
    def add_model(self, model_name: str, config: dict):
        """添加新模型配置"""
        required_fields = ["platform", "api_url", "message_format", "max_tokens", "supports"]
        for field in required_fields:
            if field not in config:
                raise ValueError(f"模型配置缺少必需字段: {field}")
        
        self.providers[model_name] = config
    
    def remove_model(self, model_name: str):
        """移除模型配置"""
        if model_name in self.providers:
            del self.providers[model_name]
    
    def update_model(self, model_name: str, config: dict):
        """更新模型配置"""
        if model_name in self.providers:
            self.providers[model_name].update(config)
        else:
            self.add_model(model_name, config)
    
    def get_platforms(self) -> list:
        """获取所有支持的平台"""
        platforms = set()
        for config in self.providers.values():
            platforms.add(config["platform"])
        return list(platforms)
    
    def get_models_by_platform(self, platform: str) -> list:
        """获取指定平台的所有模型"""
        models = []
        for model, config in self.providers.items():
            if config["platform"] == platform:
                models.append(model)
        return models

# 全局默认配置提供者实例
default_model_provider = ModelConfigProvider()

# 便捷函数，使用全局配置
def get_model_config(model: str) -> dict:
    """获取模型配置 - 使用全局配置"""
    return default_model_provider.get_model_config(model)

def list_supported_models() -> dict:
    """列出所有支持的模型 - 使用全局配置"""
    return default_model_provider.list_supported_models()

def add_global_model(model_name: str, config: dict):
    """添加全局模型配置"""
    default_model_provider.add_model(model_name, config)

def set_global_model_provider(provider: ModelConfigProvider):
    """设置全局模型配置提供者"""
    global default_model_provider
    default_model_provider = provider

def create_provider_from_host(api_host: str, api_key: str = "", platform: str = "openai_compatible") -> ModelConfigProvider:
    """
    便捷函数：从API主机创建模型配置提供者
    
    Args:
        api_host: API主机地址
        api_key: API密钥
        platform: 平台类型（ollama, openai, openai_compatible）
    
    Returns:
        ModelConfigProvider: 配置提供者实例
    """
    return ModelConfigProvider.from_host(api_host, api_key, platform)

async def add_global_models_from_host(api_host: str, api_key: str = "", platform: str = "openai_compatible"):
    """
    便捷函数：向全局配置添加来自API主机的模型
    
    Args:
        api_host: API主机地址 
        api_key: API密钥
        platform: 平台类型
    """
    await default_model_provider.add_models_from_host(api_host, api_key, platform)

def add_global_single_model(model_name: str, platform: str, api_url: str, 
                           api_key: str = None, auth_header: str = "Bearer",
                           message_format: str = "openai", max_tokens: int = 4096,
                           supports: list = None):
    """
    便捷函数：向全局配置添加单个模型
    
    Args:
        model_name: 模型名称
        platform: 平台类型
        api_url: API地址
        api_key: API密钥
        auth_header: 认证头类型
        message_format: 消息格式
        max_tokens: 最大token数
        supports: 支持的参数列表
    """
    default_model_provider.add_single_model(
        model_name, platform, api_url, api_key, auth_header, 
        message_format, max_tokens, supports
    )
