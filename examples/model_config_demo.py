#!/usr/bin/env python3
"""
模型配置演示示例
展示两种模型添加方式：
1. 通过 api_host + api_key + 平台自动发现模型
2. 手动添加单个模型的完整配置
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger
from llm_flow_engine import FlowEngine, ModelConfigProvider

logger.remove()
logger.add(sys.stderr, level="INFO")

async def demo_auto_discovery():
    """演示方式1：通过API主机自动发现模型"""
    logger.info("=== 方式1：通过API主机自动发现模型 ===")
    
    # 方法1：异步创建（推荐）
    logger.info("1.1 使用 from_host_async 方法（推荐）")
    try:
        provider1 = await ModelConfigProvider.from_host_async(
            api_host="http://localhost:11434",
            api_key="",  # Ollama通常不需要密钥
            platform="ollama"
        )
        
        models1 = provider1.list_supported_models()
        logger.info(f"自动发现的Ollama模型: {models1}")
    except Exception as e:
        logger.warning(f"Ollama连接失败: {e}")
    
    # 方法2：同步创建然后异步加载
    logger.info("\n1.2 同步创建然后异步加载")
    provider2 = ModelConfigProvider.from_host(
        api_host="http://localhost:11434",
        api_key="",
        platform="ollama"
    )
    
    try:
        await provider2.load_models_from_simple_config()
        models2 = provider2.list_supported_models()
        logger.info(f"异步加载的模型: {models2}")
    except Exception as e:
        logger.warning(f"异步加载失败: {e}")
    
    # 方法3：动态添加到现有提供者
    logger.info("\n1.3 动态添加到现有提供者")
    provider3 = ModelConfigProvider()
    logger.info(f"添加前的模型: {provider3.list_supported_models()}")
    
    try:
        await provider3.add_models_from_host(
            api_host="http://localhost:11434",
            api_key="",
            platform="ollama"
        )
        models3 = provider3.list_supported_models()
        logger.info(f"动态添加后的模型: {models3}")
    except Exception as e:
        logger.warning(f"动态添加失败: {e}")

def demo_single_model():
    """演示方式2：手动添加单个模型的完整配置"""
    logger.info("\n=== 方式2：手动添加单个模型配置 ===")
    
    # 创建基础提供者
    provider = ModelConfigProvider()
    logger.info(f"初始默认模型: {provider.list_supported_models()}")
    
    # 方法1：使用 add_single_model 方法
    logger.info("\n2.1 使用 add_single_model 方法添加OpenAI模型")
    provider.add_single_model(
        model_name="gpt-4",
        platform="openai",
        api_url="https://api.openai.com/v1/chat/completions",
        api_key="your-openai-key",
        auth_header="Bearer",
        message_format="openai",
        max_tokens=4096,
        supports=["temperature", "top_p", "frequency_penalty", "presence_penalty", "stop"]
    )
    
    # 方法2：添加DeepSeek模型
    logger.info("2.2 添加DeepSeek模型")
    provider.add_single_model(
        model_name="deepseek-chat",
        platform="openai_compatible",
        api_url="https://api.deepseek.com/v1/chat/completions",
        api_key="your-deepseek-key",
        auth_header="Bearer",
        message_format="openai",
        max_tokens=8192,
        supports=["temperature", "top_p", "frequency_penalty", "presence_penalty"]
    )
    
    # 方法3：添加本地自定义模型
    logger.info("2.3 添加本地自定义模型")
    provider.add_single_model(
        model_name="local-custom-llm",
        platform="custom",
        api_url="http://192.168.1.100:8080/v1/chat/completions",
        api_key="custom-token",
        auth_header="Bearer",
        message_format="openai",
        max_tokens=2048,
        supports=["temperature", "top_p"]
    )
    
    # 显示最终的模型列表
    final_models = provider.list_supported_models()
    logger.info(f"\n添加完成后的所有模型: {final_models}")
    
    # 获取特定模型配置
    gpt4_config = provider.get_model_config("gpt-4")
    logger.info(f"GPT-4模型配置: {gpt4_config}")
    
    return provider

def demo_mixed_usage():
    """演示混合使用两种方式"""
    logger.info("\n=== 混合使用演示 ===")
    
    # 先创建基础提供者
    provider = ModelConfigProvider()
    logger.info(f"初始模型: {provider.list_supported_models()}")
    
    # 方式2：添加几个自定义模型
    provider.add_single_model(
        model_name="claude-3",
        platform="anthropic",
        api_url="https://api.anthropic.com/v1/messages",
        api_key="your-anthropic-key",
        auth_header="x-api-key",
        message_format="anthropic",
        max_tokens=4096,
        supports=["temperature", "top_p", "max_tokens"]
    )
    
    logger.info("已添加Claude-3模型")
    
    # 检查所有配置
    all_models = provider.list_supported_models()
    logger.info(f"混合配置后的所有模型: {all_models}")
    
    # 验证各平台模型数量
    for platform, models in all_models.items():
        logger.info(f"{platform} 平台: {len(models)} 个模型")
    
    return provider

async def demo_with_flow_engine():
    """演示与FlowEngine的集成使用"""
    logger.info("\n=== 与FlowEngine集成演示 ===")
    
    # 方式1：自动发现模型
    try:
        provider = await ModelConfigProvider.from_host_async(
            api_host="http://localhost:11434",
            platform="ollama"
        )
        
        # 方式2：添加额外的自定义模型
        provider.add_single_model(
            model_name="test-gpt",
            platform="test",
            api_url="https://test-api.com/v1/chat/completions",
            api_key="test-key",
            max_tokens=2048
        )
        
        # 创建FlowEngine
        engine = FlowEngine(provider)
        logger.info("✅ FlowEngine创建成功")
        
        # 显示引擎支持的模型
        supported_models = engine.model_provider.list_supported_models()
        logger.info(f"FlowEngine支持的模型: {supported_models}")
        
    except Exception as e:
        logger.warning(f"FlowEngine集成演示失败: {e}")

async def main():
    """主函数"""
    logger.info("模型配置演示开始")
    logger.info("=" * 60)
    
    # 方式1：自动发现模型演示
    await demo_auto_discovery()
    
    # 方式2：手动添加单个模型演示
    demo_single_model()
    
    # 混合使用演示
    demo_mixed_usage()
    
    # 与FlowEngine集成演示
    await demo_with_flow_engine()
    
    logger.info("\n" + "=" * 60)
    logger.info("模型配置演示完成")
    logger.info("\n📝 总结:")
    logger.info("   方式1: 通过 api_host + api_key + 平台 自动发现模型")
    logger.info("   方式2: 手动添加单个模型的完整配置")
    logger.info("   两种方式可以混合使用，灵活配置各种模型")

if __name__ == '__main__':
    asyncio.run(main())
