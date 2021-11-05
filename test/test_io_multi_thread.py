import time
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__),'../'))
from conclave.task_runner import TaskRunner
from conclave.step import Step
from conclave.world import World
import multiprocessing
from conclave.monitor import Monitor
from conclave.task_runner import TaskRunner
import requests

@Step(pattern="^call api$")
def callApi(logger, world: World):
    logger.log(f"callApi called")
    x = requests.get('https://httpbin.org/delay/2')
    logger.log(f"response: {x}")

if __name__ == '__main__':
    program_start = time.time()
    mon = Monitor()
    print(f"cpu count: {multiprocessing.cpu_count()}")
    my_pid = os.getpid()
    #mon.startMonitor()
    print(f"process pid: {my_pid}")
    tr = TaskRunner(debugMode=True)
    error = tr.run(["io_multi_thread.feature"])

    program_end = time.time()
    print("\nprogram elapsed time :", program_end-program_start)

    #mon.stopMonitor()
    #mon.generateReport()

    tr.generateTimeline()

    if error:
        print(f"Test failed")
        sys.exit(1)