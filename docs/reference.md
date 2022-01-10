# Reference

**Table of contents**

- [class TaskRunner](#class-taskrunner)
    - [constructor(debugMode,timeout)](#constructordebugmodetruetimeout3600)
    - [run(featureFiles)](#runfeaturefiles)

# Class TaskRunner

This is the core engine of **paraworld** that is responsible for running feature files.

## Constructor(debugMode=True,timeout=3600)

- `debugMode`: \<bool> if True then prints debug messages. Default is False.
- `timeout`: \<int> a timeout value ins seconds. If the elapsed time of running the feature files exceeds the timeout value then the TaskRunner will abort the execution. Default value is 3600 seconds.
- returns \<None>

Your application code will need to instantiate an instance of the TaskRunner class and call it's [run()](#runfeaturefiles) method to run one or more feature files.

Example:

```python
tr = TaskRunner(debugMode=True)
testResult = tr.run(["test.feature"])
```

## Run(featureFiles)

- `featureFiles`: \<list[str]> A list of filepaths of the feature files to run.
- returns \<[TestResultInfo](#testresultinfo)> object