"""
LLM模型配置数据提供者
支持多平台模型的统一配置管理
"""

# 默认模型配置 - 精简版，主要使用本地ollama模型
DEFAULT_MODEL_PROVIDERS = {
    # Ollama本地模型配置 - 主要模型
    "gemma3:4b": {
        "platform": "ollama",
        "api_url": "http://localhost:11434/api/chat",
        "auth_header": None,
        "message_format": "ollama",
        "max_tokens": 8192,
        "supports": ["temperature", "top_p", "top_k"]
    },
    "qwen2.5": {
        "platform": "ollama",
        "api_url": "http://localhost:11434/api/chat",
        "auth_header": None,
        "message_format": "ollama",
        "max_tokens": 8192,
        "supports": ["temperature", "top_p", "top_k"]
    },
    "gemma2": {
        "platform": "ollama",
        "api_url": "http://localhost:11434/api/chat",
        "auth_header": None,
        "message_format": "ollama",
        "max_tokens": 8192,
        "supports": ["temperature", "top_p", "top_k"]
    },
    # 备用轻量级模型
    "phi3": {
        "platform": "ollama",
        "api_url": "http://localhost:11434/api/chat",
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
            custom_providers: 自定义模型配置，会与默认配置合并
        """
        self.providers = DEFAULT_MODEL_PROVIDERS.copy()
        if custom_providers:
            self.providers.update(custom_providers)
    
    def get_model_config(self, model: str) -> dict:
        """获取模型配置"""
        if model in self.providers:
            return self.providers[model]
        else:
            # 如果模型不在配置中，返回OpenAI兼容的默认配置
            return {
                "platform": "openai_compatible",
                "api_url": "https://api.openai.com/v1/chat/completions",
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
