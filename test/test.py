import time
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__),'../'))
from conclave.task_runner import TaskRunner
from conclave.step import Step
from conclave.world import World
import multiprocessing

from conclave.task_runner import TaskRunner

if __name__ == '__main__':
    program_start = time.time()
    print(f"cpu count: {multiprocessing.cpu_count()}")
    my_pid = os.getpid()
    print(f"process pid: {my_pid}")
    tr = TaskRunner(debugMode=True)
    error = tr.run(["concurrent.feature"])

    program_end = time.time()
    print("\nprogram elapsed time :", program_end-program_start)

    if error:
        print(f"Test failed")
        sys.exit(1)