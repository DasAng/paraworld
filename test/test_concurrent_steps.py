import time
import sys
import os
from typing import Match
sys.path.append(os.path.join(os.path.dirname(__file__),'../'))
from conclave.task_runner import TaskRunner
from conclave.step import Step
from conclave.world import World
import multiprocessing
from conclave.monitor import Monitor
from conclave.task_runner import TaskRunner
from conclave.task_logger import TaskLogger

@Step(pattern="^step1$")
def step1(logger: TaskLogger, world: World,match: Match[str]):
    logger.log(f"step1 called")
    time.sleep(1)
    #raise Exception("step1 exception")

@Step(pattern="^step2$")
def step2(logger: TaskLogger, world: World,match: Match[str]):
    logger.log(f"step2 called")
    time.sleep(2)
    

if __name__ == '__main__':
    print(f"cpu count: {multiprocessing.cpu_count()}")
    tr = TaskRunner(debugMode=True)
    testResult = tr.run(["concurrent_steps.feature"])

    print("\nprogram elapsed time :", testResult.elapsed)
    
    tr.generateTimeline()

    if not testResult.success:
        print(f"Test failed")
        os._exit(1)