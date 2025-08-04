#!/usr/bin/env python3
"""
LLM Flow Engine 演示示例
展示新架构的核心功能：
1. 自定义模型配置
2. DSL工作流执行
3. 多模型问答汇总
"""
import asyncio
from llm_flow_engine import FlowEngine, ModelConfigProvider

async def demo_basic_usage():
    print("🚀 LLM Flow Engine 演示")
    print("=" * 50)
    
    # 1. 自定义模型配置
    print("\n⚙️  1. 自定义模型配置")
    
    custom_models = {
        'gemma3:1b': {
            'platform': 'ollama', 
            'api_url': 'http://localhost:11434/api/chat',
            'auth_header': None,
            'message_format': 'ollama',
            'max_tokens': 8000,
            'supports': ['temperature', 'top_k', 'top_p']
        }
    }
    
    # 创建自定义配置提供者
    custom_provider = ModelConfigProvider(custom_models)
    engine = FlowEngine(custom_provider)
    
    # 查看支持的模型
    models = engine.model_provider.list_supported_models()
    total_models = sum(len(model_list) for model_list in models.values())
    print(f"支持 {total_models} 个模型，涵盖 {len(models)} 个平台")
    
    # 2. 从本地文件读取DSL并执行多模型问答汇总
    print("\n🤖 2. 本地Ollama模型问答汇总演示")
    print("问题: 什么是人工智能？")
    print("模型: gemma3:4b, qwen3:8b, gemma3:12b")
    print("方案: 三个模型分别回答，然后用gemma3:12b汇总")
    
    try:
        # 读取本地DSL文件
        with open('demo_qa.yaml', 'r', encoding='utf-8') as f:
            dsl_content = f.read()
        
        print("✅ 成功读取DSL文件: demo_qa.yaml")
        print("🔄 开始调用本地Ollama模型...")
        
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
                print(f"\n📋 工作流信息:")
                print(f"   版本: {metadata.get('version', '未指定')}")
                print(f"   描述: {metadata.get('description', '未指定')}")

            # 显示各个模型的回答
            model_answers = []
            for name, exec_result in qa_result['results'].items():
                if exec_result.status == 'success':
                    if name.endswith('_answer'):
                        model_name = name.replace('_answer', '').replace('model', 'Model')
                        answer = exec_result.output
                        print(f"\n📝 {model_name} 回答:")
                        # 截取回答的前200个字符用于显示
                        display_answer = answer[:200] + "..." if len(answer) > 200 else answer
                        print(f"   {display_answer}")
                        model_answers.append(answer)
                    elif name == 'summary_step':
                        print(f"\n🎯 gemma3:12b 汇总分析:")
                        summary_answer = exec_result.output
                        # 截取汇总的前300个字符用于显示
                        display_summary = summary_answer[:300] + "..." if len(summary_answer) > 300 else summary_answer
                        print(f"   {display_summary}")
                else:
                    print(f"  ❌ {name}: {exec_result.error}")
                    
            # 显示工作流输出信息
            if 'output' in qa_result:
                print(f"\n📤 工作流输出:")
                for key, value in qa_result['output'].items():
                    print(f"   {key}: {value[:100]}..." if len(str(value)) > 100 else f"   {key}: {value}")
            
            print(f"\n📊 执行统计: {len(model_answers)} 个模型成功回答，gemma3:12b完成汇总")
            
        else:
            print(f"❌ 多模型问答失败: {qa_result['error']}")
            
    except FileNotFoundError:
        print("❌ 未找到DSL文件: demo_qa.yaml")
    except Exception as e:
        print(f"❌ DSL执行出错: {str(e)}")
    
    print("\n🎉 演示完成！")
    print("核心特性展示:")
    print("✅ 自定义模型配置管理")
    print("✅ 本地DSL文件读取执行")
    print("✅ 多模型并行/串行执行")
    print("✅ 复杂依赖关系处理")
    print("✅ 模拟LLM调用和结果汇总")

if __name__ == '__main__':
    asyncio.run(demo_basic_usage())
