"""
RAG检索模块 - 向量存储、检索和问答
"""
import time
import math
import hashlib
from typing import Dict, List
from loguru import logger


# 向量存储和检索
_vector_store = {}  # 简单的内存向量存储


async def embedding_text(text: str, model: str = "text-embedding-ada-002") -> List[float]:
    """文本向量化 - 简化版本，实际应用中可以接入真实的embedding服务"""
    # 这里使用简单的哈希函数模拟向量，实际应用中应该调用真实的embedding API
    hash_obj = hashlib.md5(text.encode())
    hash_hex = hash_obj.hexdigest()
    
    # 将哈希值转换为模拟的向量（实际应该调用embedding服务）
    vector = []
    for i in range(0, len(hash_hex), 2):
        vector.append(int(hash_hex[i:i+2], 16) / 255.0)
    
    # 补齐到512维
    while len(vector) < 512:
        vector.append(0.0)
    
    logger.debug(f"文本向量化完成，维度: {len(vector)}")
    return vector[:512]


async def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """计算余弦相似度"""
    # 计算点积
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    
    # 计算向量的模
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(a * a for a in vec2))
    
    # 避免除零
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    return dot_product / (magnitude1 * magnitude2)


async def vector_store_add(doc_id: str, text: str, metadata: Dict = None) -> str:
    """向向量存储添加文档"""
    try:
        vector = await embedding_text(text)
        _vector_store[doc_id] = {
            "text": text,
            "vector": vector,
            "metadata": metadata or {},
            "timestamp": time.time()
        }
        logger.info(f"文档 {doc_id} 已添加到向量存储")
        return f"文档已添加: {doc_id}"
    except Exception as e:
        logger.error(f"添加文档到向量存储失败: {e}")
        raise


async def vector_search(query: str, top_k: int = 5, threshold: float = 0.7) -> List[Dict]:
    """向量检索"""
    try:
        query_vector = await embedding_text(query)
        results = []
        
        for doc_id, doc_data in _vector_store.items():
            similarity = await cosine_similarity(query_vector, doc_data["vector"])
            if similarity >= threshold:
                results.append({
                    "doc_id": doc_id,
                    "text": doc_data["text"],
                    "metadata": doc_data["metadata"],
                    "similarity": similarity
                })
        
        # 按相似度排序
        results.sort(key=lambda x: x["similarity"], reverse=True)
        
        logger.info(f"向量检索完成，找到 {len(results)} 个相关文档")
        return results[:top_k]
    except Exception as e:
        logger.error(f"向量检索失败: {e}")
        raise


async def rag_retrieve(query: str, top_k: int = 3, include_metadata: bool = True) -> str:
    """RAG检索 - 返回格式化的检索结果"""
    try:
        search_results = await vector_search(query, top_k)
        
        if not search_results:
            return "未找到相关文档"
        
        formatted_results = []
        for i, result in enumerate(search_results, 1):
            text = f"文档{i}:\n{result['text']}"
            if include_metadata and result['metadata']:
                text += f"\n元数据: {result['metadata']}"
            text += f"\n相似度: {result['similarity']:.3f}"
            formatted_results.append(text)
        
        return "\n\n".join(formatted_results)
    except Exception as e:
        logger.error(f"RAG检索失败: {e}")
        return f"检索失败: {str(e)}"


async def rag_qa(question: str, model: str = "gemma3:4b", top_k: int = 3) -> str:
    """RAG问答 - 基于检索结果回答问题"""
    from .llm_api import llm_api_call
    
    try:
        # 1. 检索相关文档
        context = await rag_retrieve(question, top_k)
        
        # 2. 构建提示词
        prompt = f"""基于以下检索到的相关文档回答问题。如果文档中没有相关信息，请说明无法从提供的文档中找到答案。

相关文档:
{context}

问题: {question}

请基于以上文档内容回答:"""
        
        # 3. 调用LLM生成答案
        answer = await llm_api_call(prompt=prompt, model=model, max_tokens=500)
        
        logger.info(f"RAG问答完成，问题: {question}")
        return answer
    except Exception as e:
        logger.error(f"RAG问答失败: {e}")
        return f"问答失败: {str(e)}"
