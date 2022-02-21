from dataclasses import dataclass
from typing import Any, Callable, Optional
import time
import traceback
import functools
import re
import os
import threading
from datetime import datetime

from .task_logger import TaskLogger
from .step_definition import StepDefinition

@dataclass
class StepResult:
    elapsed: float
    result: Any
    error: str
    threadId: int
    pid: int
    start: Any
    end: Any
    log: str

class Step:

    """
    A decorator class that can be used to mark methods as being a step definition in gherkin
    Example usage:

    @Step(pattern="I login to webiste")
    def mystep(logger, world, match):
        logger.log(f"mystep called")
    """ 
    stepDefinitions: list[StepDefinition] = []

    def __init__(self, pattern: str) -> None:
        self.pattern = pattern

    def __call__(self, func) -> Any:
        
        @functools.wraps(func)
        def wrapper_func(*args,**kwargs):
            start = time.time()
            pid = os.getpid()
            threadId = threading.get_ident()
            result,exc,elapsed = None,None,0.0
            logger = TaskLogger(f"{args[0].funcName}/{func.__name__}")
            parentLogger = args[0]
            newargs = list(args)
            newargs[0] = logger
            args2 = tuple(newargs)
            try:
                result = func(*args2,**kwargs)
            except Exception:
                exc = traceback.format_exc()
            finally:
                end = time.time()
                elapsed = end-start
                parentLogger.msg += logger.msg
                return StepResult(elapsed,result,exc,threadId,pid,datetime.fromtimestamp(start),datetime.fromtimestamp(end),logger.msg)
        Step.stepDefinitions.append(StepDefinition(self.pattern,wrapper_func))
        return wrapper_func
    
    @staticmethod
    def getStep(text: str) -> Optional[Callable]:
        for step in Step.stepDefinitions:
            result = re.search(step.pattern,text)
            if result:
                return step.func,result
        return None,None
