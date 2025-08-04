from typing import Any, Callable, Dict, List, Optional, Set
from loguru import logger
from .executor import Executor

class DAGWorkFlow:
    def __init__(self, executors: List[Executor], dep_map: Dict[str, List[str]]):
        self.executors = {exe.name: exe for exe in executors}
        self.dep_map = dep_map  # 节点名 -> 依赖节点名列表
        self.reverse_dep = self._build_reverse_dep()

    def _build_reverse_dep(self):
        rev = {name: [] for name in self.executors}
        for node, deps in self.dep_map.items():
            for dep in deps:
                rev[dep].append(node)
        return rev

    async def run(self, *args, **kwargs) -> Dict[str, dict]:
        # 记录每个节点的输出
        results = {}
        # 记录已完成节点
        finished: Set[str] = set()
        # 记录正在运行的任务
        running = {}
        # 记录依赖计数
        dep_count = {name: len(deps) for name, deps in self.dep_map.items()}
        # 初始化可运行节点
        ready = [name for name, count in dep_count.items() if count == 0]

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
            dep_outputs = [results[dep] for dep in self.dep_map[name]]
            # 只传递上游output字段
            dep_outputs = [o.output if hasattr(o, 'output') else o.get('output') for o in dep_outputs]
            exe = self.executors[name]
            
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
            for nxt in self.reverse_dep[name]:
                dep_count[nxt] -= 1
                if dep_count[nxt] == 0:
                    new_ready.append(nxt)
            # 并行启动所有新准备好的节点
            for ready_node in new_ready:
                running[ready_node] = asyncio.create_task(run_node(ready_node))

        import asyncio
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
        return results
