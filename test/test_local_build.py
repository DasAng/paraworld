import time
import sys
import os
from conclave.task_runner import TaskRunner
from conclave.step import Step
from conclave.world import World
import multiprocessing
from conclave.task_runner import TaskRunner

if __name__ == '__main__':
    print(f"cpu count: {multiprocessing.cpu_count()}")
    tr = TaskRunner(debugMode=True)
    testResult = tr.run(["concurrent.feature"])

    print("\nprogram elapsed time :", testResult.elapsed)

    if not testResult.success:
        print(f"Test failed")
        os._exit(1)