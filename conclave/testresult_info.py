from dataclasses import dataclass, field
from typing import Any

@dataclass
class TestResultInfo:
    elapsed: int
    start: str
    end: str
    numCpu: int
    success: bool
    pid: int
