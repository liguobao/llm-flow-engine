"""
LLM Flow DSL 执行引擎完整演示
"""
import asyncio
from loguru import logger

# 使用包导入方式
from llm_flow_engine import flow_engine, BUILTIN_FUNCTIONS

# 复杂的DSL示例：用户输入 -> 文本处理 -> LLM处理 -> 结果合并
COMPLEX_DSL = """
executors:
  - name: input_process
    func: text_process
    custom_vars:
      operation: "upper"
  - name: llm_analyze
    func: llm_simple_call
    depends_on: [input_process]
  - name: backup_process
    func: text_process
    custom_vars:
      operation: "reverse"
  - name: final_merge
    func: data_merge
    depends_on: [llm_analyze, backup_process]
"""

# HTTP + LLM 混合处理DSL
HTTP_LLM_DSL = """
executors:
  - name: fetch_data
    func: http_request_get
    custom_vars:
      url: "https://api.github.com/users/octocat"
  - name: process_with_llm
    func: llm_simple_call
    depends_on: [fetch_data]
  - name: format_result
    func: json_to_string
    depends_on: [process_with_llm]
"""

# DAG分支合并DSL示例
DAG_DSL = """
executors:
  - name: start
    func: start_func
  - name: double
    func: double_func
    depends_on: [start]
  - name: triple
    func: triple_func
    depends_on: [start]
  - name: merge
    func: merge_func
    depends_on: [double, triple]
"""

# 自定义测试函数
async def start_func(x):
    await asyncio.sleep(0.2)
    return x

async def double_func(x):
    await asyncio.sleep(0.2)
    return x * 2

async def triple_func(x):
    await asyncio.sleep(0.2)
    return x * 3

async def merge_func(double_result, triple_result):
    # 合并两个分支的结果
    return {'sum': double_result + triple_result, 'double': double_result, 'triple': triple_result}

async def demo_simple_execution():
    """演示简单执行"""
    logger.info("=== 简单执行演示 ===")
    result = await flow_engine.execute_simple_flow("你好，请介绍一下Python编程")
    logger.info(f"结果: {result}")
    logger.info("")

async def demo_complex_dsl():
    """演示复杂DSL执行"""
    logger.info("=== 复杂DSL执行演示 ===")
    result = await flow_engine.execute_dsl(
        COMPLEX_DSL, 
        inputs={"input": "Hello World"},
        dsl_type='yaml'
    )
    logger.info(f"DSL: {result['dsl']}")
    logger.info(f"输入: {result['inputs']}")
    logger.info(f"结果: {result['results']}")
    logger.info(f"成功: {result['success']}")
    logger.info("")

async def demo_dag_workflow():
    """演示DAG分支合并工作流"""
    logger.info("=== DAG分支合并工作流演示 ===")
    # 注册自定义测试函数
    flow_engine.register_function('start_func', start_func)
    flow_engine.register_function('double_func', double_func)
    flow_engine.register_function('triple_func', triple_func)
    flow_engine.register_function('merge_func', merge_func)
    
    result = await flow_engine.execute_dsl(DAG_DSL, {'input': 3}, dsl_type='yaml')
    logger.info(f"执行结果: {result}")
    logger.info("")

async def demo_http_llm_flow():
    """演示HTTP+LLM混合流程"""
    logger.info("=== HTTP+LLM混合流程演示 ===")
    # 注意：这个示例需要网络连接
    try:
        result = await flow_engine.execute_dsl(HTTP_LLM_DSL, dsl_type='yaml')
        logger.info(f"执行结果: {result}")
    except Exception as e:
        logger.warning(f"执行出错 (可能是网络问题): {e}")
    logger.info("")

class FlowAPI:
    """提供RESTful API接口的类"""
    
    @staticmethod
    async def execute_flow(dsl: str, inputs: dict = None, dsl_type: str = 'yaml'):
        """执行流程API"""
        return await flow_engine.execute_dsl(dsl, inputs, dsl_type)
    
    @staticmethod
    async def quick_llm_call(user_input: str, api_key: str = None):
        """快速LLM调用API"""
        return await flow_engine.execute_simple_flow(user_input, api_key)
    
    @staticmethod
    def list_builtin_functions():
        """列出所有内置函数"""
        return list(BUILTIN_FUNCTIONS.keys())

async def main():
    """主演示函数"""
    logger.info("LLM Flow Engine 演示")
    logger.info("=" * 50)
    
    # 演示各种功能
    await demo_simple_execution()
    await demo_complex_dsl()
    await demo_dag_workflow()
    await demo_http_llm_flow()
    
    # 显示可用函数
    logger.info("=== 可用的内置函数 ===")
    functions = FlowAPI.list_builtin_functions()
    for func in functions:
        logger.info(f"- {func}")
    
    logger.success("\n系统已满足核心需求:")
    logger.success("✓ LLM Flow DSL 的定义 (YAML/JSON格式)")
    logger.success("✓ 基于 DSL 的最小化引擎执行")
    logger.success("✓ 支持引擎里面跑程序+大模型")
    logger.success("✓ 接收用户输入，跑出结果，输出 DSL 和结果")

if __name__ == '__main__':
    asyncio.run(main())
