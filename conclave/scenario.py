from concurrent.futures import ThreadPoolExecutor, wait
import concurrent
from typing import Any
from datetime import datetime
from .scenario_result import ScenarioResult

from .task_logger import TaskLogger
import traceback
import time
import os
import threading
from .step import Step
from .world import World

class Scenario:

    """
    This class represents a scenario in Gherkin. A scenario consists of steps which
    will be executed one by one. All background steps will be executed before the
    steps of a scenario
    """
    def __init__(self, name, gherkinScenario,gherkinFeature,id):
        self.name = name
        self.logger = TaskLogger(name)
        self.gherkinScenario = gherkinScenario
        self.id = id
        self.gherkinFeature = gherkinFeature
        self.steps = self.__getAllSteps()
        self.world = World()
        self.pool = ThreadPoolExecutor()
        self.stepsError = {}
        self.result = ScenarioResult(scenario=self.gherkinScenario,id=self.id,steps=self.steps,threadId=None,pid=None,startTime=None,endTime=None)

    def run(self):
        """
        Execute the scenario
        """
        self.logger.log(f"Run scenario: {self.name}")
        my_pid = os.getpid()
        self.logger.log(f"process pid: {my_pid}")
        self.logger.log(f"thread id: {threading.get_ident()}")
        start = time.time()
        exc = None
        try:
            self.__runSteps()
            if self.stepsError:
                for key in self.stepsError:
                    exc = f"Concurrent/parallel step: {key}\n{self.stepsError[key]}\n"
        except Exception:
            exc = f"failed: {traceback.format_exc()}"
            if self.stepsError:
                for key in self.stepsError:
                    exc += f"\nConcurrent/parallel step: {key}\n{self.stepsError[key]}\n"
            self.logger.error(f"{exc}")
        finally:
            end = time.time()
            elapsed = end-start
            self.logger.log(f"elapsed time: {end-start}")
            message = self.logger.msg
            self.result.message = message
            self.result.exception = exc
            self.result.elapsed = elapsed
            self.result.threadId = threading.get_ident()
            self.result.pid = os.getpid()
            self.result.startTime = datetime.fromtimestamp(start)
            self.result.endTime = datetime.fromtimestamp(end)
            return self.result

    
    def msg(self):
        return self.logger.msg
    

    def __getBackgroundSteps(self):
        """
        Get all background steps for a scenario
        """
        backgroundSteps = []
        for child in self.gherkinFeature["children"]:
            if "background" in child:
                bg = child["background"]
                if "steps" in bg:
                    backgroundSteps.extend(bg["steps"])
        return backgroundSteps

    def __getSteps(self):
        """
        Get all main steps for a scenario
        """
        steps = []
        if "steps" in self.gherkinScenario:
            steps.extend(self.gherkinScenario["steps"])
        return steps

    def __getAllSteps(self):
        """
        Get all steps for a scenario. This will be a combined list of background steps and main steps
        """
        bgSteps = self.__getBackgroundSteps()
        steps = self.__getSteps()
        bgSteps.extend(steps)
        return bgSteps

    def __runSteps(self):
        """
        Execute all steps in the scenario
        """
        workerThread = None

        try:
            consteps = self.__getAllConcurrentSteps()
            seqsteps = self.__getAllSequentialSteps()

            for step in self.steps:
                self.__updateStep(step, "skipped", None, 0.0, None, None,None,None, "")

            if len(consteps) > 0:
                workerThread = threading.Thread(target=self.runWorkerThread,kwargs={'taskList':consteps})
                workerThread.start()

            for step in seqsteps:
                exc = None
                self.logger.log(f"execute step: {step['keyword']} {step['text']}")
                func,match = Step.getStep(step['text'])
                if func:
                    result = func(self.logger,self.world,match)
                    if result.error:
                        self.__updateStep(step, "failed", result.error, result.elapsed, result.pid,result.threadId,result.start,result.end,result.log)
                        raise Exception(result.error)
                    else:
                        self.__updateStep(step, "success", result.error, result.elapsed,result.pid,result.threadId,result.start,result.end,result.log)
                else:
                    self.__updateStep(step, "skipped", f"Could not find matching step definition for: {step['keyword']}{step['text']}",0.0,None,None,None,None,"")
                    raise Exception(f"Could not find matching step definition for: {step['keyword']}{step['text']}")
                    
        finally:
            if workerThread is not None:
                workerThread.join()
    
    def __updateStep(self, step: Any, status: str,error: str, elapsed: int, pid: int,threadId: int,start: Any, end: Any, log: str):
        item = next((x for x in self.steps if x['id'] == step['id']), None)
        if item:
            item["status"] = status
            step["error"] = error
            step["elapsed"] = elapsed
            step["pid"] = pid
            step["threadId"] = threadId
            step["start"] = start
            step["end"] = end
            step["log"] = log

    def __getAllConcurrentSteps(self):
        """
        Retrieve all steps marked to be run concurrently
        """
        return list(filter(lambda x: x["keyword"] == "Concurrent ", self.steps))
    
    def __getAllSequentialSteps(self):
        """
        Retrieve all sequential steps
        """
        return list(filter(lambda x: x["keyword"] != "Concurrent ", self.steps))
    
    def runWorkerThread(self, taskList):
        futures = {}
        for step in taskList:
            func,match = Step.getStep(step['text'])
            if func:
                futures[self.pool.submit(func, self.logger, self.world,match)] = step
            else:
                self.__updateStep(step, "skipped", f"Could not find matching step definition for: {step['keyword']}{step['text']}",0.0,None,None,None,None,"")
        
        self.logger.log(f"add steps for concurrent executions: {[t['keyword']+t['text'] for t in futures.values()]}")

        self.stepsError = {}
        while futures:
            done, _ = wait(futures,return_when=concurrent.futures.FIRST_COMPLETED)
            for c in done:
                fut = futures.pop(c)
                result = c.result()
                if result.error:
                    self.stepsError[fut["keyword"]+fut["text"]] = result.error
                    self.logger.error(f"failed: {result.error}")
                    self.__updateStep(fut,"failed",result.error,result.elapsed,result.pid,result.threadId,result.start,result.end,result.log)
                else:
                    self.__updateStep(fut,"success",None,result.elapsed,result.pid,result.threadId,result.start,result.end,result.log)
                
                self.logger.log(f"completed step: {fut['keyword']} {fut['text']}")
    
    def __getstate__(self):
        state = self.__dict__.copy()
        del state["pool"]
        return state
    
    def __setstate__(self,state):
        self.__dict__.update(state)
        self.pool = ThreadPoolExecutor()
             
