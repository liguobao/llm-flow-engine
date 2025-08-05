#!/usr/bin/env python3
"""
LLM Flow Engine 演示示例
展示新架构的核心功能：
1. 自定义模型配置
2. DSL工作流执行
3. 多模型问答汇总
"""
import asyncio
import aiohttp
from loguru import logger
from llm_flow_engine import FlowEngine, ModelConfigProvider

async def demo_basic_usage():
    logger.info("🚀 LLM Flow Engine 演示")
    logger.info("=" * 50)
    
    # 1. 自定义模型配置
    logger.info("\n⚙️  1. 自定义模型配置")
    
    ollama_host = "http://192.168.50.57:11434"
    custom_models =await load_models_from_ollama(ollama_host)
    # 创建自定义配置提供者
    custom_provider = ModelConfigProvider(custom_models)
    engine = FlowEngine(custom_provider)
    # 查看支持的模型
    models = engine.model_provider.list_supported_models()
    total_models = sum(len(model_list) for model_list in models.values())
    logger.info(f"支持 {total_models} 个模型，涵盖 {len(models)} 个平台")

    # 2. 从本地文件读取DSL并执行多模型问答汇总
    logger.info("\n🤖 2. 本地Ollama模型问答汇总演示")
    logger.info("问题: 什么是人工智能？")
    logger.info("模型: gemma3:1b, qwen2.5:0.5b, deepseek-r1:1.5b")
    logger.info("方案: 三个小模型分别回答，然后用gemma3:4b汇总分析")
    
    try:
        # 读取本地DSL文件
        with open('./examples/demo_qa.yaml', 'r', encoding='utf-8') as f:
            dsl_content = f.read()

        logger.info("✅ 成功读取DSL文件: demo_qa.yaml")
        logger.info("🔄 开始调用本地Ollama模型...")

        # 准备工作流输入参数
        workflow_input = {
            "question": "什么是人工智能？"  # 用户实际的问题
        }
        
        # 执行多模型问答DSL
        qa_result = await engine.execute_dsl(dsl_content, inputs={"workflow_input": workflow_input})
        
        if qa_result['success']:
            print("✅ 多模型问答执行成功:")
            
            # 显示工作流元数据
            if 'metadata' in qa_result:
                metadata = qa_result['metadata']
                logger.info(f"\n📋 工作流信息:")
                logger.info(f"   版本: {metadata.get('version', '未指定')}")
                logger.info(f"   描述: {metadata.get('description', '未指定')}")

            # 显示各个模型的回答
            model_answers = []
            for name, exec_result in qa_result['results'].items():
                if exec_result.status == 'success':
                    if name.endswith('_answer'):
                        model_name = name.replace('_answer', '').replace('model', 'Model')
                        answer = exec_result.output
                        logger.info(f"\n📝 {model_name} 回答:")
                        # 截取回答的前200个字符用于显示
                        display_answer = answer[:200] + "..." if len(answer) > 200 else answer
                        logger.info(f"   {display_answer}")
                        model_answers.append(answer)
                    elif name == 'summary_step':
                        logger.info(f"\n🎯 gemma3:4b 汇总分析:")
                        summary_answer = exec_result.output
                        # 截取汇总的前300个字符用于显示
                        display_summary = summary_answer[:300] + "..." if len(summary_answer) > 300 else summary_answer
                        logger.info(f"   {display_summary}")
                else:
                    logger.error(f"  ❌ {name}: {exec_result.error}")

            # 显示工作流输出信息
            if 'output' in qa_result:
                logger.info(f"\n📤 工作流输出:")
                for key, value in qa_result['output'].items():
                    logger.info(f"   {key}: {value[:100]}..." if len(str(value)) > 100 else f"   {key}: {value}")

            logger.info(f"\n📊 执行统计: {len(model_answers)} 个模型成功回答，最后完成汇总")

        else:
            logger.error(f"❌ 多模型问答失败: {qa_result['error']}")

    except FileNotFoundError:
        logger.error("❌ 未找到DSL文件: demo_qa.yaml")
    except Exception as e:
        logger.error(f"❌ DSL执行出错: {str(e)}")

    logger.info("\n🎉 演示完成！")
    logger.info("核心特性展示:")
    logger.info("✅ 自定义模型配置管理")
    logger.info("✅ 本地DSL文件读取执行")
    logger.info("✅ 多模型并行/串行执行")
    logger.info("✅ 复杂依赖关系处理")
    logger.info("✅ 模拟LLM调用和结果汇总")

async def load_models_from_ollama(ollama_host):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{ollama_host}/v1/models") as resp:
            resp = await resp.json()
            model_items= resp.get("data",[])
    ollama_model_config = {
            'platform': 'ollama', 
            'api_url': f'{ollama_host}/api/chat',
            'auth_header': None,
            'message_format': 'ollama',
            'max_tokens': 2048,  # 适合1B模型的token限制
            'supports': ['temperature', 'top_k', 'top_p']
    }
    
    custom_models = {}
    for model_item in model_items:
        model_name = model_item["id"]
        custom_models[model_name] = ollama_model_config
    return custom_models

if __name__ == '__main__':
    asyncio.run(demo_basic_usage())
