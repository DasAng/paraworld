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
    program_start = time.time()
    print(f"cpu count: {multiprocessing.cpu_count()}")
    my_pid = os.getpid()
    print(f"process pid: {my_pid}")
    tr = TaskRunner(debugMode=True)
    error = tr.run(["match_group.feature"])

    program_end = time.time()
    print("\nprogram elapsed time :", program_end-program_start)

    if error:
        print(f"Test failed")
        sys.exit(1)