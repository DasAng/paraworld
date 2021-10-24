from dataclasses import dataclass
from typing import Callable

@dataclass
class StepDefinition:
    pattern: str
    func: Callable