from dataclasses import dataclass, field
from typing import Any

from .step_result import StepResult

@dataclass
class BaseFeedback:
    threadId: int = None
    pid: int = None
    startTime: str = None
    endTime: str = None
    elapsed: float = 0
    type: str = None

class FeedbackStatus:
    STARTING = 'starting'
    SUCCESS = 'success'
    SKIPPED = 'skipped'
    FAILED = 'failed'

@dataclass
class ScenarioInfo:
    name: str = None
    line: int = 0
    column: int = 0
    tags: list[str] = field(default_factory=list)
    description: str = None
    numberOfSteps: int = 0

@dataclass
class FeatureInfo:
    name: str = None
    tags: list[str] = field(default_factory=list)
    description: str = None

@dataclass
class ScenarioFeedback(BaseFeedback,ScenarioInfo):
    status: FeedbackStatus = None
    error: str = None
    id: str = None
    depends: list[str] = field(default_factory=list)
    dependsGroups: list[str] = field(default_factory=list)
    runAlways: bool = False
    group: str = None
    isSetup: bool = False
    isConcurrent: bool = False
    isTeardown: bool = False
    isParallel: bool = False
    type: str = "ScenarioFeedback"
    featureInfo: FeatureInfo = None

@dataclass
class StepFeedback(BaseFeedback):
    type: str = "StepFeedback"
    status: FeedbackStatus = None
    result: Any = None
    error: str = None
    log: str = None
    line: int = 0
    column: int = 0
    keyword: str = None
    text: str = None
    feature: FeatureInfo = None
    scenario: ScenarioInfo = None

