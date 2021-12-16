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

@Step(pattern="^step 1$")
def step1(logger: TaskLogger, world: World,match: Match[str]):
    logger.log(f"step 1")
    world.setProp("itemA","hello")
    time.sleep(10)

@Step(pattern="^step 2$")
def step2(logger: TaskLogger, world: World,match: Match[str]):
    logger.log(f"step 1")
    value = world.getProp("itemA")
    logger.log(f"itemA: {value}")

if __name__ == '__main__':
    print(f"cpu count: {multiprocessing.cpu_count()}")
    tr = TaskRunner(debugMode=True)
    testResult = tr.run(["parallel_world.feature"])

    print("\nprogram elapsed time :", testResult.elapsed)

    if not testResult.success:
        print(f"Test failed")
        os._exit(1)