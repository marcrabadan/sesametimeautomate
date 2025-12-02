from abc import abstractmethod
from typing import Any

class Runnable:
    def __or__(self, other) -> "RunnableSequence":
        return RunnableSequence(self, other)
    
    @abstractmethod
    def execute(self, data: dict[str, Any] | None = None) -> dict[str, Any]:
        raise NotImplementedError()

class RunnableSequence:
    def __init__(self, *steps: Runnable):
        for i, step in enumerate(steps):
            if not isinstance(step, Runnable):
                raise TypeError(f"Step {i} must be an instance of Runnable, got {type(step).__name__}")
        self.steps = steps
    
    def __or__(self, other: Runnable) -> 'RunnableSequence':
        if not isinstance(other, Runnable):
            raise TypeError(f"Cannot chain non-Runnable object of type {type(other).__name__}")
        return RunnableSequence(*self.steps, other)
    
    def invoke(self, initial_data: Any = None) -> Any:
        result = initial_data if initial_data is not None else {}
        
        if not isinstance(result, dict):
            result = {'initial_data': result}
        
        for step in self.steps:
            step_result = step.execute(result)
            
            if isinstance(step_result, dict):
                result.update(step_result)
            else:
                step_name = step.__class__.__name__
                result[f'{step_name}_result'] = step_result
                
        return result
