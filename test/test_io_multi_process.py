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
import requests
from conclave.scenario_scope import ScenarioScope

@Step(pattern="^call api$")
def callApi(logger: TaskLogger, world: World,match: Match[str], context: ScenarioScope):
    logger.log(f"callApi called")
    x = requests.get('https://httpbin.org/delay/2')
    logger.log(f"response: {x}")

if __name__ == '__main__':
    mon = Monitor()
    print(f"cpu count: {multiprocessing.cpu_count()}")
    #mon.startMonitor()
    tr = TaskRunner(debugMode=True)
    testResult = tr.run(["io_multi_process.feature"])

    print("\nprogram elapsed time :", testResult.elapsed)

    #mon.stopMonitor()
    #mon.generateReport()

    tr.generateTimeline()
    tr.generateReport()

    if not testResult.success:
        print(f"Test failed")
        os._exit(1)