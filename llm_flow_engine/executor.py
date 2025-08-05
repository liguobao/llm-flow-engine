import asyncio
import time
from typing import Any, Callable, Optional
from loguru import logger
from .executor_result import ExecutorResult
from .utils import resolve_placeholders

class Executor:
    def __init__(self, name: str, exec_type: str, func: Callable, *,
                 timeout: int = 60, retry: int = 0, retry_interval: int = 1,
                 context: dict = None, model=None, kb=None, ext_dep=None,
                 custom_vars: dict = None, intermediate: dict = None, context_params: dict = None):
        self.name = name
        self.exec_type = exec_type
        self.func = func
        self.timeout = timeout
        self.retry = retry
        self.retry_interval = retry_interval
        self.context = context or {}
        self.model = model
        self.kb = kb
        self.ext_dep = ext_dep
        self.custom_vars = custom_vars or {}
        self.intermediate = intermediate or {}
        self.context_params = context_params or {}

    async def run(self, *args, **kwargs) -> ExecutorResult:
        start = time.time()
        last_err = None
        
        logger.debug(f"执行器 {self.name} 的 custom_vars: {self.custom_vars}")
        
        # 获取全局执行上下文（包含其他步骤的输出）
        global_context = kwargs.get('_global_context', {})
        # 合并当前输入和全局上下文
        execution_context = {**kwargs, **global_context}
        logger.debug(f"执行器 {self.name} 的全局上下文: {list(global_context.keys())}")
        
        # 如果有位置参数传入（来自上游依赖），优先使用它们，否则使用custom_vars
        # 处理参数，确保不会有重复的参数传递
        final_kwargs = {k: v for k, v in self.custom_vars.items()}
        final_kwargs.update(kwargs)

        # 如果 func 是 llm_simple_call，处理特殊情况
        if self.func.__name__ == 'llm_simple_call':
            # 移除 custom_vars 中可能存在的 user_input，因为它会作为位置参数传递
            final_kwargs.pop('user_input', None)
            # 移除不需要的参数，避免传递给llm_simple_call
            final_kwargs.pop('workflow_input', None)
            final_kwargs.pop('_global_context', None)
            final_kwargs.pop('prompt', None)  # llm_simple_call 不支持 prompt 参数
            
            # 确保上游参数作为 user_input
            if args:
                args = (args[0],)  # 只取第一个参数作为 user_input
                logger.debug(f"执行器 {self.name} 开始运行，user_input: {args[0]}, 额外参数: {final_kwargs}")
            else:
                # 没有上游参数时，使用 custom_vars 中的 user_input
                user_input_value = self.custom_vars.get('user_input')
                args = (user_input_value,)
                logger.debug(f"执行器 {self.name} 开始运行，参数: {args}, {final_kwargs}")
        elif self.func.__name__ == 'text_process':
            # text_process 函数需要保留 workflow_input 参数
            final_kwargs.pop('_global_context', None)
            if args:
                logger.debug(f"执行器 {self.name} 开始运行，上游参数: {args}, 额外参数: {final_kwargs}")
            else:
                logger.debug(f"执行器 {self.name} 开始运行，参数: {args}, {final_kwargs}")
        else:
            # 其他函数保持原有逻辑，但也移除不需要的参数
            final_kwargs.pop('workflow_input', None)
            final_kwargs.pop('_global_context', None)
            if args:
                logger.debug(f"执行器 {self.name} 开始运行，上游参数: {args}, 额外参数: {final_kwargs}")
            else:
                logger.debug(f"执行器 {self.name} 开始运行，参数: {args}, {final_kwargs}")

        logger.debug(f"执行器 {self.name} 调用函数 {self.func.__name__} 的最终参数: args={args}, kwargs={final_kwargs}")
        logger.debug(f"执行器 {self.name} 的最终参数检查: final_kwargs={final_kwargs}")
        
        # 在执行阶段解析占位符，使用包含全局上下文的execution_context
        logger.debug(f"解析占位符前的参数: {final_kwargs}")
        final_kwargs = {key: resolve_placeholders(val, execution_context) for key, val in final_kwargs.items()}
        logger.debug(f"解析占位符后的参数: {final_kwargs}")
        logger.debug(f"解析占位符后的参数检查: {final_kwargs}")
        
        # 在运行时重新解析 custom_vars
        self.custom_vars = {key: resolve_placeholders(val, execution_context) for key, val in self.custom_vars.items()}
        logger.debug(f"运行时重新解析后的 custom_vars: {self.custom_vars}")
        
        for attempt in range(self.retry + 1):
            try:
                result = await asyncio.wait_for(self.func(*args, **final_kwargs), timeout=self.timeout)
                logger.debug(f"执行器 {self.name} 的函数返回值: {result}")
                logger.success(f"执行器 {self.name} 运行成功，用时: {time.time() - start:.3f}s")
                return ExecutorResult(self.exec_type, start, time.time(), 'success', None, self.custom_vars, self.intermediate, self.context_params, result)
            except Exception as e:
                last_err = str(e)
                logger.warning(f"执行器 {self.name} 第{attempt+1}次尝试失败: {last_err}")
                if attempt < self.retry:
                    logger.info(f"等待 {self.retry_interval}s 后重试...")
                    await asyncio.sleep(self.retry_interval)
                    
        logger.error(f"执行器 {self.name} 所有重试均失败，最终错误: {last_err}")
        return ExecutorResult(self.exec_type, start, time.time(), 'failed', last_err, self.custom_vars, self.intermediate, self.context_params, None)
