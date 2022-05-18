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
from conclave.scenario_scope import ScenarioScope

@Step(pattern="^calculate pi$")
def calcPi(logger: TaskLogger, world: World,match: Match[str], context: ScenarioScope):
    logger.log(f"calcPi called")
    pi = 0
    accuracy = 100000

    for i in range(50):
        for i in range(0, accuracy):
            pi += ((4.0 * (-1)**i) / (2*i + 1))
    logger.log(f"done calc pi")

if __name__ == '__main__':
    mon = Monitor()
    print(f"cpu count: {multiprocessing.cpu_count()}")
    my_pid = os.getpid()
    #mon.startMonitor()
    print(f"process pid: {my_pid}")
    tr = TaskRunner(debugMode=True)
    testResult = tr.run(["cpu_multi_thread.feature"])

    print("\nprogram elapsed time :", testResult.elapsed)

    #mon.stopMonitor()
    #mon.generateReport()

    tr.generateTimeline()
    tr.generateReport()

    if not testResult.success:
        print(f"Test failed")
        os._exit(1)