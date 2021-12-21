from dataclasses import dataclass, field

@dataclass
class FeatureInfo:
    id: str
    filePath: str
    depends: list[str] = field(default_factory=list)
