# Reference

**Table of contents**

- [class Step](#class-step)
    - [constructor(pattern)](#constructorpattern)
- [class TaskLogger](#class-tasklogger)
    - [constructor(funcName)](#constructorfuncname)
    - [log(msg)](#logmsg)
    - [error(msg)](#errormsg)
- [class TaskRunner](#class-taskrunner)
    - [constructor(debugMode,timeout)](#constructordebugmodefalsetimeout3600)
    - [generateDepencyGraph()](#generatedependencygraph)
    - [generateReport()](#generatereport)
    - [generateTimeline()](#generatetimeline)
    - [run(featureFiles)](#runfeaturefiles)
- [class TestResultInfo](#class-testresultinfo)
    - [elapsed: \<int>](#elapsed-int)
    - [end: \<str>](#end-str)
    - [numCpu: \<int>](#numcpu-int)
    - [pid: \<int>](#pid-int)
    - [start: \<str>](#start-str)
    - [success: \<bool>](#success-bool)
- [class World](#class-world)
    - [getProp(key)](#getpropkey)
    - [setProp(key,value)](#setpropkeyvalue)

# Class Step

A decorator class that can be used to mark methods as being a step definition in gherkin. This class is used to define a regular expression that can be mapped between gherkin steps and your own functions.

Let's illustrate this to better understand it's usage. Imagine you have written a feature file with the following scenario and step:

```feature
Feature: Test database connectivity
    Scenario: connect to database successfully
        Then login to database using master
```

Next we will have to implement the functionality for the step *login to database using master*. Let's create function to implement the code to login to a database:

```python
def loginToDatabaseStep():
    .... implementation goes here
```

But how does the TaskRunner class know that this method is supposed to be executed when it encounters the step *login to database using master*? Well the answer to that is to use the **Step** class decorator and add it to you method like the following:

```python
@Step(pattern="login to database using master")
def loginToDatabaseStep(logger: TaskLogger, world: World, match: Match[str]):
    .... implementation goes here
```

The above code shows that we have decorated our *loginToDatabaseStep* with the **Step** class and set the *pattern* paramter to a regular expression that will be used to match against gherkin steps. In addition we have refactored our *logintoDatabaseStep* method to pass in three additional parameters *logger, world, and match*. When using the **Step** decorator your method must have the three parameters:

- `logger`: \<[TaskLogger](#class-tasklogger)> an instance of a logger that can be used to print log statement to console.
- `world`: \<[World](#class-world)> an instance of a **World** object that can be used to store and retrieve contextual data. The world object is an immutable thread-safe key-value store that are shared across all step definitions.
- `match`: \<[Match](https://docs.python.org/3/library/re.html#match-objects)> an instance of a Match object that holds the regular expression match result

## constructor(pattern)

- `pattern`: \<string> A regular expression text that will be used to match against gherkin steps
- returns \<None>

Instantiating an instance of class **Step** requires a single paramter named *pattern* which is a regular expression that will be used to match against gherkin steps.

# Class TaskLogger

This class is used to print text to the console. It is thread-safe and holds an internal buffer of text. It is designed to group text outputs from step definitions belonging to the same scenario, this way it will help multiple step definitions running in different threads and process writing to the console in an ordered fashion. You should always use the instance of the **TaskLogger** passed in as the parameter to your step defintion method when writing log statements. If you start using the normal built-in *print* or other log libraries to write log to console, then you will not get the benefit of the ordered and grouping of log statements.

## constructor(funcName)

- `funcName`: \<string> the name of the method used to prefix all log statements for this instance of the **TaskLogger**
- returns \<None>

You will not need to ever create a new object of class **TaskLogger**. An instance of the TaskLogger will be provided to your step definition as a parameter.

Example:

```python
@Step(pattern="login to database using master")
def loginToDatabaseStep(logger: TaskLogger, world: World, match: Match[str]):
    logger.log("login to database")
```

## log(msg)

- `msg`: \<msg> the text to print
- returns \<None>

This method will print the specified text to the console. In reality what happens is the text will be enriched with timestamp as well as the caller function's name and stored internally for later retrieval. It will be the [TaskRunner](#class-taskrunner) class that is responsible for collecting these log statements and print it to the console.

## error(msg)

- `msg`: \<msg> the text to print as an error, which will be visualized in red color.
- returns \<None>

This method will print the specified text to the console in red color. In reality what happens is the text will be enriched with timestamp as well as the caller function's name and stored internally for later retrieval. It will be the [TaskRunner](#class-taskrunner) class that is responsible for collecting these log statements and print it to the console.

# Class TaskRunner

This is the core engine of **paraworld** that is responsible for running feature files.

## constructor(debugMode=False,timeout=3600)

- `debugMode`: \<bool> if True then prints debug messages. Default is False.
- `timeout`: \<int> a timeout value ins seconds. If the elapsed time of running the feature files exceeds the timeout value then the TaskRunner will abort the execution. Default value is 3600 seconds.
- returns \<None>

Your application code will need to instantiate an instance of the TaskRunner class and call it's [run()](#runfeaturefiles) method to run one or more feature files.

Example:

```python
tr = TaskRunner(debugMode=True)
testResult = tr.run(["test.feature"])
```

## generateDependencyGraph()

- returns None

This method can be used to generate a dependency graph of the features. Call this once you have completed the run to generate a dependency graph. The result will be a file generated named *dependency_output.html* which shows the dependency graph in HTML.

Example:

*Generate dependency graph once the feature files have been run*

```python
tr = TaskRunner(debugMode=True)
tr.run(["test.feature"])

tr.generateDependencyGraph()
```

## generateReport()

- returns None

This method can be used to generate a HTML visualization of the entire run. Call this once you have completed the run to generate the HTML report. The result will be a file generated named *report_output.html* which contains all the details of the run from start to end.

Example:

*Generate HTML report once the feature files have been run*

```python
tr = TaskRunner(debugMode=True)
tr.run(["test.feature"])

tr.generateReport()
```

## generateTimeline()

- returns None

This method can be used to generate a visualization of the timeline for the feature files that have been run. Call this once you have completed the run to generate the timeline visualization. The result will be a file generated named *timeline_output.html* which contains the HTML rendering of the timeline.

Example:

*Generate timeline visualization file once the feature files have been run*

```python
tr = TaskRunner(debugMode=True)
tr.run(["test.feature"])

tr.generateTimeline()
```

## run(featureFiles)

- `featureFiles`: \<list[str]> A list of filepaths of the feature files to run.
- returns \<[TestResultInfo](#class-testresultinfo)> object

Call this method in order to run the feature files specified in argument *featureFiles*. This method will block until all the feature files have completed. The return value is an instance of class [TestResultInfo](#class-testresultinfo). You can check how long time it takes to complete all feature files by looking at the [TestResultInfo.elapsed](#class-testresultinfo) and also know whether the run has completed successfully or not by checking the [TestResultInfo.success](#class-testresultinfo) flag.

Example:

*Run two feature files and check the status of the result as well as print out the elapsed time*

```python
tr = TaskRunner(debugMode=True)
testResult = tr.run(["test.feature", "dir1/test2.feature"])

print(f"elapsed time: {testResult.elapsed}")

if testResult.success == True:
    print("Test successfull")
else:
    print("Test failed")
```

# Class TestResultInfo

An instance of this class will be returned by the [run()](#runfeaturefiles) method of class [TaskRunner](#class-taskrunner). This class is a dataclass and does not have any methods but carries various information about the test run.

## elapsed: \<int>

This field shows how much time has elapsed in seconds from start to finish of the test run.

## end: \<str>

This field shows the end time and date of when the test run has completed.

## numCpu: \<int>

This field shows how many CPU cores are present.

## pid: \<int>

This field shows the process id the test run was initiated on.

## start: \<str>

This field shows the start time and date of when the test run has been started.

## success: \<bool>

This field shows if the test run completed successfully or failed. If True then it is successfull.

# Class World

This class is responsible for keeping track of all contextual data for the entire test run. It is a thread-safe and immutable key-value dictionary that can be accessed by all step definitions across the test run. This class is implemented as a singleton class and therefore only has one copy throughout the entire application lifetime.
This class will also be synchronized across multiple process when scenarios are running in parallel in different processes.

The singleton instance will be passed as a parameter to every step definitions.

The following example shows how the world instance is being used to store the password in one step definition and retrieve the password from another step definition:

```python
@Step(pattern="login to database using master")
def loginToDatabaseStep(logger: TaskLogger, world: World, match: Match[str]):
    # use the world instance to retrieve the password under the key "password"
    password = world.getProp("password")

@Step(pattern="set master password")
def setMasterPasswordStep(logger: TaskLogger, world: World, match: Match[str]):
    # use the world instance to store value
    world.setProp("password","xasdxawdadas")
```

By using the world object you will avoid having to have global variables which are not thread-safe and prone to error. In addition any objects stored inside the world object are immutable so they cannot be changed without having to replace the object again. This is helpful to keep the integrity of the data being stored. Changing the returned object will not affect the object in store.

## getProp(key)

- `key`: \<str> gets the value stored under the specified key
- returns \<Any|None> the object or value if present otherwise None

This method can be used to retrieve any value stored under the specified *key*. If the key is not found then *None* is returned. This method is thread-safe

## setProp(key,value)

- `key`: \<str> the key where the value will be stored under
- `value`: \<Any> the value to be stored
- returns \<None>

This method can be used to store any value under the specified key. This method is thread-safe.

---

[Home](../README.md)