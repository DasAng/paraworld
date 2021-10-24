from concurrent.futures import ThreadPoolExecutor, wait
import concurrent
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

    def run(self):
        """
        Execute the scenario
        """
        self.logger.log(f"Run scenario: {self.name}")
        my_pid = os.getpid()
        self.logger.log(f"process pid: {my_pid}")
        self.logger.log(f"thread id: {threading.get_ident()}")
        start = time.time()
        exc, message, id, elapsed = None,None,None,None
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
            id = self.id
            return exc,message,id,elapsed
    
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

            if len(consteps) > 0:
                workerThread = threading.Thread(target=self.runWorkerThread,kwargs={'taskList':consteps})
                workerThread.start()

            for step in seqsteps:
                self.logger.log(f"execute step: {step['keyword']} {step['text']}")
                func = Step.getStep(step['text'])
                if func:
                    func(self.logger,self.world)
        finally:
            if workerThread is not None:
                workerThread.join()
    
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
            func = Step.getStep(step['text'])
            if func:
                futures[self.pool.submit(func, self.logger, self.world)] = step
        #     if task.isConcurrent:
        #         futures[self.pool.submit(task.scenario.run)] = task
        #     elif task.isParallel:
        #         futures[self.parallelPool.submit(task.scenario.run)] = task
        
        self.logger.log(f"add steps for concurrent executions: {[t['keyword']+t['text'] for t in futures.values()]}")

        self.stepsError = {}
        while futures:
            done, _ = wait(futures,return_when=concurrent.futures.FIRST_COMPLETED)
            for c in done:
                fut = futures.pop(c)
                try:
                    c.result()
                except Exception:
                    self.stepsError[fut["keyword"]+fut["text"]] = {traceback.format_exc()}
                    self.logger.error(f"failed: {traceback.format_exc()}")
                
                self.logger.log(f"completed step: {fut['keyword']} {fut['text']}")
    
    def __getstate__(self):
        state = self.__dict__.copy()
        del state["pool"]
        return state
    
    def __setstate__(self,state):
        self.__dict__.update(state)
        self.pool = ThreadPoolExecutor()
             
