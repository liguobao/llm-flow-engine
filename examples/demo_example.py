#!/usr/bin/env python3
"""
LLM Flow Engine 使用演示 - 三步上手
"""
import asyncio
import time
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger
from llm_flow_engine import FlowEngine, ModelConfigProvider

logger.remove()
logger.add(sys.stderr, level="INFO")

async def demo_basic_usage():
    """演示如何使用 LLM Flow Engine"""
    logger.info("🚀 LLM Flow Engine 演示")
    logger.info("=" * 40)
    
    # 第1步: 配置模型
    logger.info("第1步: 配置模型")
    
    # 自动发现本地Ollama模型
    model_provider = await ModelConfigProvider.from_host_async(
        api_host="http://127.0.0.1:11434", 
        platform="ollama"
    )
    
    # (可选) 手动添加其他模型
    model_provider.add_single_model(
        model_name="gpt-4",
        platform="openai", 
        api_url="https://api.openai.com/v1/chat/completions",
        api_key="your-api-key",  # 替换为真实API key
        max_tokens=4096
    )
    
    engine = FlowEngine(model_provider)
    models = engine.model_provider.list_supported_models()
    total = sum(len(models[p]) for p in models)
    logger.info(f"✅ 已配置 {total} 个模型")

    # 第2步: 执行工作流
    logger.info("第2步: 执行工作流")
    
    dsl_file = './examples/demo_qa.yaml'
    if not os.path.exists(dsl_file):
        logger.error(f"❌ 找不到文件: {dsl_file}")
        return

    with open(dsl_file, 'r', encoding='utf-8') as f:
        dsl_content = f.read()
    
    # 输入问题
    question = "什么是人工智能？"
    logger.info(f"❓ 问题: {question}")
    
    # 执行
    start = time.time()
    flow_result = await engine.execute_dsl(
        dsl_content, 
        inputs={"workflow_input": {"question": question}}
    )
    logger.info(f"⏱️  用时: {time.time() - start:.1f}秒")
    
    # 第3步: 查看结果
    logger.info("第3步: 查看结果")
    
    if flow_result['success']:
        logger.info("✅ 执行成功!")
        # 显示工作流最终输出
        if 'workflow_output' in flow_result['results']:
            output_step = flow_result['results']['workflow_output']
            if output_step.status == 'success':
                logger.info(f"📝 最终结果: {output_step.output}")
            else:
                logger.error(f"❌ 工作流输出失败: {output_step.error}")
        # 统计
        success = sum(1 for r in flow_result['results'].values() if r.status == 'success')
        total = len(flow_result['results'])
        logger.info(f"📊 {success}/{total} 步骤成功")
    else:
        logger.error(f"❌ 失败: {flow_result.get('error', '未知错误')}")

    logger.info("=" * 40)
    logger.info("🎉 演示完成!")
    logger.info("� 核心方法:")
    logger.info("   • ModelConfigProvider.from_host_async() - 自动配置")
    logger.info("   • provider.add_single_model() - 手动添加")  
    logger.info("   • engine.execute_dsl() - 执行工作流")

if __name__ == '__main__':
    asyncio.run(demo_basic_usage())
