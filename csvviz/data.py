from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import pandas as pd

from csvviz.exceptions import EmptyDataError, InvalidColumnError

if TYPE_CHECKING:
    from csvviz.specs import BaseSpec


def load_csv(spec: "BaseSpec") -> pd.DataFrame:
    """Read CSV (file/stdin), resolve column defaults on the spec, validate references."""
    df = _read(spec.input_path)
    if df.shape[1] == 0 or df.shape[0] == 0:
        raise EmptyDataError("CSV has no data")
    _resolve_defaults(spec, df)
    _validate_references(spec, df)
    return df


def _read(input_path: str | None) -> pd.DataFrame:
    if input_path in (None, "-"):
        if input_path is None and sys.stdin.isatty():
            raise EmptyDataError("No input file given and stdin is a terminal (nothing to read)")
        try:
            return pd.read_csv(sys.stdin)
        except pd.errors.EmptyDataError as e:
            raise EmptyDataError("CSV has no data") from e
    try:
        return pd.read_csv(input_path)
    except pd.errors.EmptyDataError as e:
        raise EmptyDataError("CSV has no data") from e


def _resolve_defaults(spec: "BaseSpec", df: pd.DataFrame) -> None:
    from csvviz.specs import HeatmapSpec, HistSpec

    cols = list(df.columns)
    if spec.xvar is None:
        spec.xvar = cols[0]
    # Hist does not use a y column; do not resolve.
    if not isinstance(spec, HistSpec):
        if spec.yvar is None:
            if len(cols) < 2:
                raise EmptyDataError(f"chart type needs at least 2 columns; got {cols}")
            spec.yvar = cols[1]
    if isinstance(spec, HeatmapSpec) and spec.valuevar is None:
        if len(cols) < 3:
            raise EmptyDataError(f"heatmap needs at least 3 columns; got {cols}")
        spec.valuevar = cols[2]


def _validate_references(spec: "BaseSpec", df: pd.DataFrame) -> None:
    from csvviz.specs import HeatmapSpec, ScatterSpec

    cols = set(df.columns)
    refs: list[tuple[str, str | None]] = [
        ("-x/--xvar", spec.xvar),
        ("-y/--yvar", spec.yvar),
        ("-c/--colorvar", spec.colorvar),
        ("-f/--facet", spec.facet),
    ]
    if isinstance(spec, ScatterSpec):
        refs.append(("-s/--sizevar", spec.sizevar))
    if isinstance(spec, HeatmapSpec):
        refs.append(("--valuevar", spec.valuevar))

    for flag, value in refs:
        if value is None:
            continue
        if value not in cols:
            raise InvalidColumnError(
                f"{flag} references column '{value}' which is not in the CSV. "
                f"Valid columns: {sorted(cols)}"
            )
