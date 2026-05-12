from dataclasses import dataclass
from typing import Literal

from csvviz.exceptions import ConflictingFlagsError


@dataclass
class BaseSpec:
    input_path: str | None
    xvar: str | None = None
    yvar: str | None = None
    colorvar: str | None = None
    facet: str | None = None
    facet_cols: int = 3
    title: str | None = None
    width_px: int | None = None
    height_px: int | None = None
    xlim: tuple[float, float] | None = None
    ylim: tuple[float, float] | None = None
    xlabel: str | None = None
    ylabel: str | None = None
    no_legend: bool = False
    theme: str = "whitegrid"
    palette: str | None = None
    colors: list[str] | None = None

    def __post_init__(self) -> None:
        if self.palette and self.colors:
            raise ConflictingFlagsError("--colors and --palette cannot both be set")
        if self.facet_cols < 1:
            raise ConflictingFlagsError("--facet-cols must be >= 1")


@dataclass
class BarSpec(BaseSpec):
    horizontal: bool = False
    stacked: bool = False
    normalized: bool = False
    sort: Literal["x", "y", "-x", "-y"] | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.normalized:
            self.stacked = True
        if self.stacked and not self.colorvar:
            raise ConflictingFlagsError("--stacked/--normalized requires -c/--colorvar")


@dataclass
class LineSpec(BaseSpec):
    pass


@dataclass
class ScatterSpec(BaseSpec):
    sizevar: str | None = None
    alpha: float | None = None


@dataclass
class HistSpec(BaseSpec):
    bins: int | None = None
    cumulative: bool = False


@dataclass
class AreaSpec(BaseSpec):
    stacked: bool = False
    normalized: bool = False

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.normalized:
            self.stacked = True
        if self.stacked and not self.colorvar:
            raise ConflictingFlagsError("--stacked/--normalized requires -c/--colorvar")


@dataclass
class HeatmapSpec(BaseSpec):
    valuevar: str | None = None
