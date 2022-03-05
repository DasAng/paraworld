import time
import sys
import os
from typing import Match

from conclave.task_runner_config import TaskRunnerConfig
sys.path.append(os.path.join(os.path.dirname(__file__),'../'))
from conclave.task_runner import TaskRunner
from conclave.step import Step
from conclave.world import World
from conclave.task_runner import TaskRunner
from conclave.task_logger import TaskLogger
from conclave.task_runner_config import TaskRunnerConfig

@Step(pattern="^step 1$")
def func1(logger: TaskLogger, world: World,match: Match[str]):
    logger.log(f"func1 called")

if __name__ == '__main__':
    my_pid = os.getpid()
    print(f"process pid: {my_pid}")
    tr = TaskRunner(debugMode=True)
    testResult = tr.run(TaskRunnerConfig(featureFiles=["dep.feature", "test-dir", "dep.feature"],onlyRunScenarioTags=["@scenario4"]))

    print("\nprogram elapsed time :", testResult.elapsed)

    tr.generateTimeline()
    tr.generateDependencyGraph()
    tr.generateReport()

    if not testResult.success:
        print(f"Test failed")
        os._exit(1)