from typing import Any, Callable, Dict, List, Optional
from loguru import logger
from .executor import Executor
from .executor_result import ExecutorResult

class WorkFlow:
    def __init__(self, executors: List[Executor], force_sequential: bool = True, 
                 dep_map: Optional[Dict[str, List[str]]] = None):
        self.executors = executors
        self.force_sequential = force_sequential
        self.context = {}  # 添加 context 属性
        self.dep_map = dep_map or {}  # 依赖映射，如果为空则表示无依赖
        
        # DSL 相关属性
        self.metadata: Dict = {}
        self.input: Dict = {}
        self.output: Dict = {}
        self.global_context: Dict = {}

    def _validate(self):
        # 简单参数合法性校验
        logger.debug("开始验证工作流配置...")
        for exe in self.executors:
            assert exe.name, 'Executor name required'
            assert exe.exec_type, 'Executor type required'
            assert callable(exe.func), 'Executor func must be callable'
        logger.debug("工作流配置验证通过")

    def _build_reverse_dep(self):
        """构建反向依赖映射"""
        executor_names = {exe.name for exe in self.executors}
        rev = {name: [] for name in executor_names}
        for node, deps in self.dep_map.items():
            for dep in deps:
                if dep in rev:
                    rev[dep].append(node)
        return rev

    def _has_dependencies(self):
        """检查是否有依赖关系"""
        return any(self.dep_map.get(exe.name, []) for exe in self.executors)

    async def run(self, *args, **kwargs) -> Dict[str, 'ExecutorResult']:
        self._validate()
        
        # 如果有依赖关系，使用DAG执行模式
        if self._has_dependencies():
            return await self._run_dag(*args, **kwargs)
        else:
            return await self._run_simple(*args, **kwargs)

    async def _run_simple(self, *args, **kwargs) -> Dict[str, 'ExecutorResult']:
        """简单执行模式（顺序或并行）"""
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

    async def _run_dag(self, *args, **kwargs) -> Dict[str, 'ExecutorResult']:
        """DAG执行模式（处理依赖关系）"""
        from typing import Set
        import asyncio
        
        # 将executors转换为字典形式便于查找
        executors_dict = {exe.name: exe for exe in self.executors}
        
        # 记录每个节点的输出
        results = {}
        # 记录已完成节点
        finished: Set[str] = set()
        # 记录正在运行的任务
        running = {}
        # 构建反向依赖
        reverse_dep = self._build_reverse_dep()
        # 记录依赖计数
        dep_count = {exe.name: len(self.dep_map.get(exe.name, [])) for exe in self.executors}
        # 初始化可运行节点
        ready = [exe.name for exe in self.executors if dep_count[exe.name] == 0]

        # 更新全局上下文 - 运行时输入覆盖 DSL 中的静态输入
        if hasattr(self, 'global_context'):
            # 合并运行时输入
            for key, value in kwargs.items():
                if key in self.global_context:
                    # 运行时输入覆盖 DSL 中的静态值
                    self.global_context[key] = value
                    logger.debug(f"运行时输入覆盖了 DSL 静态值: {key} = {value}")

        async def run_node(name):
            # 收集依赖节点输出
            deps = self.dep_map.get(name, [])
            dep_outputs = [results[dep] for dep in deps]
            # 只传递上游output字段
            dep_outputs = [o.output if hasattr(o, 'output') else o.get('output') for o in dep_outputs]
            exe = executors_dict[name]
            
            # 构建全局上下文，包含所有已完成节点的输出和运行时输入
            global_context = {}
            
            # 添加运行时输入
            for key, value in kwargs.items():
                global_context[key] = value
            
            # 添加已完成节点的输出
            for finished_name, finished_result in results.items():
                if hasattr(finished_result, 'output') and finished_result.output is not None:
                    global_context[f"{finished_name}.output"] = finished_result.output
                    global_context[finished_name] = finished_result  # 也保存完整的ExecutorResult
            
            # 将全局上下文添加到kwargs中
            node_kwargs = {**kwargs, '_global_context': global_context}
            
            # 合并参数：支持单输入或多输入
            if dep_outputs:
                res = await exe.run(*dep_outputs, **node_kwargs)
            else:
                res = await exe.run(*args, **node_kwargs)
            results[name] = res  # 直接存储ExecutorResult对象
            finished.add(name)
            # 检查下游节点，收集所有新准备好的节点
            new_ready = []
            for nxt in reverse_dep[name]:
                dep_count[nxt] -= 1
                if dep_count[nxt] == 0:
                    new_ready.append(nxt)
            # 并行启动所有新准备好的节点
            for ready_node in new_ready:
                running[ready_node] = asyncio.create_task(run_node(ready_node))

        # 并行启动所有初始ready节点
        for name in ready:
            running[name] = asyncio.create_task(run_node(name))
        
        # 动态等待任务完成，支持并行执行
        while running:
            done, pending = await asyncio.wait(running.values(), return_when=asyncio.FIRST_COMPLETED)
            # 移除已完成的任务
            completed_names = []
            for task in done:
                for name, t in running.items():
                    if t == task:
                        completed_names.append(name)
                        break
            for name in completed_names:
                del running[name]
        
        logger.success("DAG工作流执行完成")
        return results
