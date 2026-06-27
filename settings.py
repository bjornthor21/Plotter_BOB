from dataclasses import dataclass

@dataclass
class Settings:
    feed: int = 1000
    textOn: bool = True
    dimensionsOn: bool = True
    borderOn: bool = True
    titleBlocksOn: bool = True

settings = Settings()