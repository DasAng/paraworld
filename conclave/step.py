from dataclasses import asdict, dataclass
import multiprocessing
from typing import Any, Callable, Optional
import time
import traceback
import functools
import re
import os
import threading
from datetime import datetime

from .feedback_schema import FeatureInfo, ScenarioInfo, StepFeedback
from .task_logger import TaskLogger
from .step_definition import StepDefinition
from .step_result import StepResult

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
            gherkinStep = newargs[3]
            gherkinScenario = newargs[4]
            gherkinFeature = newargs[5]
            scenarioScope = newargs[6]
            feedbackQueue = newargs[-1]
            newargs.pop()
            newargs.pop()
            newargs.pop()
            newargs.pop()
            newargs.pop()
            newargs.append(scenarioScope)
            args2 = tuple(newargs)
            try:
                self.notifyStepStarted(feedbackQueue,start,gherkinStep,gherkinScenario,gherkinFeature)
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
    
    def notifyStepStarted(self,queue: multiprocessing.Queue, start: float, gherkinStep: Any, gherkinScenario: Any, gherkinFeature: Any):
        try:
            msg = asdict(StepFeedback(
                threadId=threading.get_ident(),
                elapsed=0,
                endTime=None,
                pid=os.getpid(),
                startTime=datetime.fromtimestamp(start),
                status="starting",
                column=gherkinStep["location"]["column"],
                line=gherkinStep["location"]["line"],
                keyword=gherkinStep["keyword"],
                text=gherkinStep["text"],
                scenario=ScenarioInfo(
                    name=gherkinScenario["name"],
                    column=gherkinScenario["location"]["column"],
                    line=gherkinScenario["location"]["line"],
                    description=gherkinScenario["description"],
                    tags=[t["name"] for t in gherkinScenario["tags"]],
                    numberOfSteps=len(gherkinScenario["steps"])
                ),
                feature=FeatureInfo(
                    description=gherkinFeature["description"],
                    name=gherkinFeature["name"],
                    tags=[t["name"] for t in gherkinFeature["tags"]]
                )
            ))
            queue.put_nowait(msg)
        except:
            pass
 
    
    @staticmethod
    def getStep(text: str) -> Optional[Callable]:
        for step in Step.stepDefinitions:
            result = re.search(step.pattern,text)
            if result:
                return step.func,result
        return None,None
