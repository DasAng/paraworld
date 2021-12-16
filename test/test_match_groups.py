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

@Step(pattern="^match group (.+) and (.+)$")
def matchGroup(logger: TaskLogger, world: World,match: Match[str]):
    logger.log(f"matchgroup called")
    group1 = match.group(1)
    group2 = match.group(2)
    logger.log(f"match group 1: {group1}")
    logger.log(f"match group 2: {group2}")

if __name__ == '__main__':
    print(f"cpu count: {multiprocessing.cpu_count()}")
    tr = TaskRunner(debugMode=True)
    testResult = tr.run(["match_group.feature"])

    print("\nprogram elapsed time :", testResult.elapsed)

    if not testResult.success:
        print(f"Test failed")
        os._exit(1)