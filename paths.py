from dataclasses import dataclass
from ezdxf.math import Vec3


@dataclass
class PlotPath:
    points: list[Vec3]
    source_type: str = ""
    layer: str = ""

    @property
    def start(self):
        return self.points[0]

    @property
    def end(self):
        return self.points[-1]