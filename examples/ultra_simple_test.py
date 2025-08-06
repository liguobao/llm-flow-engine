#!/usr/bin/env python3
"""
超简化版客服Agent - 专注于DSL工作流正确性测试
只解决最核心的参数传递问题
"""
import asyncio
from llm_flow_engine import FlowEngine
from llm_flow_engine.functions.knowledge_base import knowledge_base_create, knowledge_base_add_document, knowledge_base_search
from llm_flow_engine.functions.llm_api import llm_simple_call

class UltraSimpleCustomerAgent:
    """超简化版客服Agent，专注于测试DSL工作流的正确性"""
    
    def __init__(self):
        self.engine = FlowEngine()
        
    async def test_knowledge_base_search(self, query: str):
        """测试知识库搜索功能"""
        print(f"🔍 测试知识库搜索: {query}")
        
        # 先初始化知识库
        await knowledge_base_create("test_kb", "测试知识库")
        await knowledge_base_add_document(
            "test_kb",
            "password_help",
            "如果忘记密码，请点击登录页面的'忘记密码'链接",
            {"type": "help"}
        )
        
        # 最简单的DSL工作流 - 只测试知识库搜索
        simple_search_dsl = """
metadata:
  version: "1.0"
  description: "简单知识库搜索测试"

input:
  type: "start"
  name: "workflow_input"
  data:
    search_query: "{query}"

executors:
  - name: search_result
    type: "task"
    func: knowledge_base_search
    custom_vars:
      kb_name: "test_kb"
      query: "${workflow_input.search_query}"
      top_k: 1

output:
  name: "search_output"
  value: "${search_result.output}"
""".replace("{query}", query)
        
        try:
            result = await self.engine.execute_dsl(simple_search_dsl, {"search_query": query})
            print(f"✅ 搜索结果: {result}")
            return result
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
            return None
    
    async def test_llm_simple_call(self, message: str):
        """测试LLM简单调用功能"""
        print(f"🤖 测试LLM调用: {message}")
        
        # 最简单的DSL工作流 - 只测试LLM调用
        simple_llm_dsl = """
metadata:
  version: "1.0"
  description: "简单LLM调用测试"

input:
  type: "start"
  name: "workflow_input"
  data:
    user_message: "{message}"

executors:
  - name: llm_response
    type: "task"
    func: llm_simple_call
    custom_vars:
      user_input: "${workflow_input.user_message}"
      model: "gemma3:4b"

output:
  name: "llm_output"
  value: "${llm_response.output}"
""".replace("{message}", message)
        
        try:
            result = await self.engine.execute_dsl(simple_llm_dsl, {"user_message": message})
            print(f"✅ LLM回复: {result}")
            return result
        except Exception as e:
            print(f"❌ LLM调用失败: {e}")
            return None

async def main():
    """测试主函数"""
    print("🧪 开始超简化DSL工作流测试")
    print("=" * 50)
    
    agent = UltraSimpleCustomerAgent()
    
    # 测试1: 知识库搜索
    print("\n📋 测试1: 知识库搜索功能")
    await agent.test_knowledge_base_search("忘记密码")
    
    # 测试2: LLM调用
    print("\n📋 测试2: LLM简单调用功能")
    await agent.test_llm_simple_call("你好，请介绍一下自己")
    
    print("\n🏁 测试完成")

if __name__ == "__main__":
    asyncio.run(main())
