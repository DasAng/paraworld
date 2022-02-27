from dataclasses import dataclass, field

@dataclass
class TaskRunnerConfig:
    onlyRunScenarioTags: list[str] = field(default_factory=list)
    featureFiles: list[str] = field(default_factory=list)
