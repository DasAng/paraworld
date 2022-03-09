from dataclasses import dataclass
from typing import Any

@dataclass
class StepResult:
    elapsed: float
    result: Any
    error: str
    threadId: int
    pid: int
    start: Any
    end: Any
    log: str