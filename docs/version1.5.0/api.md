# API Reference

*`This is the documentation for Version 1.5.0`*

**Table of contents**

- [class AfterScenario](#class-afterscenario)
- [class BeforeScenario](#class-beforescenario)
- [class FeedbackAdapter](#class-feedbackadapter)
    - [onNotifyScenario(schema)](#onnotifyscenarioschema)
    - [onNotifyStep(schema)](#onnotifystepschema)
- [class ScenarioScope](#class-scenarioscope)
- [class Step](#class-step)
    - [constructor(pattern)](#constructorpattern)
- [class TaskLogger](#class-tasklogger)
    - [constructor(funcName)](#constructorfuncname)
    - [log(msg)](#logmsg)
    - [error(msg)](#errormsg)
- [class TaskRunner](#class-taskrunner)
    - [constructor(debugMode,timeout)](#constructordebugmodefalsetimeout3600)
    - [generateDepencyGraph()](#generatedependencygraph)
    - [generateJUnitReport()](#generatejunitreport)
    - [generateReport()](#generatereport)
    - [generateTimeline()](#generatetimeline)
    - [registerFeedbackAdapter(adapter)](#registerfeedbackadapteradapter)
    - [run(options)](#runoptions)
- [class TaskRunnerConfig](#class-taskrunnerconfig)
    - [featureFiles: list\[str\]](#featurefiles-liststr)
    - [onlyRunScenarioTags: list\[str\]](#onlyrunscenariotags-liststr)
- [class TestResultInfo](#class-testresultinfo)
    - [elapsed: int](#elapsed-int)
    - [end: str](#end-str)
    - [numCpu: int](#numcpu-int)
    - [pid: int](#pid-int)
    - [start: str](#start-str)
    - [success: bool](#success-bool)
- [class World](#class-world)
    - [getProp(key)](#getpropkey)
    - [setProp(key,value)](#setpropkeyvalue)

# Class AfterScenario

This decorator class can be used to mark a method to be executed after a scenario completes. For example if you need to have some kind of cleanup logic that needs to be done
after each scenario.

Methods that can be decorated with this class must have three parameters *logger, world, and context*. The following is how to use the decorator:

*Example*:

```python
@AfterScenario()
def after_scenario(logger: TaskLogger, world: World, context: ScenarioScope):
    logger.log(f"After scenario")
```

You can have multiple methods decorated with the AfterScenario class. Each method will be executed in turn. If any of the method throws an exception then it will stop executing the remaining
and the scenario is marked as failed.

# Class BeforeScenario

This decorator class can be used to mark a method to be executed before a scenario starts. For example if you need to have some kind of setup logic that needs to be done
befire each scenario.

Methods that can be decorated with this class must have three parameters *logger, world, and context*. The following is how to use the decorator:

*Example*:

```python
@BeforeScenario()
def before_scenario(logger: TaskLogger, world: World, context: ScenarioScope):
    logger.log(f"Before scenario")
```

You can have multiple methods decorated with the BeforeScenario class. Each method will be executed in turn. If any of the method throws an exception then it will stop executing the remaining
and the scenario is marked as failed.

# Class FeedbackAdapter

This is the base class for all implementation of a feedback adapter. When creating a feedback adapter you will need to inherit from this class. You will also need to implement the \__init__() , *onNotifyScenario()* and *onNotifyStep()* methods.

```python
class FeedbackAdapter:

    def __init__(self):
        raise NotImplementedError

    def onNotifyScenario(self,schema: ScenarioFeedback):
        raise NotImplementedError
    
    def onNotifyStep(self,schema: StepFeedback):
        raise NotImplementedError
```

## onNotifyScenario(schema)

- `schema`: [ScenarioFeedback](feedback-schema.md#scenario-schema) - An instance of the schema that contains information about the scenario
- returns \<None>

This method will be called by the feedback system to allow feedback adapters to be notified whenever a scenario starts or completes.

## onNotifyStep(schema)

- `schema`: [StepFeedback](feedback-schema.md#step-schema) - An instance of the schema that contains information about the step
- returns \<None>

This method will be called by the feedback system to allow feedback adapters to be notified whenever a step starts or completes.

# Class ScenarioScope

This class is used to retrieve and add custom data that can be accessed by all step implementations in the current scenario. Each scenario will have its own instance of the ScenarioScope.

An instance of this class will be passed as a parameter to the step implementation method. You can use this instance to set and retrieve custom data that will be available throughout the scenario.

*Example*:

```feature
Feature: Test database connectivity
    
    Scenario: connect to database successfully
        Then login to database using master
        And get database password
```

```python
@Step(pattern="login to database using master")
def loginToDatabaseStep(logger: TaskLogger, world: World, match: Match[str], context: ScenarioScope):
    context.password = "abcd"

@Step(pattern="get database password")
def loginToDatabaseStep(logger: TaskLogger, world: World, match: Match[str], context: ScenarioScope):
    logger.log(f"database password: {context.password}")

```

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
def loginToDatabaseStep(logger: TaskLogger, world: World, match: Match[str], context: ScenarioScope):
    .... implementation goes here
```

The above code shows that we have decorated our *loginToDatabaseStep* with the **Step** class and set the *pattern* paramter to a regular expression that will be used to match against gherkin steps. In addition we have refactored our *logintoDatabaseStep* method to pass in four additional parameters *logger, world, match and context*. When using the **Step** decorator your method must have the four parameters:

- `logger`: \<[TaskLogger](#class-tasklogger)> an instance of a logger that can be used to print log statement to console.
- `world`: \<[World](#class-world)> an instance of a **World** object that can be used to store and retrieve contextual data. The world object is an immutable thread-safe key-value store that are shared across all step definitions.
- `match`: \<[Match](https://docs.python.org/3/library/re.html#match-objects)> an instance of a Match object that holds the regular expression match result
- `context`: \<[ScenarioScope](#class-scenarioscope)> an instance of a ScenarioScope object that can be used to add or retrieve custom data available only in the current scenario

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
def loginToDatabaseStep(logger: TaskLogger, world: World, match: Match[str], context: ScenarioScope):
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

Your application code will need to instantiate an instance of the TaskRunner class and call it's [run()](#runoptions) method to run one or more feature files.

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

## generateJUnitReport()

- returns None

This method can be used to generate a JUNIT XML report. Call this once you have completed the run to generate the JUNIT report. The result will be a file generated named *junit_output.xml* which contains all the details of the run from start to end.

Example:

*Generate JUNIT report once the feature files have been run*

```python
tr = TaskRunner(debugMode=True)
tr.run(["test.feature"])

tr.generateJUnitReport()
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

## registerFeedbackAdapter(adapter)

- `adapter`: [FeedbackAdapter](#class-feedbackadapter) - An instance of the feedback adapter to register
- returns None

Use this method to register your own feedback adapter class. Only registered feedback adapters will be sent feedback messages.
You should register feedback adapters before calling the [run()](#runoptions) method.

## run(options)

- `options`: \<list[str]>|\<[TaskRunnerConfig](#class-taskrunnerconfig)> The options can be either a list of filepaths of the feature files to run or an instance of [TaskRunnerConfig](#class-taskrunnerconfig).
The list of filepaths can either be directories or files, if a directory is specified then all *.feature* files will be recursively included.
- returns \<[TestResultInfo](#class-testresultinfo)> object

Call this method in order to run the feature files specified in argument *featureFiles*. You can also pass in an instance of [TaskRunnerConfig](#class-taskrunnerconfig) instead, this will allow you to specify more options. This method will block until all the feature files have completed. The return value is an instance of class [TestResultInfo](#class-testresultinfo). You can check how long time it takes to complete all feature files by looking at the [TestResultInfo.elapsed](#class-testresultinfo) and also know whether the run has completed successfully or not by checking the [TestResultInfo.success](#class-testresultinfo) flag.

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

Example 2:

*Pass in TaskRunnerConfig specifying two feature files to run as well as only run scenarios with the specified tags*

```python
tr = TaskRunner(debugMode=True)
testResult = tr.run(
    TaskRunnerConfig(
        featureFiles=["test.feature", "dir1/test2.feature"],
        onlyRunScenarioTags=["@scenarioX","@scenarioY"]
    )
)

print(f"elapsed time: {testResult.elapsed}")

if testResult.success == True:
    print("Test successfull")
else:
    print("Test failed")
```

Example 3:

*Specify a directory to recursively get all feature files as well as specifying specific feature files to run*

```python
tr = TaskRunner(debugMode=True)
testResult = tr.run(
    TaskRunnerConfig(
        featureFiles=["test.feature", "dir1"]
    )
)

print(f"elapsed time: {testResult.elapsed}")

if testResult.success == True:
    print("Test successfull")
else:
    print("Test failed")
```

# Class TaskRunnerConfig

You can pass an instance of this class to the [run()](#runoptions) method of class [TaskRunner](#class-taskrunner).

## featureFiles: list[str]

This field contains the list of feature files to run. These can be absolute or relative path to the feature files.
The list of filepaths can either be directories or files, if a directory is specified then all *.feature* files will be recursively included.

## onlyRunScenarioTags: list[str]

This optional field can contain a list of scenario tags that indicates only those scenarios that contains these tags should be included to run.

# Class TestResultInfo

An instance of this class will be returned by the [run()](#runoptions) method of class [TaskRunner](#class-taskrunner). This class is a dataclass and does not have any methods but carries various information about the test run.

## elapsed: int

This field shows how much time has elapsed in seconds from start to finish of the test run.

## end: str

This field shows the end time and date of when the test run has completed.

## numCpu: int

This field shows how many CPU cores are present.

## pid: int

This field shows the process id the test run was initiated on.

## start: str

This field shows the start time and date of when the test run has been started.

## success: bool

This field shows if the test run completed successfully or failed. If True then it is successfull.

# Class World

This class is responsible for keeping track of all contextual data for the entire test run. It is a thread-safe and immutable key-value dictionary that can be accessed by all step definitions across the test run. This class is implemented as a singleton class and therefore only has one copy throughout the entire application lifetime.
This class will also be synchronized across multiple process when scenarios are running in parallel in different processes.

The singleton instance will be passed as a parameter to every step definitions.

The following example shows how the world instance is being used to store the password in one step definition and retrieve the password from another step definition:

```python
@Step(pattern="login to database using master")
def loginToDatabaseStep(logger: TaskLogger, world: World, match: Match[str], context: ScenarioScope):
    # use the world instance to retrieve the password under the key "password"
    password = world.getProp("password")

@Step(pattern="set master password")
def setMasterPasswordStep(logger: TaskLogger, world: World, match: Match[str], context: ScenarioScope):
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

[Home](../../README.md)