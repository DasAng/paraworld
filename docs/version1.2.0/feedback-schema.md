# Feedback schema

*`This is the documentation for Version 1.2.0`*

Feedback system is being introduced in version 1.2.0 and allows the execution flow to notify whenever a scenario or step has started and completed.

The data format that is sent to the recipient is what we call a *feedback schema*.

- [Base schema](#base-schema)
- [Scenario schema](#scenario-schema)
- [Step schema](#step-schema)

## Base schema

This schema contains information shared by multiple schemas. All schemas will inherit from the base schema.

```python
@dataclass
class BaseFeedback:
    threadId: int = None    # thread identifier
    pid: int = None         # process identifier
    startTime: str = None   # start date time
    endTime: str = None     # end date time
    elapsed: float = 0      # number of seconds took to complete the execution of the step or scenario
    type: str = None        # type of schema
```

## Scenario schema

When a scenario either starts or has completed a message will be sent to the feedback system containing the following schema:

```python
@dataclass
class ScenarioInfo:
    name: str = None                # name of scenario
    line: int = 0                   # line number this scenario is defined in gherkin file
    column: int = 0                 # column number this scenario is defined in gherkin file
    tags: list[str] = field(default_factory=list)   # all the tags for the scenario
    description: str = None         # scenario description
    numberOfSteps: int = 0          # number of steps in the scenario

@dataclass
class FeatureInfo:
    name: str = None                # name of feature
    tags: list[str] = field(default_factory=list)   # all the tags for the feature
    description: str = None         # feature description

@dataclass
class ScenarioFeedback(BaseFeedback,ScenarioInfo):
    status: FeedbackStatus = None   # status of the scenario can be one of the following: "starting", "success", "failed", "skipped"
    error: str = None               # if the scenario failed this field contains any error message
    id: str = None                  # scenario identifier
    depends: list[str] = field(default_factory=list)    # list of other scenarios this scenario depends on
    dependsGroups: list[str] = field(default_factory=list)  # the groups this scenario depends on
    runAlways: bool = False         # is the scenario marked to always run
    group: str = None               # the group this scenario belongs to
    isSetup: bool = False           # is the scenario marked to be run during setup
    isConcurrent: bool = False      # is the scenario running concurrently
    isTeardown: bool = False        # is the scenario marked to be run during teardown
    isParallel: bool = False        # is the scenario running in parallel
    type: str = "ScenarioFeedback"  # type of schema, will be set to "ScenarioFeedback". This is used internally to determine the schema type.
    featureInfo: FeatureInfo = None # Information related to the feature this scenario belongs to
```

So when a scenario starts the status of the *ScenarioFeedback* will be set to *"starting"* and when a scenario completes the status can be either "success", "failed" or "skipped".

## Step schema

When a step either starts or has completed a message will be sent to the feedback system containing the following schema:

```python
@dataclass
class ScenarioInfo:
    name: str = None                # name of scenario
    line: int = 0                   # line number this scenario is defined in gherkin file
    column: int = 0                 # column number this scenario is defined in gherkin file
    tags: list[str] = field(default_factory=list)   # all the tags for the scenario
    description: str = None         # scenario description
    numberOfSteps: int = 0          # number of steps in the scenario

@dataclass
class FeatureInfo:
    name: str = None                # name of feature
    tags: list[str] = field(default_factory=list)   # all the tags for the feature
    description: str = None         # feature description

@dataclass
class StepFeedback(BaseFeedback):
    type: str = "StepFeedback"       # type of schema, will be set to "ScenarioFeedback". This is used internally to determine the schema type. 
    status: FeedbackStatus = None   # status of the scenario can be one of the following: "starting", "success", "failed", "skipped"
    result: Any = None              # any data returned from the step implementation
    error: str = None               # if the step failed this field contains any error messag
    log: str = None                 # all the log messages bein logged by the step implementation
    line: int = 0                   # line number this step is defined in gherkin file
    column: int = 0                 # column number this step is defined in gherkin file
    keyword: str = None             # the step keyword fx: Given, When, Then, etc.
    text: str = None                # the actual step text as shown in the gherkin file
    feature: FeatureInfo = None     # Information related to the feature this step belongs to
    scenario: ScenarioInfo = None   # Information related to the scenario this step belongs to
```

So when a step starts the status of the *StepFeedback* will be set to *"starting"* and when a step completes the status can be either "success", "failed" or "skipped".