from typing import Protocol

import pandas as pd
from matplotlib.figure import Figure

from csvviz.specs import (
    AreaSpec,
    BarSpec,
    HeatmapSpec,
    HistSpec,
    LineSpec,
    ScatterSpec,
)


class Renderer(Protocol):
    """Protocol every chart backend implements. Returns a matplotlib Figure for v0.5.

    A future non-matplotlib backend will return its own figure type; when that
    happens, promote `Figure` here to a Union or a Figure protocol.
    """

    def render_bar(self, spec: BarSpec, df: pd.DataFrame) -> Figure: ...
    def render_line(self, spec: LineSpec, df: pd.DataFrame) -> Figure: ...
    def render_scatter(self, spec: ScatterSpec, df: pd.DataFrame) -> Figure: ...
    def render_hist(self, spec: HistSpec, df: pd.DataFrame) -> Figure: ...
    def render_area(self, spec: AreaSpec, df: pd.DataFrame) -> Figure: ...
    def render_heatmap(self, spec: HeatmapSpec, df: pd.DataFrame) -> Figure: ...
