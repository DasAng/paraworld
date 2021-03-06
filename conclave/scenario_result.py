from typing import Any
from dataclasses import dataclass

@dataclass
class ScenarioResult:
    scenario: Any = None
    steps: Any = None
    id: str = None
    message: str = None
    elapsed: float = 0.0
    exception: str = None
    threadId: int = None
    pid: int = None
    startTime: Any = None
    endTime: Any = None