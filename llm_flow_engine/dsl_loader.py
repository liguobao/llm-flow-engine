import json
try:
    import yaml
except ImportError:
    yaml = None
from .executor import Executor
from .workflow import WorkFlow
from typing import Union, Callable, Dict
import re
from .utils import resolve_placeholders
from loguru import logger

def load_workflow_from_dsl(dsl: Union[str, dict], func_map: Dict[str, Callable], dsl_type: str = 'yaml'):
    """
    从DSL定义加载工作流
    
    Args:
        dsl: str或dict，定义工作流结构
        func_map: 执行器名称->函数 的映射
        dsl_type: 'yaml' 或 'json'

    DSL 格式:
        metadata:
            version: str   # DSL版本号
            description: str   # 工作流描述
        input:
            type: "start"  # 起始节点类型
            name: str      # 输入节点名称
            data: dict     # 输入数据
        executors: []      # 执行器列表，每个执行器包含:
            - name: str    # 执行器名称
              type: str    # 执行器类型
              func: str    # 函数名称
              depends_on: []  # 依赖的执行器列表
              custom_vars: {}  # 自定义变量
              # ... 其他配置
        output:
            type: "end"    # 终止节点类型
            name: str      # 输出节点名称
            data: dict     # 输出数据映射
    """
    if isinstance(dsl, str):
        if dsl_type == 'yaml':
            if not yaml:
                raise ImportError('请先安装pyyaml: pip install pyyaml')
            dsl_obj = yaml.safe_load(dsl)
        elif dsl_type == 'json':
            dsl_obj = json.loads(dsl)
        else:
            raise ValueError('dsl_type must be yaml or json')
    else:
        dsl_obj = dsl

    # 提取元数据
    metadata = dsl_obj.get('metadata', {})
    version = metadata.get('version', '1.0')
    description = metadata.get('description', '')
    logger.debug(f"工作流版本: {version}, 描述: {description}")

    # 处理输入节点 - 创建一个可以在运行时更新的工作流上下文
    workflow_input = dsl_obj.get('input', {})
    if workflow_input:
        input_data = workflow_input.get('data', workflow_input)  # 兼容直接定义数据的格式
        # 创建一个占位符上下文，运行时会被覆盖
        workflow_context = {'workflow_input': input_data}
        logger.debug(f"工作流输入数据: {input_data}")
    else:
        workflow_context = {}
        logger.debug("工作流没有定义输入节点")

    # 初始化执行器列表和依赖图
    executors = []
    dep_map = {}
    
    # 使用executors格式
    executors_config = dsl_obj.get('executors', [])
    
    for exe_conf in executors_config:
        name = exe_conf['name']
        exec_type = exe_conf.get('type', '')
        func_name = exe_conf['func']
        # 核心算子或者自定义函数
        if func_name not in func_map:
            raise ValueError(f"未找到函数: {func_name}，请检查DSL定义和函数映射")
        # 获取函数具体实现
        func = func_map[func_name]
        timeout = exe_conf.get('timeout', 60)
        retry = exe_conf.get('retry', 0)
        retry_interval = exe_conf.get('retry_interval', 1)
        context = exe_conf.get('context', {})
        model = exe_conf.get('model')
        kb = exe_conf.get('kb')
        ext_dep = exe_conf.get('ext_dep')
        custom_vars = exe_conf.get('custom_vars', {})
        intermediate = exe_conf.get('intermediate', {})
        context_params = exe_conf.get('context_params', {})
        logger.debug(f"解析占位符前的custom_vars: {exe_conf.get('custom_vars', {})}")
        context.update(workflow_context)  # 合并工作流全局上下文
        custom_vars = {key: resolve_placeholders(val, context) for key, val in exe_conf.get('custom_vars', {}).items()}
        logger.debug(f"解析占位符后的custom_vars: {custom_vars}")
        exe = Executor(
            name, exec_type, func,
            timeout=timeout, retry=retry, retry_interval=retry_interval,
            context=context, model=model, kb=kb, ext_dep=ext_dep,
            custom_vars=custom_vars, intermediate=intermediate, context_params=context_params
        )
        executors.append(exe)
        # 使用depends_on依赖声明
        depends_on = exe_conf.get('depends_on', [])
        if isinstance(depends_on, str):
            depends_on = [depends_on]
        dep_map[name] = depends_on

    # 处理输出节点
    workflow_output = dsl_obj.get('output', {})
    if workflow_output:
        # 兼容直接定义输出映射和在data字段下定义的格式
        output_data = workflow_output.get('data', workflow_output) if 'data' in workflow_output else workflow_output
        logger.debug(f"工作流输出映射: {output_data}")
        
        # 添加虚拟执行器来处理输出
        async def async_output_handler(*args, **kwargs):
            # 优先使用第一个位置参数作为结果
            if args:
                return args[0]
            # 如果没有位置参数,尝试从上下文获取结果
            for key, value in output_data.items():
                if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                    result = value[2:-1].split('.')
                    if len(result) > 1:
                        executor_name, output_field = result
                        if executor_name in workflow_context:
                            return workflow_context[executor_name][output_field]
            return None

        output_executor = Executor(
            name=workflow_output.get('name', 'workflow_output'),
            exec_type='output',
            func=async_output_handler,  # 使用async函数处理输出
            context={'output_mapping': output_data}
        )
        
        # 从占位符中提取依赖
        output_deps = []
        executor_names = [exe.name for exe in executors]  # 获取所有执行器名称
        
        for value in output_data.values():
            if isinstance(value, str):
                matches = re.findall(r"\$\{(.*?)\}", value)
                for match in matches:
                    step_name = match.split('.')[0]  # 提取步骤名称
                    # 只添加实际的执行器依赖，忽略workflow_input等
                    if step_name in executor_names:
                        output_deps.append(step_name)
        
        # 确保依赖列表中没有重复
        output_deps = list(set(output_deps))
        logger.debug(f"输出节点依赖: {output_deps}")
        
        executors.append(output_executor)
        if output_deps:
            dep_map[output_executor.name] = output_deps

    # 判断是否为DAG - 统一使用WorkFlow类处理
    is_dag = any(dep_map[name] for name in dep_map)
    if is_dag:
        workflow = WorkFlow(executors, force_sequential=False, dep_map=dep_map)
    else:
        force_sequential = dsl_obj.get('force_sequential', True)
        workflow = WorkFlow(executors, force_sequential=force_sequential)

    # 设置工作流属性
    workflow.metadata = metadata
    workflow.input = workflow_input
    workflow.output = workflow_output
    workflow.global_context = workflow_context

    return workflow
