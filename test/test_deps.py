import time
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__),'../'))
from conclave.task_runner import TaskRunner
from conclave.step import Step
from conclave.world import World
from conclave.task_runner import TaskRunner

@Step(pattern="^step 1$")
def func1(logger, world: World):
    logger.log(f"func1 called")

if __name__ == '__main__':
    program_start = time.time()
    my_pid = os.getpid()
    print(f"process pid: {my_pid}")
    tr = TaskRunner(debugMode=True)
    error = tr.run(["dep.feature"])

    program_end = time.time()
    print("\nprogram elapsed time :", program_end-program_start)

    tr.generateTimeline()
    tr.generateDependencyGraph()

    if error:
        print(f"Test failed")
        sys.exit(1)