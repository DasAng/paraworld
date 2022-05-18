import functools
import traceback
from dataclasses import dataclass
from typing import Any, Callable, Optional

@dataclass
class AfterScenarioResult:
    error: str
    result: Any

class AfterScenario:

    methods: list[Callable] = []

    def __init__(self) -> None:
        pass

    def __call__(self, func) -> Any:

        @functools.wraps(func)
        def wrapper_func(*args,**kwargs):
            result, error = None, None
            try:
                result = func(*args,**kwargs)
            except Exception:
                error = traceback.format_exc()
            finally:
                return AfterScenarioResult(error=error,result=result)
        AfterScenario.methods.append(wrapper_func)
        return wrapper_func
    
    @staticmethod
    def getMethods() -> Optional[list[Callable]]:
        return AfterScenario.methods
