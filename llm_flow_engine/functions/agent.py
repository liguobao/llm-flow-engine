"""
智能Agent模块 - 组合RAG、工具、知识库的智能处理
"""
from typing import List, Dict
from loguru import logger


async def agent_process(user_input: str, kb_name: str = None, model: str = "gemma3:4b", 
                       enable_tools: bool = True, enable_rag: bool = True, **kwargs) -> str:
    """智能Agent处理 - 组合使用RAG检索、工具执行、知识库查询"""
    from .knowledge_base import knowledge_base_search
    from .rag import vector_search
    from .tools import list_available_tools
    from .llm_api import llm_api_call
    
    try:
        logger.info(f"Agent开始处理用户请求: {user_input}")
        
        # 1. 首先尝试知识库查询（如果指定了知识库）
        kb_context = ""
        if enable_rag and kb_name:
            kb_results = await knowledge_base_search(kb_name, user_input, 3)
            if kb_results:
                kb_context = f"\n\n知识库相关信息:\n"
                for i, result in enumerate(kb_results, 1):
                    kb_context += f"{i}. {result['text']}\n"
        
        # 2. 然后尝试通用RAG检索
        rag_context = ""
        if enable_rag:
            rag_results = await vector_search(user_input, 3)
            if rag_results:
                rag_context = f"\n\n检索到的相关文档:\n"
                for i, result in enumerate(rag_results, 1):
                    rag_context += f"{i}. {result['text']}\n"
        
        # 3. 检查是否需要使用工具
        tool_context = ""
        if enable_tools:
            available_tools = await list_available_tools()
            if available_tools:
                tools_desc = "\n".join([
                    f"- {tool['name']}: {tool['description']}"
                    for tool in available_tools
                ])
                tool_context = f"\n\n可用工具:\n{tools_desc}"
        
        # 4. 构建综合提示词
        prompt = f"""你是一个智能AI助手，具有以下能力：
- 基于知识库和文档检索回答问题
- 使用工具执行特定任务
- 进行推理和分析

用户请求: {user_input}

{kb_context}{rag_context}{tool_context}

请基于以上信息回答用户问题。如果需要使用工具，请说明需要使用哪个工具以及原因。
如果可以直接基于已有信息回答，请直接给出答案。"""

        # 5. 生成初始响应
        response = await llm_api_call(prompt=prompt, model=model, max_tokens=800)
        
        logger.success(f"Agent处理完成")
        return response
        
    except Exception as e:
        logger.error(f"Agent处理失败: {e}")
        return f"处理失败: {str(e)}"
