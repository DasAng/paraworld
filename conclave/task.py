from dataclasses import dataclass, field
from typing import Any
from .scenario import Scenario

@dataclass
class Task:
    name: str
    scenario: Scenario
    feature: Any
    id: str
    depends: list[str] = field(default_factory=list)
    dependsGroups: list[str] = field(default_factory=list)
    runAlways: bool = False
    group: str = None
    isSetup: bool = False
    isConcurrent: bool = False
    isTeardown: bool = False
    isParallel: bool = False
