"""
使用 llm-flow-engine 包的示例
"""
import asyncio
from loguru import logger

# 方式1：直接从包导入
from llm_flow_engine import execute_dsl, quick_llm_call, list_functions

# 方式2：导入引擎实例
from llm_flow_engine import flow_engine

# 方式3：导入具体组件
from llm_flow_engine import Executor, WorkFlow

async def package_usage_demo():
    """演示包的使用方式"""
    
    logger.info("=== 包使用演示 ===")
    
    # 使用便捷接口
    logger.info("1. 使用便捷接口")
    result = await quick_llm_call("测试输入")
    logger.info(f"快速LLM调用结果: {result['success']}")
    
    # 使用DSL执行
    logger.info("\n2. 使用DSL执行")
    simple_dsl = """
executors:
  - name: test
    func: text_process
    custom_vars:
      operation: "upper"
"""
    result = await execute_dsl(simple_dsl, {"input": "hello world"})
    logger.info(f"DSL执行结果: {result['success']}")
    
    # 列出可用函数
    logger.info("\n3. 可用函数列表")
    functions = list_functions()
    logger.info(f"共有 {len(functions)} 个内置函数")
    
    # 直接使用引擎
    logger.info("\n4. 直接使用引擎实例")
    flow_engine.register_function('custom_func', lambda x: x.upper())
    
    logger.success("\n包导入和使用成功！")

if __name__ == '__main__':
    asyncio.run(package_usage_demo())
