# Paraworld

This is a BDD framework using the Gherkin language to define tests. The framework is written in Python 3.9.

It can run scenarios sequentially, in parallel or concurrently or in any combination.
It also supports running steps concurrently using the custom keyword *concurrent* instead of *Given and Then*

# Usage

To use the framework install it through pip:

```shell
pip install paraworld
```

Below is an example code using paraworld to run a sample feature file:

```python
import time
import sys
import os
from conclave.task_runner import TaskRunner
from conclave.step import Step
from conclave.world import World
import multiprocessing
from conclave.task_runner import TaskRunner

## define a step matching the word: "This is a test step"
@Step(pattern="^This is a test step$")
def testStep(logger, world: World):
    logger.log(f"test step called")
    world.setProp("testValue",["hello"])
    logger.log(f"world object ab: {world.getProp('testValue')}")

if __name__ == '__main__':
    program_start = time.time()
    tr = TaskRunner(debugMode=True)
    error = tr.run(["concurrent.feature"])

    program_end = time.time()
    print("\nprogram elapsed time :", program_end-program_start)

    if error:
        print(f"Test failed")
        sys.exit(1)
```

And the feature file looks like this:

```feature
Feature: Test feature

    Feature Description

    @concurrent
    Scenario: scenario 1
        Then This is a test step
```

The above code will run the scenario *scenario 1* concurrently, due to tag *@concurrent*

# How to build

To test the build locally create a virtual environment:

```shell
python -m venv paraworld-env
paraworld-env\Scripts\activate.bat
```

If not already installed then install the build package:

```shell
python -m pip install --upgrade build
```

Build the report first by doing the following:

*Window*:

```shell
cd report
npm run build_window
cd ..
```

Then run the build command

```shell
python -m build
```

The will create a gz and whl file inside a **dist** folder

# Test locally

To test the build locally create a virtual environment:

*Windows*:

```shell
python -m venv test-env
test-env\Scripts\activate.bat
```

Then run pip install the **whl** file that is created by the build command:

```shell
pip install <path to paraworld whl file>
```

So if the whl file is in dist and called **paraworld-0.0.1-py3-none-any.whl** then run:

```shell
pip install dist/paraworld-0.0.1-py3-none-any.whl
```

Now lets test the installed package, by running the test file **test_local_build.py**:

```shell
cd test
python test_local_build.py
```

# Publish to TestPyPI

Before publishing to PyPI you can upload to TestPyPI for testing the package:

```shell
twine upload --repository testpypi dist/*
``` 

This will upload whatever is in the **dist** folder to TestPyPI.

To test out the newly published package:

```shell
python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ paraworld
```