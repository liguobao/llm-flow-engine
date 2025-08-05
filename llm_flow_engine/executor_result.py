import time
from typing import Any, Optional

class ExecutorResult:
    def __init__(self, exec_type: str, start_time: float, end_time: float, status: str, error: Optional[str],
                 custom_vars: dict = None, intermediate: dict = None, context_params: dict = None, output: Any = None):
        self.exec_time = end_time - start_time
        self.status = status
        self.error = error
        self.custom_vars = custom_vars or {}
        self.intermediate = intermediate or {}
        self.context_params = context_params or {}
        self.output = output
        self.exec_type = exec_type

    def to_dict(self):
        return {
            'exec_time': self.exec_time,
            'status': self.status,
            'error': self.error,
            'custom_vars': self.custom_vars,
            'intermediate': self.intermediate,
            'context_params': self.context_params,
            'output': self.output
        }
