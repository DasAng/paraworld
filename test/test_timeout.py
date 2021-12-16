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

@Step(pattern="^run for long time$")
def longRunningStep(logger: TaskLogger, world: World,match: Match[str]):
    logger.log(f"long running step")
    time.sleep(30)

if __name__ == '__main__':
    print(f"cpu count: {multiprocessing.cpu_count()}")
    my_pid = os.getpid()
    print(f"process pid: {my_pid}")
    tr = TaskRunner(debugMode=True,timeout=10)
    testResult = tr.run(["timeout.feature"])

    print("\nprogram elapsed time :", testResult.elapsed)
    tr.generateTimeline()
    tr.generateReport()

    if not testResult.success:
        print(f"Test failed")
        os._exit(1)
            
