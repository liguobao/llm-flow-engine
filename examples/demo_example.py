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
import time
from loguru import logger
from llm_flow_engine import FlowEngine, ModelConfigProvider
import sys
logger.remove()
logger.add(sys.stderr, level="INFO")

async def demo_basic_usage():
    logger.info("LLM Flow Engine 演示")
    logger.info("=" * 50)
    
    # 1. 自定义模型配置
    logger.info("1. 自定义模型配置")
    # ollama pull gemma3:1b
    # ollama pull qwen2.5:0.5b
    # ollama pull gemma3:4b
    # ollama pull deepseek-r1:7b
    ollama_host = "http://127.0.0.1:11434"
    custom_models = await load_models_from_ollama(ollama_host)
    logger.info(f"成功加载 {len(custom_models)} 个模型配置")
    
    # 创建自定义配置提供者
    custom_provider = ModelConfigProvider(custom_models)
    engine = FlowEngine(custom_provider)
    
    # 查看支持的模型
    models = engine.model_provider.list_supported_models()
    total_models = sum(len(model_list) for model_list in models.values())
    logger.info(f"支持 {total_models} 个模型，涵盖 {len(models)} 个平台")
    
    # 显示可用模型列表
    for platform, model_list in models.items():
        if model_list:
            logger.info(f"  {platform}: {', '.join(model_list[:5])}{'...' if len(model_list) > 5 else ''}")

    # 2. 从本地文件读取DSL并执行多模型问答汇总
    logger.info("2. 本地Ollama模型问答汇总演示")
    logger.info("问题: 什么是人工智能？")
    logger.info("模型: gemma3:1b, qwen2.5:0.5b")
    logger.info("方案: 两个小模型分别回答，然后用gemma3:1b进行汇总分析")

    try:
        # 读取本地DSL文件
        logger.info("读取DSL配置文件...")
        with open('./examples/demo_qa.yaml', 'r', encoding='utf-8') as f:
            dsl_content = f.read()

        logger.info("成功读取DSL文件: demo_qa.yaml")
        logger.info("开始调用本地Ollama模型...")

        # 准备工作流输入参数
        workflow_input = {
            "question": "什么是人工智能？"  # 用户实际的问题
        }
        
        logger.info(f"工作流输入参数: {workflow_input}")
        
        # 展示执行计划
        logger.info("工作流执行计划:")
        logger.info("  1. text_processing - 文本预处理")
        logger.info("  2. model1_answer - gemma3:1b 模型回答")
        logger.info("  3. model2_answer - qwen2.5:0.5b 模型回答") 
        logger.info("  4. deep_analysis - gemma3:1b 深度分析汇总")
        logger.info("  5. workflow_output - 生成最终输出")
        
        start_time = time.time()
        
        # 执行多模型问答DSL
        logger.info("开始执行工作流...")
        qa_result = await engine.execute_dsl(dsl_content, inputs={"workflow_input": workflow_input})
        
        execution_time = time.time() - start_time
        logger.info(f"工作流总执行时间: {execution_time:.2f}秒")
        
        if qa_result['success']:
            logger.info("多模型问答执行成功!")
            
            # 显示工作流元数据
            if 'metadata' in qa_result:
                metadata = qa_result['metadata']
                logger.info(f"工作流信息:")
                logger.info(f"   版本: {metadata.get('version', '未指定')}")
                logger.info(f"   描述: {metadata.get('description', '未指定')}")

            # 按执行顺序显示每一步的详细结果
            logger.info(f"详细执行步骤结果:")
            
            # 1. 文本处理步骤
            if 'text_processing' in qa_result['results']:
                text_result = qa_result['results']['text_processing']
                logger.info(f"步骤1: 文本处理")
                logger.info(f"   状态: {'成功' if text_result.status == 'success' else '失败'}")
                if text_result.status == 'success':
                    logger.info(f"   输入: {workflow_input['question']}")
                    logger.info(f"   输出: {text_result.output}")
                    logger.info(f"   耗时: {text_result.exec_time:.3f}秒")
                else:
                    logger.error(f"   错误: {text_result.error}")

            # 2. 模型回答步骤
            model_answers = []
            step_num = 2
            for name, exec_result in qa_result['results'].items():
                if name.endswith('_answer'):
                    model_name = name.replace('_answer', '').replace('model', 'Model')
                    logger.info(f"步骤{step_num}: {model_name} 回答")
                    logger.info(f"   状态: {'成功' if exec_result.status == 'success' else '失败'}")
                    
                    if exec_result.status == 'success':
                        answer = exec_result.output
                        logger.info(f"   模型: {exec_result.custom_vars.get('model', '未知')}")
                        logger.info(f"   耗时: {exec_result.exec_time:.3f}秒")
                        logger.info(f"   回答长度: {len(answer)} 字符")
                        logger.info(f"   回答内容: {answer}")
                        model_answers.append(answer)
                    else:
                        logger.error(f"   错误: {exec_result.error}")
                    step_num += 1

            # 3. 深度分析步骤
            if 'deep_analysis' in qa_result['results']:
                analysis_result = qa_result['results']['deep_analysis']
                logger.info(f"步骤{step_num}: 深度分析")
                logger.info(f"   状态: {'成功' if analysis_result.status == 'success' else '失败'}")
                
                if analysis_result.status == 'success':
                    logger.info(f"   模型: {analysis_result.custom_vars.get('model', '未知')}")
                    logger.info(f"   耗时: {analysis_result.exec_time:.3f}秒")
                    logger.info(f"   分析结果: {analysis_result.output}")
                else:
                    logger.error(f"   错误: {analysis_result.error}")

            # 4. 最终输出结果
            if 'workflow_output' in qa_result['results']:
                output_result = qa_result['results']['workflow_output']
                logger.info(f"� 最终工作流输出:")
                logger.info(f"   状态: {'成功' if output_result.status == 'success' else '失败'}")
                
                if output_result.status == 'success' and hasattr(output_result, 'output') and isinstance(output_result.output, dict):
                    output_data = output_result.output
                    logger.info(f"   原始问题: {output_data.get('original_question', 'N/A')}")
                    logger.info(f"   处理后问题: {output_data.get('processed_question', 'N/A')}")
                    
                    if 'model_answers' in output_data:
                        logger.info(f"   模型回答汇总:")
                        for model, answer in output_data['model_answers'].items():
                            logger.info(f"     - {model}: {answer[:100]}{'...' if len(answer) > 100 else ''}")
                    
                    if 'summary' in output_data:
                        logger.info(f"   综合总结: {output_data['summary']}")

            # 执行统计
            total_steps = len(qa_result['results'])
            success_steps = sum(1 for result in qa_result['results'].values() if result.status == 'success')
            total_time = sum(result.exec_time for result in qa_result['results'].values() if hasattr(result, 'exec_time'))
            
            logger.info(f"执行统计:")
            logger.info(f"   总步骤数: {total_steps}")
            logger.info(f"   成功步骤: {success_steps}")
            logger.info(f"   失败步骤: {total_steps - success_steps}")
            logger.info(f"   总耗时: {total_time:.3f}秒")
            logger.info(f"   成功率: {(success_steps/total_steps*100):.1f}%")

        else:
            logger.error(f" 多模型问答失败: {qa_result.get('error', '未知错误')}")
            
            # 显示失败的步骤详情
            if 'results' in qa_result:
                logger.info(" 失败步骤详情:")
                for name, result in qa_result['results'].items():
                    if result.status != 'success':
                        logger.error(f"   {name}: {result.error}")
                    else:
                        logger.info(f"   {name}: 执行成功")

    except FileNotFoundError:
        logger.error(" 未找到DSL文件: demo_qa.yaml")
        logger.info(" 请确保当前目录下存在 ./examples/demo_qa.yaml 文件")
    except Exception as e:
        logger.error(f" DSL执行出错: {str(e)}")
        logger.error(f"📍 错误类型: {type(e).__name__}")

    logger.info("" + "="*60)
    logger.info("🎉 演示完成！")
    logger.info("📖 核心特性展示:")
    logger.info(" 自定义模型配置管理")
    logger.info(" 本地DSL文件读取执行")
    logger.info(" 多模型并行/串行执行")
    logger.info(" 复杂依赖关系处理")
    logger.info(" 详细执行步骤追踪")
    logger.info(" 完整的错误处理机制")
    logger.info(" 提示: 查看上面的详细日志了解每个步骤的执行情况")

async def load_models_from_ollama(ollama_host):
    """从Ollama服务器加载模型配置"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{ollama_host}/v1/models") as resp:
                if resp.status != 200:
                    logger.error(f" 连接Ollama失败，状态码: {resp.status}")
                    return {}
                    
                resp_data = await resp.json()
                model_items = resp_data.get("data", [])
                
        logger.info(f" 成功获取 {len(model_items)} 个可用模型")
        
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
        
    except Exception as e:
        logger.error(f" 加载Ollama模型配置失败: {str(e)}")
        return {}

if __name__ == '__main__':
    asyncio.run(demo_basic_usage())
