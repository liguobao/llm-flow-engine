"""
知识库模块 - 知识库创建、管理和查询
"""
import time
from typing import Dict, List
from loguru import logger


_knowledge_base = {}  # 知识库存储


async def knowledge_base_create(kb_name: str, description: str = "") -> str:
    """创建知识库"""
    try:
        if kb_name not in _knowledge_base:
            _knowledge_base[kb_name] = {
                "description": description,
                "documents": {},
                "created_at": time.time(),
                "updated_at": time.time()
            }
            logger.info(f"知识库已创建: {kb_name}")
            return f"知识库已创建: {kb_name}"
        else:
            return f"知识库已存在: {kb_name}"
    except Exception as e:
        logger.error(f"创建知识库失败: {e}")
        raise


async def knowledge_base_add_document(kb_name: str, doc_id: str, content: str, metadata: Dict = None) -> str:
    """向知识库添加文档"""
    from .rag import vector_store_add
    
    try:
        if kb_name not in _knowledge_base:
            await knowledge_base_create(kb_name)
        
        # 添加文档到知识库
        _knowledge_base[kb_name]["documents"][doc_id] = {
            "content": content,
            "metadata": metadata or {},
            "added_at": time.time()
        }
        
        # 同时添加到向量存储用于检索
        vector_doc_id = f"{kb_name}:{doc_id}"
        await vector_store_add(vector_doc_id, content, {
            "kb_name": kb_name,
            "doc_id": doc_id,
            **(metadata or {})
        })
        
        _knowledge_base[kb_name]["updated_at"] = time.time()
        
        logger.info(f"文档已添加到知识库 {kb_name}: {doc_id}")
        return f"文档已添加: {doc_id}"
    except Exception as e:
        logger.error(f"添加文档到知识库失败: {e}")
        raise


async def knowledge_base_search(kb_name: str, query: str, top_k: int = 5) -> List[Dict]:
    """在指定知识库中搜索"""
    from .rag import vector_search
    
    try:
        if kb_name not in _knowledge_base:
            return []
        
        # 在向量存储中搜索该知识库的文档
        all_results = await vector_search(query, top_k * 2)  # 搜索更多然后过滤
        
        # 过滤出属于指定知识库的结果
        kb_results = [
            result for result in all_results
            if result["metadata"].get("kb_name") == kb_name
        ]
        
        return kb_results[:top_k]
    except Exception as e:
        logger.error(f"知识库搜索失败: {e}")
        return []


async def knowledge_base_qa(kb_name: str, question: str, model: str = "gemma3:4b", top_k: int = 3) -> str:
    """基于指定知识库回答问题"""
    from .llm_api import llm_api_call
    
    try:
        # 1. 在知识库中搜索相关文档
        search_results = await knowledge_base_search(kb_name, question, top_k)
        
        if not search_results:
            return f"在知识库 {kb_name} 中未找到相关信息"
        
        # 2. 构建上下文
        context_parts = []
        for i, result in enumerate(search_results, 1):
            context_parts.append(f"文档{i}: {result['text']}")
        
        context = "\n\n".join(context_parts)
        
        # 3. 构建提示词
        prompt = f"""你是一个基于知识库的问答助手。请基于以下知识库内容回答用户问题。

知识库名称: {kb_name}

相关文档内容:
{context}

用户问题: {question}

请基于以上知识库内容进行回答。如果知识库中没有相关信息，请明确说明。"""

        # 4. 生成答案
        answer = await llm_api_call(prompt=prompt, model=model, max_tokens=500)
        
        logger.info(f"知识库问答完成: {kb_name} - {question}")
        return answer
    except Exception as e:
        logger.error(f"知识库问答失败: {e}")
        return f"问答失败: {str(e)}"


async def knowledge_base_list() -> Dict:
    """列出所有知识库"""
    kb_list = {}
    for kb_name, kb_info in _knowledge_base.items():
        kb_list[kb_name] = {
            "description": kb_info["description"],
            "document_count": len(kb_info["documents"]),
            "created_at": kb_info["created_at"],
            "updated_at": kb_info["updated_at"]
        }
    return kb_list


async def knowledge_base_get_info(kb_name: str) -> Dict:
    """获取知识库信息"""
    if kb_name not in _knowledge_base:
        return {"error": f"知识库不存在: {kb_name}"}
    
    kb_info = _knowledge_base[kb_name]
    return {
        "name": kb_name,
        "description": kb_info["description"],
        "document_count": len(kb_info["documents"]),
        "created_at": kb_info["created_at"],
        "updated_at": kb_info["updated_at"],
        "documents": list(kb_info["documents"].keys())
    }
