import time
import sys
import os
from typing import Match
sys.path.append(os.path.join(os.path.dirname(__file__),'../'))
from conclave.task_runner import TaskRunner
from conclave.step import Step
from conclave.before_scenario import BeforeScenario
from conclave.after_scenario import AfterScenario
from conclave.world import World
import multiprocessing
from conclave.task_runner import TaskRunner
from conclave.task_logger import TaskLogger

@BeforeScenario()
def before_scenario(logger: TaskLogger, world: World):
    logger.log(f"Before scenario")
    raise Exception("Force error")

@AfterScenario()
def after_scenario(logger: TaskLogger, world: World):
    logger.log(f"After scenario")
    raise Exception("Force after error")

@Step(pattern="^step 1$")
def step1(logger: TaskLogger, world: World,match: Match[str]):
    logger.log(f"step 1")

if __name__ == '__main__':
    print(f"cpu count: {multiprocessing.cpu_count()}")
    tr = TaskRunner(debugMode=True)
    testResult = tr.run(["before_scenario.feature"])

    print("\nprogram elapsed time :", testResult.elapsed)

    if not testResult.success:
        print(f"Test failed")
        os._exit(1)