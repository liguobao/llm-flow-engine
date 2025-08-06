"""
数据流处理模块 - 处理数据组合、转换、流控制
"""
import json as pyjson
from typing import Any, Dict, List
from loguru import logger


async def combine_outputs(*args, prompt_template: str = None, combine_method: str = "template", 
                         input_mapping: Dict[str, str] = None, **kwargs) -> str:
    """
    组合多个输出，支持灵活的参数传递和组合方式
    
    Args:
        *args: 上游节点的输出
        prompt_template: 格式化模板，使用 {input_name} 等占位符
        combine_method: 组合方式 ('template', 'json', 'structured', 'custom')
        input_mapping: 输入映射，将位置参数映射到具名参数 {0: 'model1_result', 1: 'model2_result'}
        **kwargs: 其他参数，包括自定义组合逻辑
    """
    if not args:
        return ""
    
    logger.debug(f"combine_outputs: 接收到 {len(args)} 个输入参数，组合方式: {combine_method}")
    
    # 构建输入参数字典
    inputs = {}
    
    # 使用input_mapping映射参数名
    if input_mapping:
        for i, arg in enumerate(args):
            if i in input_mapping:
                inputs[input_mapping[i]] = str(arg)
            else:
                inputs[f'input{i+1}'] = str(arg)
    else:
        # 默认命名方式
        for i, arg in enumerate(args):
            inputs[f'input{i+1}'] = str(arg)
            inputs[f'output{i+1}'] = str(arg)  # 保持向后兼容
    
    # 添加kwargs中的参数
    for key, value in kwargs.items():
        if key not in ['prompt_template', 'combine_method', 'input_mapping']:
            inputs[key] = str(value)
    
    logger.debug(f"combine_outputs: 构建的输入字典: {list(inputs.keys())}")
    
    # 根据combine_method选择组合方式
    if combine_method == "template" and prompt_template:
        try:
            result = prompt_template.format(**inputs)
            logger.debug(f"combine_outputs: 模板格式化成功")
            return result
        except KeyError as e:
            logger.warning(f"模板格式化失败，缺少占位符: {e}")
            logger.warning(f"可用的占位符: {list(inputs.keys())}")
            return str(args[0]) if args else ""
    
    elif combine_method == "json":
        # 返回JSON格式的组合结果
        result = {
            "combined_inputs": inputs,
            "input_count": len(args),
            "timestamp": kwargs.get("timestamp", ""),
            "metadata": kwargs.get("metadata", {})
        }
        return pyjson.dumps(result, ensure_ascii=False, indent=2)
    
    elif combine_method == "structured":
        # 结构化组合，适用于多模型结果汇总
        sections = []
        for i, arg in enumerate(args, 1):
            section_name = input_mapping.get(i-1, f"输入{i}") if input_mapping else f"输入{i}"
            sections.append(f"## {section_name}\n{str(arg)}")
        
        if prompt_template:
            header = prompt_template.format(**inputs)
            return f"{header}\n\n" + "\n\n".join(sections)
        else:
            return "\n\n".join(sections)
    
    elif combine_method == "custom":
        # 自定义组合逻辑
        separator = kwargs.get("separator", "\n\n")
        prefix = kwargs.get("prefix", "")
        suffix = kwargs.get("suffix", "")
        
        combined = separator.join(str(arg) for arg in args)
        return f"{prefix}{combined}{suffix}"
    
    else:
        # 默认简单拼接
        return "\n\n".join(str(arg) for arg in args)


async def smart_parameter_pass(*args, target_function: str = None, parameter_mapping: Dict = None, 
                              context_data: Dict = None, **kwargs) -> Any:
    """
    智能参数传递函数 - 替代简单的combine_outputs
    
    Args:
        *args: 上游节点的输出
        target_function: 目标函数名称
        parameter_mapping: 参数映射规则 {'arg0': 'user_input', 'arg1': 'context'}
        context_data: 上下文数据
        **kwargs: 其他参数
    """
    # 延迟导入避免循环依赖
    logger.debug(f"smart_parameter_pass: 目标函数={target_function}, 映射={parameter_mapping}")
    
    # 构建目标函数的参数
    target_params = {}
    
    # 应用参数映射
    if parameter_mapping:
        for i, arg in enumerate(args):
            arg_key = f'arg{i}'
            if arg_key in parameter_mapping:
                target_param_name = parameter_mapping[arg_key]
                target_params[target_param_name] = arg
                logger.debug(f"映射参数: {arg_key} -> {target_param_name}")
    
    # 添加上下文数据
    if context_data:
        target_params.update(context_data)
    
    # 添加其他参数
    target_params.update(kwargs)
    
    # 如果指定了目标函数，尝试调用
    if target_function:
        try:
            from . import BUILTIN_FUNCTIONS
            if target_function in BUILTIN_FUNCTIONS:
                func = BUILTIN_FUNCTIONS[target_function]
                logger.debug(f"调用目标函数 {target_function}，参数: {target_params}")
                return await func(**target_params)
        except ImportError:
            logger.warning("无法导入BUILTIN_FUNCTIONS，返回参数字典")
    
    # 否则返回构建好的参数字典
    return target_params


async def data_flow_transform(*args, transform_rules: List[Dict] = None, **kwargs) -> Any:
    """
    数据流转换函数 - 提供更灵活的数据处理
    
    Args:
        *args: 输入数据
        transform_rules: 转换规则列表 [{'type': 'extract', 'field': 'content'}, {'type': 'format', 'template': '...'}]
        **kwargs: 其他参数
    """
    if not args:
        return {}
    
    current_data = list(args)
    
    if transform_rules:
        for rule in transform_rules:
            rule_type = rule.get('type')
            
            if rule_type == 'extract':
                # 提取字段
                field = rule.get('field')
                if field:
                    current_data = [
                        item.get(field, item) if isinstance(item, dict) else str(item)
                        for item in current_data
                    ]
            
            elif rule_type == 'filter':
                # 过滤数据
                condition = rule.get('condition', lambda x: True)
                current_data = [item for item in current_data if condition(item)]
            
            elif rule_type == 'format':
                # 格式化数据
                template = rule.get('template', '{data}')
                current_data = [
                    template.format(data=item) for item in current_data
                ]
            
            elif rule_type == 'aggregate':
                # 聚合数据
                method = rule.get('method', 'join')
                if method == 'join':
                    separator = rule.get('separator', '\n')
                    current_data = [separator.join(str(item) for item in current_data)]
                elif method == 'count':
                    current_data = [len(current_data)]
    
    return current_data[0] if len(current_data) == 1 else current_data
