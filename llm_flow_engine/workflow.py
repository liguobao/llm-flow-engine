from typing import Any, Callable, Dict, List
from loguru import logger
from .executor import Executor
from .executor_result import ExecutorResult

class WorkFlow:
    def __init__(self, executors: List[Executor], force_sequential: bool = True):
        self.executors = executors
        self.force_sequential = force_sequential
        self.context = {}  # 添加 context 属性

    def _validate(self):
        # 简单参数合法性校验
        logger.debug("开始验证工作流配置...")
        for exe in self.executors:
            assert exe.name, 'Executor name required'
            assert exe.exec_type, 'Executor type required'
            assert callable(exe.func), 'Executor func must be callable'
        logger.debug("工作流配置验证通过")

    async def run(self, *args, **kwargs) -> Dict[str, 'ExecutorResult']:
        self._validate()
        results = {}
        
        if self.force_sequential:
            logger.info(f"开始顺序执行 {len(self.executors)} 个执行器")
            for exe in self.executors:
                res = await exe.run(*args, **kwargs)
                results[exe.name] = res
                # 更新全局 context
                if res.output is not None:
                    self.context[f"{exe.name}.output"] = res.output
        else:
            logger.info(f"开始并行执行 {len(self.executors)} 个执行器")
            import asyncio
            tasks = {exe.name: exe.run(*args, **kwargs) for exe in self.executors}
            done = await asyncio.gather(*tasks.values(), return_exceptions=True)
            for i, exe in enumerate(self.executors):
                results[exe.name] = done[i]
                # 更新全局 context
                if done[i].output is not None:
                    self.context[f"{exe.name}.output"] = done[i].output
                
        logger.success("工作流执行完成")
        return results
