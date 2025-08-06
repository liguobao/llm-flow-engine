#!/usr/bin/env python3
"""
智能客服Agent示例 - 使用LLM Flow Engine的DSL工作流
演示如何使用工作流引擎构建智能客服系统
"""
import asyncio
import sys
import os
import yaml

# 添加项目根目录到path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm_flow_engine.flow_engine import FlowEngine
from llm_flow_engine.functions.knowledge_base import knowledge_base_create, knowledge_base_add_document
from llm_flow_engine.functions.tools import register_tool

class CustomerServiceAgent:
    """智能客服Agent - 使用LLM Flow Engine工作流"""
    
    def __init__(self):
        self.kb_name = "customer_service_kb"
        self.model = "gemma3:4b"
        self.engine = FlowEngine()
        self.initialized = False
    
    async def initialize(self):
        """初始化客服知识库和工具"""
        if self.initialized:
            return
            
        print("🤖 初始化智能客服Agent（DSL工作流模式）...")
        
        # 1. 创建客服知识库
        await knowledge_base_create(self.kb_name, "客服知识库 - 包含常见问题和解决方案")
        
        # 2. 添加常见问题到知识库
        faq_data = [
            {
                "id": "login_issue",
                "content": "登录问题：如果无法登录，请检查用户名密码是否正确，确认账号未被锁定，清除浏览器缓存后重试。",
                "metadata": {"category": "login", "priority": "high"}
            },
            {
                "id": "password_reset",
                "content": "密码重置：点击登录页面的'忘记密码'链接，输入注册邮箱，查收重置邮件并按提示操作。",
                "metadata": {"category": "password", "priority": "high"}
            },
            {
                "id": "payment_issue",
                "content": "支付问题：支持支付宝、微信支付、银行卡。如支付失败，请检查余额、网络连接或联系银行。",
                "metadata": {"category": "payment", "priority": "medium"}
            },
            {
                "id": "refund_policy",
                "content": "退款政策：购买后7天内可申请退款，数字商品除外。退款将在5-7个工作日内到账。",
                "metadata": {"category": "refund", "priority": "medium"}
            },
            {
                "id": "technical_support",
                "content": "技术支持：遇到技术问题请提供错误截图、操作系统版本、浏览器信息，我们会尽快处理。",
                "metadata": {"category": "technical", "priority": "low"}
            }
        ]
        
        for faq in faq_data:
            await knowledge_base_add_document(
                self.kb_name, 
                faq["id"], 
                faq["content"], 
                faq["metadata"]
            )
        
        # 3. 注册客服专用工具到引擎
        self.engine.register_function("check_order_status", self._check_order_status)
        self.engine.register_function("create_support_ticket", self._create_support_ticket)
        self.engine.register_function("transfer_to_human", self._transfer_to_human)
        
        self.initialized = True
        print("✅ 智能客服Agent（DSL工作流模式）初始化完成")
    
    async def _check_order_status(self, order_id: str) -> str:
        """模拟查询订单状态"""
        order_statuses = {
            "ORD001": "已发货，预计明天到达",
            "ORD002": "正在处理中，预计今天发货", 
            "ORD003": "已完成，感谢您的购买",
            "ORD004": "已取消，退款将在3-5个工作日到账"
        }
        
        status = order_statuses.get(order_id, "未找到该订单，请检查订单号是否正确")
        return f"订单 {order_id} 状态：{status}"
    
    async def _create_support_ticket(self, issue_type: str, description: str, priority: str = "medium") -> str:
        """创建客服工单"""
        import uuid
        ticket_id = str(uuid.uuid4())[:8].upper()
        return f"已为您创建工单 #{ticket_id}，问题类型：{issue_type}，优先级：{priority}。我们会在24小时内回复您。"
    
    async def _transfer_to_human(self, reason: str) -> str:
        """转接人工客服"""
        return f"正在为您转接人工客服（原因：{reason}），请稍候。当前排队人数：3人，预计等待时间：5分钟。"
    
    async def handle_customer_query(self, query: str) -> str:
        """处理客户咨询 - 使用DSL工作流"""
        await self.initialize()
        
        print(f"\n👤 客户咨询: {query}")
        print("🤖 正在通过工作流分析并查找相关信息...")
        
        # 定义客服处理工作流DSL
        customer_service_dsl = f"""
metadata:
  version: "1.0"
  description: "智能客服查询处理工作流"

input:
  type: "start"
  name: "customer_query"
  data:
    query: "{query}"

executors:
  # 步骤1: 知识库查询
  - name: kb_search
    type: "task"
    func: knowledge_base_search
    custom_vars:
      kb_name: "{self.kb_name}"
      query: "${{customer_query.query}}"
      top_k: 3

  # 步骤2: 分析查询意图
  - name: intent_analysis
    type: "task"
    func: llm_simple_call
    custom_vars:
      user_input: "分析以下客户查询的意图类型（登录问题/订单查询/支付问题/退款申请/技术支持）：${{customer_query.query}}"
      model: "{self.model}"
    depends_on: ["kb_search"]

  # 步骤3: 生成智能回复
  - name: generate_response
    type: "task"
    func: llm_simple_call
    custom_vars:
      user_input: |
        作为专业客服，基于以下信息回复客户：
        
        客户问题：${{customer_query.query}}
        查询意图：${{intent_analysis.output}}
        相关知识：${{kb_search.output}}
        
        要求：
        1. 回复专业、友好、有帮助
        2. 如果知识库有相关信息，直接提供解决方案
        3. 如果需要查询订单等，说明需要的信息
        4. 复杂问题建议转接人工客服
      model: "{self.model}"
    depends_on: ["intent_analysis"]

output:
  name: "final_response"
  value: "${{generate_response.output}}"
"""
        
        # 执行DSL工作流
        result = await self.engine.execute_dsl(customer_service_dsl, {"query": query})
        
        if result['success']:
            return result['results'].get('final_response', '抱歉，处理您的请求时出现问题')
        else:
            return f"系统错误：{result['error']}"
    
    async def handle_order_query(self, query: str, order_id: str = None) -> str:
        """专门处理订单查询的工作流"""
        await self.initialize()
        
        print(f"\n📦 订单查询: {query} (订单号: {order_id or '待提取'})")
        print("🤖 正在通过订单查询工作流处理...")
        
        order_query_dsl = f"""
metadata:
  version: "1.0"
  description: "订单查询处理工作流"

input:
  type: "start"
  name: "order_request"
  data:
    query: "{query}"
    order_id: "{order_id or ''}"

executors:
  # 步骤1: 查询订单状态（直接使用提供的order_id）
  - name: check_order
    type: "task"
    func: check_order_status
    custom_vars:
      order_id: "{order_id or 'ORD001'}"

  # 步骤2: 格式化回复
  - name: format_response
    type: "task"
    func: llm_simple_call
    custom_vars:
      user_input: |
        将以下订单查询结果转换为友好的客服回复：
        查询结果：${{check_order.output}}
        
        要求：语言亲切，信息准确，如有物流信息要详细说明
      model: "{self.model}"
    depends_on: ["check_order"]

output:
  name: "order_response"
  value: "${{format_response.output}}"
"""
        
        result = await self.engine.execute_dsl(order_query_dsl, {"query": query, "order_id": order_id})
        
        if result['success']:
            return result['results'].get('order_response', '订单查询失败')
        else:
            return f"订单查询错误：{result['error']}"
    
    async def handle_complex_issue(self, query: str) -> str:
        """处理复杂问题的多步骤工作流"""
        await self.initialize()
        
        print(f"\n🔧 复杂问题处理: {query}")
        print("🤖 正在通过多步骤工作流处理复杂问题...")
        
        complex_issue_dsl = f"""
metadata:
  version: "1.0"
  description: "复杂问题处理工作流"

input:
  type: "start"
  name: "complex_query"
  data:
    query: "{query}"

executors:
  # 步骤1: 问题分类
  - name: classify_issue
    type: "task"
    func: llm_simple_call
    custom_vars:
      user_input: |
        对以下客户问题进行分类，判断严重程度和处理优先级：
        问题：${{complex_query.query}}
        
        请从以下方面分析：
        1. 问题类型（技术/账户/订单/支付等）
        2. 严重程度（高/中/低）
        3. 是否需要人工介入
        4. 预估解决时间
        
        输出JSON格式结果
      model: "{self.model}"

  # 步骤2: 知识库深度搜索
  - name: deep_kb_search
    type: "task"
    func: knowledge_base_search
    custom_vars:
      kb_name: "{self.kb_name}"
      query: "${{complex_query.query}}"
      top_k: 5
    depends_on: ["classify_issue"]

  # 步骤3: 生成详细解决方案
  - name: generate_solution
    type: "task"
    func: llm_simple_call
    custom_vars:
      user_input: |
        基于问题分类和知识库信息，为客户提供详细解决方案：
        
        客户问题：${{complex_query.query}}
        问题分类：${{classify_issue.output}}
        相关知识：${{deep_kb_search.output}}
        
        要求：
        1. 提供详细的步骤化解决方案
        2. 如果涉及技术问题，提供具体操作步骤
        3. 给出预计解决时间
        4. 提供后续联系方式
        5. 必要时建议创建工单或转人工
      model: "{self.model}"
    depends_on: ["deep_kb_search"]

output:
  name: "complex_response"
  value: "${{generate_solution.output}}"
"""
        
        result = await self.engine.execute_dsl(complex_issue_dsl, {"query": query})
        
        if result['success']:
            return result['results'].get('complex_response', '复杂问题处理失败')
        else:
            return f"复杂问题处理错误：{result['error']}"

async def demo_customer_service_flow():
    """客服Agent工作流演示"""
    print("🎯 智能客服Agent演示 (LLM Flow Engine工作流模式)")
    print("=" * 60)
    
    agent = CustomerServiceAgent()
    
    # 测试不同类型的客户咨询
    test_scenarios = [
        {
            "type": "基础查询",
            "query": "我忘记密码了，怎么办？",
            "method": "handle_customer_query"
        },
        {
            "type": "订单查询",
            "query": "查询订单ORD001的状态",
            "method": "handle_order_query",
            "order_id": "ORD001"
        },
        {
            "type": "复杂问题",
            "query": "我的支付失败了，显示错误代码500，而且账户余额也被扣了，这是什么原因？需要多久能解决？",
            "method": "handle_complex_issue"
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n🔍 测试场景 {i}: {scenario['type']}")
        print(f"📝 查询内容: {scenario['query']}")
        print("-" * 50)
        
        method = getattr(agent, scenario['method'])
        if scenario.get('order_id'):
            response = await method(scenario['query'], scenario['order_id'])
        else:
            response = await method(scenario['query'])
            
        print(f"🤖 客服回复: {response}")
        print("=" * 60)
        
        # 添加延迟，模拟真实对话
        await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(demo_customer_service_flow())
