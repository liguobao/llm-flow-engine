import re
from loguru import logger

def resolve_placeholders(value, context):
    """解析占位符 ${...}，并用 context 中的值替换"""
    logger.debug(f"resolve_placeholders: value={value}, context keys={list(context.keys()) if isinstance(context, dict) else 'not dict'}")
    
    if isinstance(value, str):
        # 匹配 ${node.output} 或 ${workflow_input.key} 格式的占位符
        matches = re.findall(r'\$\{(\w+)\.(\w+)\}', value)
        for node_name, attr in matches:
            placeholder = f'${{{node_name}.{attr}}}'
            resolved_value = None
            
            # 从 context 中查找对应的值
            if node_name in context:
                node_output = context[node_name]
                if isinstance(node_output, dict) and attr in node_output:
                    resolved_value = node_output[attr]
                elif hasattr(node_output, attr):
                    resolved_value = getattr(node_output, attr)
                else:
                    # 直接使用节点输出作为默认值
                    resolved_value = node_output
                
                # 执行替换
                if resolved_value is not None:
                    # 如果整个字符串就是一个占位符，直接返回值
                    if value.strip() == placeholder:
                        return resolved_value
                    # 否则进行字符串替换
                    value = value.replace(placeholder, str(resolved_value))
                    logger.debug(f"替换占位符 {placeholder} -> {resolved_value}")
            else:
                logger.debug(f"找不到匹配的值: {node_name} in context keys: {list(context.keys()) if isinstance(context, dict) else context}")
        
        return value
    elif isinstance(value, dict):
        return {k: resolve_placeholders(v, context) for k, v in value.items()}
    elif isinstance(value, list):
        return [resolve_placeholders(v, context) for v in value]
    else:
        return value
