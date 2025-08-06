#!/usr/bin/env python3
"""
简化版智能客服Agent - 展示正确的DSL工作流使用方法
"""
import asyncio
import sys
import os

# 添加项目根目录到path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm_flow_engine.flow_engine import FlowEngine
from llm_flow_engine.functions.knowledge_base import knowledge_base_create, knowledge_base_add_document

class SimpleCustomerServiceAgent:
    """简化版智能客服Agent - 演示正确的DSL工作流用法"""
    
    def __init__(self):
        self.kb_name = "simple_customer_kb"
        self.model = "gemma3:4b"
        self.engine = FlowEngine()
        self.initialized = False
    
    async def initialize(self):
        """初始化客服知识库"""
        if self.initialized:
            return
            
        print("🤖 初始化简化版客服Agent...")
        
        # 创建客服知识库
        await knowledge_base_create(self.kb_name, "简化版客服知识库")
        
        # 添加常见问题到知识库
        faq_data = [
            {
                "id": "password_reset",
                "content": "密码重置：点击登录页面的'忘记密码'链接，输入注册邮箱，查收重置邮件并按提示操作。",
                "metadata": {"category": "password", "priority": "high"}
            },
            {
                "id": "payment_issue", 
                "content": "支付问题：支持支付宝、微信支付、银行卡。如支付失败，请检查余额、网络连接或联系银行。",
                "metadata": {"category": "payment", "priority": "medium"}
            }
        ]
        
        for faq in faq_data:
            await knowledge_base_add_document(
                self.kb_name,
                faq["id"],
                faq["content"],
                faq["metadata"]
            )
        
        self.initialized = True
        print("✅ 简化版客服Agent初始化完成")
    
    async def handle_simple_query(self, user_query: str) -> str:
        """处理简单客户查询 - 使用正确的DSL工作流"""
        await self.initialize()
        
        print(f"\n👤 客户咨询: {user_query}")
        print("🤖 正在通过简化工作流处理...")
        
        # 简化的客服处理工作流DSL
        simple_customer_dsl = f"""
metadata:
  version: "1.0"
  description: "简化客服查询处理工作流"

input:
  type: "start"
  name: "workflow_input"
  data:
    user_query: "{user_query}"

executors:
  # 步骤1: 知识库查询
  - name: search_kb
    type: "task"
    func: knowledge_base_search
    custom_vars:
      kb_name: "{self.kb_name}"
      query: "${{workflow_input.user_query}}"
      top_k: 2

  # 步骤2: 生成回复
  - name: generate_reply
    type: "task"
    func: llm_simple_call
    custom_vars:
      user_input: |
        作为专业客服，基于以下信息回复客户：
        
        客户问题：${{workflow_input.user_query}}
        知识库查询结果：${{search_kb.output}}
        
        要求：
        1. 回复专业、友好、有帮助
        2. 如果知识库有相关信息，直接提供解决方案
        3. 如果没有相关信息，礼貌地说明并建议联系人工客服
      model: "{self.model}"
    depends_on: ["search_kb"]

output:
  name: "customer_reply"
  value: "${{generate_reply.output}}"
"""
        
        # 执行DSL工作流
        result = await self.engine.execute_dsl(simple_customer_dsl, {"user_query": user_query})
        
        if result['success']:
            # 获取执行结果，如果是ExecutorResult对象则获取其output属性
            customer_reply = result['results'].get('customer_reply')
            if hasattr(customer_reply, 'output'):
                return customer_reply.output if customer_reply.output is not None else '抱歉，处理您的请求时出现问题'
            return customer_reply if customer_reply is not None else '抱歉，处理您的请求时出现问题'
        else:
            return f"系统错误：{result['error']}"
    
    async def handle_order_status_query(self, order_id: str) -> str:
        """处理订单状态查询"""
        await self.initialize()
        
        print(f"\n📦 订单查询: {order_id}")
        print("🤖 正在查询订单状态...")
        
        # 注册订单查询工具到引擎（临时注册）
        async def check_order_status_simple(order_id: str) -> str:
            order_statuses = {
                "ORD001": "已发货，预计明天到达",
                "ORD002": "正在处理中，预计今天发货",
                "ORD003": "已完成，感谢您的购买"
            }
            return order_statuses.get(order_id, "未找到该订单，请检查订单号是否正确")
        
        self.engine.register_function("check_order_status_simple", check_order_status_simple)
        
        order_query_dsl = f"""
metadata:
  version: "1.0" 
  description: "订单状态查询工作流"

input:
  type: "start"
  name: "workflow_input"
  data:
    order_id: "{order_id}"

executors:
  # 步骤1: 查询订单状态
  - name: get_order_status
    type: "task"
    func: check_order_status_simple
    custom_vars:
      order_id: "${{workflow_input.order_id}}"

  # 步骤2: 格式化回复
  - name: format_order_reply
    type: "task"
    func: llm_simple_call
    custom_vars:
      user_input: |
        将订单查询结果转换为友好的客服回复：
        订单号：${{workflow_input.order_id}}
        查询结果：${{get_order_status.output}}
        
        要求：语言亲切，信息准确
      model: "{self.model}"
    depends_on: ["get_order_status"]

output:
  name: "order_status_reply"
  value: "${{format_order_reply.output}}"
"""
        
        result = await self.engine.execute_dsl(order_query_dsl, {"order_id": order_id})
        
        if result['success']:
            # 获取执行结果，如果是ExecutorResult对象则获取其output属性
            order_reply = result['results'].get('order_status_reply')
            if hasattr(order_reply, 'output'):
                return order_reply.output if order_reply.output is not None else '订单查询失败'
            return order_reply if order_reply is not None else '订单查询失败'
        else:
            return f"订单查询错误：{result['error']}"

async def demo_simple_customer_service():
    """简化版客服Agent演示"""
    print("🎯 简化版智能客服Agent演示")
    print("展示正确的DSL工作流使用方法")
    print("=" * 50)
    
    agent = SimpleCustomerServiceAgent()
    
    # 测试场景
    test_cases = [
        {
            "type": "密码问题",
            "method": "handle_simple_query",
            "input": "我忘记密码了，怎么办？"
        },
        {
            "type": "支付问题", 
            "method": "handle_simple_query",
            "input": "我的支付失败了，是什么原因？"
        },
        {
            "type": "订单查询",
            "method": "handle_order_status_query",
            "input": "ORD001"
        },
        {
            "type": "未知问题",
            "method": "handle_simple_query", 
            "input": "你们的营业时间是什么时候？"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 测试场景 {i}: {test_case['type']}")
        print(f"📝 输入内容: {test_case['input']}")
        print("-" * 40)
        
        method = getattr(agent, test_case['method'])
        response = await method(test_case['input'])
        
        print(f"🤖 客服回复: {response}")
        print("=" * 50)
        
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(demo_simple_customer_service())
