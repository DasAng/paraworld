from typing import Any, Callable, Optional
import functools
import re
from .step_definition import StepDefinition

class Step:

    """
    A decorator class that can be used to mark methods as being a step definition in gherkin
    Example usage:

    @Step(pattern="I login to webiste")
    def mystep(logger):
        logger.log(f"mystep called")
    """ 
    stepDefinitions: list[StepDefinition] = []

    def __init__(self, pattern: str) -> None:
        self.pattern = pattern

    def __call__(self, func) -> Any:
        
        @functools.wraps(func)
        def wrapper_func(*args,**kwargs):
            return func(*args,**kwargs)
        Step.stepDefinitions.append(StepDefinition(self.pattern,wrapper_func))
        return wrapper_func
    
    @staticmethod
    def getStep(text: str) -> Optional[Callable]:
        for step in Step.stepDefinitions:
            result = re.search(step.pattern,text)
            if result:
                return step.func
        return None
