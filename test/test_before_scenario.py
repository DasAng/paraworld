from random import randint
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
from conclave.scenario_scope import ScenarioScope

@BeforeScenario()
def before_scenario(logger: TaskLogger, world: World, context: ScenarioScope):
    logger.log(f"Before scenario")
    context.num = randint(0,100)
    logger.log(f"context.num: {context.num}")
    #raise Exception("Force error")

@AfterScenario()
def after_scenario(logger: TaskLogger, world: World, context: ScenarioScope):
    logger.log(f"After scenario")
    raise Exception("Force after error")

@Step(pattern="^step 1$")
def step1(logger: TaskLogger, world: World,match: Match[str], context: ScenarioScope):
    logger.log(f"step 1")
    logger.log(f"context name: {context.num}")

if __name__ == '__main__':
    print(f"cpu count: {multiprocessing.cpu_count()}")
    tr = TaskRunner(debugMode=True)
    testResult = tr.run(["before_scenario.feature"])

    print("\nprogram elapsed time :", testResult.elapsed)

    tr.generateReport()

    if not testResult.success:
        print(f"Test failed")
        os._exit(1)