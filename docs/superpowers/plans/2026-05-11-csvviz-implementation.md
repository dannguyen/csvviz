# csvviz 0.5 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build csvviz 0.5, a CLI that turns a CSV into a chart in one command (`csvviz bar foo.csv`), using matplotlib + pandas + seaborn under a backend-swappable architecture.

**Architecture:** Five modules with one-way dependencies: `cli.py` → `specs.py` (dataclasses) → `data.py` (CSV loading) → `renderers/matplotlib_renderer.py` (Figure construction) → `output.py` (show/save). A `Renderer` protocol isolates the drawing layer so a future backend is a new file, not a rewrite.

**Tech Stack:** Python 3.10+, Click 8.1+, pandas 2.0+, matplotlib 3.7+, seaborn 0.13+, pytest 8+, black 24+.

**Spec:** `docs/superpowers/specs/2026-05-11-csvviz-design.md`

---

## File map

**Source (`csvviz/`):**
- `__init__.py` — `__version__`
- `exceptions.py` — `CsvvizError` hierarchy
- `specs.py` — `BaseSpec` + 6 per-chart-type dataclasses
- `data.py` — `load_csv(spec) -> DataFrame`
- `output.py` — `deliver(figure, ...)`, display detection
- `renderers/__init__.py`
- `renderers/base.py` — `Renderer` Protocol
- `renderers/matplotlib_renderer.py` — `MatplotlibRenderer` with 6 `render_*` methods
- `cli.py` — Click group + 6 subcommands + error wrapping

**Tests (`tests/`):**
- `conftest.py` — sets `matplotlib.use("Agg")` at session start
- `fixtures/tings.csv`, `fixtures/stocks.csv`, `fixtures/hot.csv` — copied from `old-csvviz/examples/`
- `test_exceptions.py`, `test_specs.py`, `test_data.py`, `test_output.py`
- `test_renderer_matplotlib.py`
- `test_cli.py`

**Project root:**
- `pyproject.toml`, `pytest.ini`, `.gitignore`, `README.md`
- `examples/` — `tings.csv`, `stocks.csv`, `hot.csv`, `cars.csv` copied from `old-csvviz/examples/`

---

## Task 1: Project scaffold

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `pytest.ini`
- Create: `csvviz/__init__.py`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`

- [ ] **Step 1: Initialize git repo (project is not a git repo yet)**

Run:
```bash
cd /Users/dan/LOCALSTAGE/csvviz-project
git init
```

- [ ] **Step 2: Create `.gitignore`**

Write `/Users/dan/LOCALSTAGE/csvviz-project/.gitignore`:
```
__pycache__/
*.py[cod]
*.egg-info/
.pytest_cache/
.venv/
build/
dist/
*.png
*.svg
*.pdf
!tests/fixtures/*
!examples/*
.DS_Store
```

- [ ] **Step 3: Create `pyproject.toml`**

Write `/Users/dan/LOCALSTAGE/csvviz-project/pyproject.toml`:
```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "csvviz"
version = "0.5.0"
description = "Create visualizations from CSV files on the command line"
readme = "README.md"
license = { text = "MIT" }
authors = [{ name = "Dan Nguyen", email = "dansonguyen@gmail.com" }]
requires-python = ">=3.10"
dependencies = [
    "click>=8.1",
    "pandas>=2.0",
    "matplotlib>=3.7",
    "seaborn>=0.13",
]

[project.optional-dependencies]
dev = [
    "pytest>=8",
    "black>=24",
]

[project.scripts]
csvviz = "csvviz.cli:cli"

[tool.setuptools.packages.find]
include = ["csvviz*"]
exclude = ["old-csvviz*", "tests*", "examples*"]

[tool.black]
line-length = 100
target-version = ["py310"]
```

- [ ] **Step 4: Create `pytest.ini`**

Write `/Users/dan/LOCALSTAGE/csvviz-project/pytest.ini`:
```ini
[pytest]
testpaths = tests
python_files = test_*.py
addopts = -ra
```

- [ ] **Step 5: Create `csvviz/__init__.py`**

Write `/Users/dan/LOCALSTAGE/csvviz-project/csvviz/__init__.py`:
```python
__version__ = "0.5.0"
```

- [ ] **Step 6: Create `tests/__init__.py` and `tests/conftest.py`**

Write `/Users/dan/LOCALSTAGE/csvviz-project/tests/__init__.py` (empty file):
```python
```

Write `/Users/dan/LOCALSTAGE/csvviz-project/tests/conftest.py`:
```python
import matplotlib

matplotlib.use("Agg")
```

- [ ] **Step 7: Create virtualenv and install in editable mode with dev deps**

Run:
```bash
cd /Users/dan/LOCALSTAGE/csvviz-project
python3 -m venv .venv
.venv/bin/pip install -U pip
.venv/bin/pip install -e ".[dev]"
```

Expected: pip installs click, pandas, matplotlib, seaborn, pytest, black, and the `csvviz` package itself in editable mode.

- [ ] **Step 8: Sanity check — version import works**

Run:
```bash
.venv/bin/python -c "import csvviz; print(csvviz.__version__)"
```

Expected output: `0.5.0`

- [ ] **Step 9: Commit**

```bash
git add .gitignore pyproject.toml pytest.ini csvviz/__init__.py tests/__init__.py tests/conftest.py
git commit -m "scaffold project: pyproject.toml, pytest config, version"
```

---

## Task 2: Exceptions module

**Files:**
- Create: `csvviz/exceptions.py`
- Create: `tests/test_exceptions.py`

- [ ] **Step 1: Write the failing test**

Write `/Users/dan/LOCALSTAGE/csvviz-project/tests/test_exceptions.py`:
```python
import pytest

from csvviz.exceptions import (
    CsvvizError,
    InvalidColumnError,
    ConflictingFlagsError,
    EmptyDataError,
    OutputError,
)


def test_all_errors_subclass_csvviz_error():
    for cls in (
        InvalidColumnError,
        ConflictingFlagsError,
        EmptyDataError,
        OutputError,
    ):
        assert issubclass(cls, CsvvizError)


def test_csvviz_error_is_exception():
    assert issubclass(CsvvizError, Exception)


def test_invalid_column_error_carries_message():
    err = InvalidColumnError("column 'foo' not found")
    assert "foo" in str(err)
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
.venv/bin/pytest tests/test_exceptions.py -v
```

Expected: ImportError (csvviz.exceptions does not exist yet).

- [ ] **Step 3: Implement the exceptions module**

Write `/Users/dan/LOCALSTAGE/csvviz-project/csvviz/exceptions.py`:
```python
class CsvvizError(Exception):
    """Base class for all csvviz user-facing errors."""


class InvalidColumnError(CsvvizError):
    """A referenced column is not in the CSV."""


class ConflictingFlagsError(CsvvizError):
    """Flags combine in a way that doesn't make sense."""


class EmptyDataError(CsvvizError):
    """The input CSV is empty or has too few columns for the chart type."""


class OutputError(CsvvizError):
    """The output path or format is invalid."""
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
.venv/bin/pytest tests/test_exceptions.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Format and commit**

```bash
.venv/bin/black csvviz tests
git add csvviz/exceptions.py tests/test_exceptions.py
git commit -m "add CsvvizError hierarchy"
```

---

## Task 3: Spec dataclasses

**Files:**
- Create: `csvviz/specs.py`
- Create: `tests/test_specs.py`

- [ ] **Step 1: Write failing tests for BaseSpec defaults and per-type specs**

Write `/Users/dan/LOCALSTAGE/csvviz-project/tests/test_specs.py`:
```python
import pytest

from csvviz.exceptions import ConflictingFlagsError
from csvviz.specs import (
    AreaSpec,
    BarSpec,
    BaseSpec,
    HeatmapSpec,
    HistSpec,
    LineSpec,
    ScatterSpec,
)


def test_basespec_defaults():
    spec = BaseSpec(input_path="foo.csv")
    assert spec.input_path == "foo.csv"
    assert spec.xvar is None
    assert spec.yvar is None
    assert spec.colorvar is None
    assert spec.facet is None
    assert spec.facet_cols == 3
    assert spec.theme == "whitegrid"
    assert spec.no_legend is False


def test_barspec_normalized_implies_stacked():
    spec = BarSpec(input_path="f.csv", colorvar="c", normalized=True)
    assert spec.stacked is True


def test_barspec_stacked_without_colorvar_raises():
    with pytest.raises(ConflictingFlagsError):
        BarSpec(input_path="f.csv", stacked=True)


def test_barspec_normalized_without_colorvar_raises():
    with pytest.raises(ConflictingFlagsError):
        BarSpec(input_path="f.csv", normalized=True)


def test_areaspec_normalized_implies_stacked():
    spec = AreaSpec(input_path="f.csv", colorvar="c", normalized=True)
    assert spec.stacked is True


def test_areaspec_stacked_without_colorvar_raises():
    with pytest.raises(ConflictingFlagsError):
        AreaSpec(input_path="f.csv", stacked=True)


def test_colors_and_palette_conflict():
    with pytest.raises(ConflictingFlagsError):
        BarSpec(input_path="f.csv", palette="viridis", colors=["red", "blue"])


def test_facet_cols_must_be_positive():
    with pytest.raises(ConflictingFlagsError):
        BarSpec(input_path="f.csv", facet_cols=0)


def test_linespec_has_no_extra_fields():
    spec = LineSpec(input_path="f.csv")
    assert hasattr(spec, "xvar")
    # LineSpec adds nothing; the dataclass exists for type discrimination


def test_scatterspec_has_sizevar_and_alpha():
    spec = ScatterSpec(input_path="f.csv", sizevar="cyl", alpha=0.5)
    assert spec.sizevar == "cyl"
    assert spec.alpha == 0.5


def test_histspec_has_bins_and_cumulative():
    spec = HistSpec(input_path="f.csv", bins=20, cumulative=True)
    assert spec.bins == 20
    assert spec.cumulative is True


def test_heatmapspec_has_valuevar():
    spec = HeatmapSpec(input_path="f.csv", valuevar="sold")
    assert spec.valuevar == "sold"
```

- [ ] **Step 2: Run tests to verify they fail**

Run:
```bash
.venv/bin/pytest tests/test_specs.py -v
```

Expected: ImportError (csvviz.specs does not exist).

- [ ] **Step 3: Implement `csvviz/specs.py`**

Write `/Users/dan/LOCALSTAGE/csvviz-project/csvviz/specs.py`:
```python
from dataclasses import dataclass, field
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
            raise ConflictingFlagsError(
                "--colors and --palette cannot both be set"
            )
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
            raise ConflictingFlagsError(
                "--stacked/--normalized requires -c/--colorvar"
            )


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
            raise ConflictingFlagsError(
                "--stacked/--normalized requires -c/--colorvar"
            )


@dataclass
class HeatmapSpec(BaseSpec):
    valuevar: str | None = None
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
.venv/bin/pytest tests/test_specs.py -v
```

Expected: 11 passed.

- [ ] **Step 5: Format and commit**

```bash
.venv/bin/black csvviz tests
git add csvviz/specs.py tests/test_specs.py
git commit -m "add Spec dataclasses with validation"
```

---

## Task 4: Test fixtures

**Files:**
- Create: `tests/fixtures/tings.csv`
- Create: `tests/fixtures/stocks.csv`
- Create: `tests/fixtures/hot.csv`

- [ ] **Step 1: Copy fixtures from old-csvviz/examples**

Run:
```bash
mkdir -p tests/fixtures
cp old-csvviz/examples/tings.csv tests/fixtures/tings.csv
cp old-csvviz/examples/stocks.csv tests/fixtures/stocks.csv
cp old-csvviz/examples/hot.csv tests/fixtures/hot.csv
```

- [ ] **Step 2: Verify fixtures exist and have expected headers**

Run:
```bash
head -1 tests/fixtures/tings.csv
head -1 tests/fixtures/stocks.csv
head -1 tests/fixtures/hot.csv
```

Expected output:
```
name,amount
company,date,price
state,item,sold
```

- [ ] **Step 3: Commit**

```bash
git add tests/fixtures/
git commit -m "add test fixtures (tings, stocks, hot)"
```

---

## Task 5: Data loading — file input, defaults, validation

**Files:**
- Create: `csvviz/data.py`
- Create: `tests/test_data.py`

- [ ] **Step 1: Write failing tests for `load_csv`**

Write `/Users/dan/LOCALSTAGE/csvviz-project/tests/test_data.py`:
```python
import io
from pathlib import Path

import pandas as pd
import pytest

from csvviz.data import load_csv
from csvviz.exceptions import EmptyDataError, InvalidColumnError
from csvviz.specs import BarSpec, HeatmapSpec, HistSpec, LineSpec

FIXTURES = Path(__file__).parent / "fixtures"


def test_load_csv_from_file():
    spec = BarSpec(input_path=str(FIXTURES / "tings.csv"))
    df = load_csv(spec)
    assert list(df.columns) == ["name", "amount"]
    assert len(df) == 5


def test_xvar_defaults_to_first_column():
    spec = BarSpec(input_path=str(FIXTURES / "tings.csv"))
    load_csv(spec)
    assert spec.xvar == "name"


def test_yvar_defaults_to_second_column():
    spec = BarSpec(input_path=str(FIXTURES / "tings.csv"))
    load_csv(spec)
    assert spec.yvar == "amount"


def test_explicit_xvar_not_overridden():
    spec = LineSpec(input_path=str(FIXTURES / "stocks.csv"), xvar="date")
    load_csv(spec)
    assert spec.xvar == "date"


def test_heatmap_valuevar_defaults_to_third_column():
    spec = HeatmapSpec(input_path=str(FIXTURES / "hot.csv"))
    load_csv(spec)
    assert spec.xvar == "state"
    assert spec.yvar == "item"
    assert spec.valuevar == "sold"


def test_hist_does_not_resolve_yvar():
    spec = HistSpec(input_path=str(FIXTURES / "tings.csv"))
    load_csv(spec)
    assert spec.xvar == "name"
    assert spec.yvar is None


def test_invalid_xvar_raises():
    spec = BarSpec(input_path=str(FIXTURES / "tings.csv"), xvar="nope")
    with pytest.raises(InvalidColumnError) as exc:
        load_csv(spec)
    assert "nope" in str(exc.value)
    assert "name" in str(exc.value)  # lists valid columns


def test_invalid_colorvar_raises():
    spec = BarSpec(input_path=str(FIXTURES / "tings.csv"), colorvar="bogus")
    with pytest.raises(InvalidColumnError):
        load_csv(spec)


def test_empty_csv_raises(tmp_path):
    p = tmp_path / "empty.csv"
    p.write_text("")
    spec = BarSpec(input_path=str(p))
    with pytest.raises(EmptyDataError):
        load_csv(spec)


def test_single_column_csv_raises_for_bar(tmp_path):
    p = tmp_path / "one.csv"
    p.write_text("only\n1\n2\n")
    spec = BarSpec(input_path=str(p))
    with pytest.raises(EmptyDataError):
        load_csv(spec)
```

- [ ] **Step 2: Run tests to verify they fail**

Run:
```bash
.venv/bin/pytest tests/test_data.py -v
```

Expected: ImportError on `csvviz.data`.

- [ ] **Step 3: Implement `csvviz/data.py` (file input only — stdin in Task 6)**

Write `/Users/dan/LOCALSTAGE/csvviz-project/csvviz/data.py`:
```python
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
            raise EmptyDataError(
                "No input file given and stdin is a terminal (nothing to read)"
            )
        return pd.read_csv(sys.stdin)
    return pd.read_csv(input_path)


def _resolve_defaults(spec: "BaseSpec", df: pd.DataFrame) -> None:
    from csvviz.specs import HeatmapSpec, HistSpec

    cols = list(df.columns)
    if spec.xvar is None:
        spec.xvar = cols[0]
    # Hist does not use a y column; do not resolve.
    if not isinstance(spec, HistSpec):
        if spec.yvar is None:
            if len(cols) < 2:
                raise EmptyDataError(
                    f"chart type needs at least 2 columns; got {cols}"
                )
            spec.yvar = cols[1]
    if isinstance(spec, HeatmapSpec) and spec.valuevar is None:
        if len(cols) < 3:
            raise EmptyDataError(
                f"heatmap needs at least 3 columns; got {cols}"
            )
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
.venv/bin/pytest tests/test_data.py -v
```

Expected: 10 passed.

- [ ] **Step 5: Format and commit**

```bash
.venv/bin/black csvviz tests
git add csvviz/data.py tests/test_data.py
git commit -m "add load_csv with column resolution and validation"
```

---

## Task 6: Output layer — display detection and `deliver`

**Files:**
- Create: `csvviz/output.py`
- Create: `tests/test_output.py`

- [ ] **Step 1: Write failing tests**

Write `/Users/dan/LOCALSTAGE/csvviz-project/tests/test_output.py`:
```python
from pathlib import Path
from unittest.mock import patch

import matplotlib
import matplotlib.pyplot as plt
import pytest

from csvviz.exceptions import OutputError
from csvviz.output import deliver, has_display, fallback_path


def _make_figure():
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [4, 5, 6])
    return fig


def test_has_display_linux_with_display():
    with patch("csvviz.output.sys.platform", "linux"):
        with patch.dict("os.environ", {"DISPLAY": ":0"}, clear=True):
            assert has_display() is True


def test_has_display_linux_without_display():
    with patch("csvviz.output.sys.platform", "linux"):
        with patch.dict("os.environ", {}, clear=True):
            assert has_display() is False


def test_has_display_linux_with_wayland():
    with patch("csvviz.output.sys.platform", "linux"):
        with patch.dict("os.environ", {"WAYLAND_DISPLAY": "wayland-0"}, clear=True):
            assert has_display() is True


def test_has_display_macos_local():
    with patch("csvviz.output.sys.platform", "darwin"):
        with patch.dict("os.environ", {}, clear=True):
            assert has_display() is True


def test_has_display_macos_ssh():
    with patch("csvviz.output.sys.platform", "darwin"):
        with patch.dict("os.environ", {"SSH_CONNECTION": "1.2.3.4"}, clear=True):
            assert has_display() is False


def test_has_display_windows():
    with patch("csvviz.output.sys.platform", "win32"):
        with patch.dict("os.environ", {}, clear=True):
            assert has_display() is True


def test_fallback_path_uses_csv_stem():
    p = fallback_path("data/sales.csv", "bar")
    assert p.name == "sales-bar.png"


def test_fallback_path_for_stdin():
    p = fallback_path(None, "hist")
    assert p.name == "stdin-hist.png"


def test_deliver_saves_to_output_path(tmp_path):
    fig = _make_figure()
    out = tmp_path / "chart.png"
    deliver(fig, chart_type="bar", input_path="x.csv", output=out, no_show=False, dpi=100)
    assert out.exists()
    assert out.stat().st_size > 0


def test_deliver_unknown_extension_raises(tmp_path):
    fig = _make_figure()
    out = tmp_path / "chart.xyz"
    with pytest.raises(OutputError):
        deliver(fig, chart_type="bar", input_path="x.csv", output=out, no_show=False, dpi=100)


def test_deliver_no_show_writes_fallback(tmp_path, monkeypatch):
    fig = _make_figure()
    monkeypatch.chdir(tmp_path)
    deliver(fig, chart_type="bar", input_path="data.csv", output=None, no_show=True, dpi=100)
    assert (tmp_path / "data-bar.png").exists()


def test_deliver_headless_writes_fallback(tmp_path, monkeypatch):
    fig = _make_figure()
    monkeypatch.chdir(tmp_path)
    with patch("csvviz.output.has_display", return_value=False):
        deliver(fig, chart_type="bar", input_path="data.csv", output=None, no_show=False, dpi=100)
    assert (tmp_path / "data-bar.png").exists()
```

- [ ] **Step 2: Run tests to verify they fail**

Run:
```bash
.venv/bin/pytest tests/test_output.py -v
```

Expected: ImportError on `csvviz.output`.

- [ ] **Step 3: Implement `csvviz/output.py`**

Write `/Users/dan/LOCALSTAGE/csvviz-project/csvviz/output.py`:
```python
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from csvviz.exceptions import OutputError

if TYPE_CHECKING:
    from matplotlib.figure import Figure

VALID_EXTENSIONS = {".png", ".svg", ".pdf"}


def has_display() -> bool:
    """Best-effort detection of a graphical display."""
    if sys.platform.startswith("linux"):
        return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))
    if sys.platform == "darwin":
        # macOS GUI doesn't use DISPLAY; SSH session means no GUI.
        return not os.environ.get("SSH_CONNECTION")
    if sys.platform.startswith("win"):
        return True
    return False


def fallback_path(input_path: str | None, chart_type: str) -> Path:
    stem = Path(input_path).stem if input_path else "stdin"
    return Path.cwd() / f"{stem}-{chart_type}.png"


def deliver(
    figure: "Figure",
    *,
    chart_type: str,
    input_path: str | None,
    output: Path | None,
    no_show: bool,
    dpi: int,
) -> None:
    """Show the figure or save it to disk per the §2 decision table."""
    if output is not None:
        _save(figure, output, dpi)
        print(f"wrote {output}", file=sys.stderr)
        return

    if no_show:
        path = fallback_path(input_path, chart_type)
        _save(figure, path, dpi)
        print(f"wrote {path}", file=sys.stderr)
        return

    if has_display():
        import matplotlib.pyplot as plt
        plt.show()
        return

    path = fallback_path(input_path, chart_type)
    _save(figure, path, dpi)
    print(f"wrote {path} (no display detected)", file=sys.stderr)


def _save(figure: "Figure", path: Path, dpi: int) -> None:
    ext = path.suffix.lower()
    if ext not in VALID_EXTENSIONS:
        raise OutputError(
            f"output extension '{ext}' not supported; use one of {sorted(VALID_EXTENSIONS)}"
        )
    figure.savefig(path, dpi=dpi, bbox_inches="tight")
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
.venv/bin/pytest tests/test_output.py -v
```

Expected: 12 passed.

- [ ] **Step 5: Format and commit**

```bash
.venv/bin/black csvviz tests
git add csvviz/output.py tests/test_output.py
git commit -m "add output layer: display detection, deliver, fallback paths"
```

---

## Task 7: Renderer protocol

**Files:**
- Create: `csvviz/renderers/__init__.py`
- Create: `csvviz/renderers/base.py`

- [ ] **Step 1: Create the renderers package**

Write `/Users/dan/LOCALSTAGE/csvviz-project/csvviz/renderers/__init__.py` (empty file):
```python
```

- [ ] **Step 2: Define the protocol**

Write `/Users/dan/LOCALSTAGE/csvviz-project/csvviz/renderers/base.py`:
```python
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
```

- [ ] **Step 3: Sanity check the import**

Run:
```bash
.venv/bin/python -c "from csvviz.renderers.base import Renderer; print(Renderer)"
```

Expected: prints `<class 'csvviz.renderers.base.Renderer'>` (no errors).

- [ ] **Step 4: Commit**

```bash
.venv/bin/black csvviz
git add csvviz/renderers/__init__.py csvviz/renderers/base.py
git commit -m "add Renderer protocol"
```

---

## Task 8: MatplotlibRenderer — bar chart (basic + variants)

**Files:**
- Create: `csvviz/renderers/matplotlib_renderer.py`
- Create: `tests/test_renderer_matplotlib.py`

- [ ] **Step 1: Write failing tests for bar rendering**

Write `/Users/dan/LOCALSTAGE/csvviz-project/tests/test_renderer_matplotlib.py`:
```python
from pathlib import Path

import pandas as pd
import pytest
from matplotlib.figure import Figure

from csvviz.data import load_csv
from csvviz.renderers.matplotlib_renderer import MatplotlibRenderer
from csvviz.specs import BarSpec

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def renderer():
    return MatplotlibRenderer()


def _load(spec):
    df = load_csv(spec)
    return df


def test_render_bar_returns_figure(renderer):
    spec = BarSpec(input_path=str(FIXTURES / "tings.csv"))
    df = _load(spec)
    fig = renderer.render_bar(spec, df)
    assert isinstance(fig, Figure)
    assert len(fig.axes) == 1


def test_render_bar_with_title(renderer):
    spec = BarSpec(input_path=str(FIXTURES / "tings.csv"), title="My Chart")
    df = _load(spec)
    fig = renderer.render_bar(spec, df)
    assert fig.axes[0].get_title() == "My Chart"


def test_render_bar_horizontal(renderer):
    spec = BarSpec(input_path=str(FIXTURES / "tings.csv"), horizontal=True)
    df = _load(spec)
    fig = renderer.render_bar(spec, df)
    # Horizontal: y-axis shows the categorical names
    assert isinstance(fig, Figure)


def test_render_bar_with_dimensions(renderer):
    spec = BarSpec(
        input_path=str(FIXTURES / "tings.csv"), width_px=800, height_px=400
    )
    df = _load(spec)
    fig = renderer.render_bar(spec, df)
    # default dpi 100 → 8x4 inches
    w, h = fig.get_size_inches()
    assert abs(w - 8.0) < 0.01
    assert abs(h - 4.0) < 0.01


def test_render_bar_stacked_requires_colorvar_in_data(renderer, tmp_path):
    # Build a CSV with a category column for stacking
    p = tmp_path / "stack.csv"
    p.write_text(
        "month,product,sales\n"
        "Jan,A,10\n"
        "Jan,B,20\n"
        "Feb,A,15\n"
        "Feb,B,25\n"
    )
    spec = BarSpec(
        input_path=str(p), xvar="month", yvar="sales", colorvar="product", stacked=True
    )
    df = _load(spec)
    fig = renderer.render_bar(spec, df)
    assert isinstance(fig, Figure)
```

- [ ] **Step 2: Run tests to verify they fail**

Run:
```bash
.venv/bin/pytest tests/test_renderer_matplotlib.py -v
```

Expected: ImportError on `csvviz.renderers.matplotlib_renderer`.

- [ ] **Step 3: Implement `MatplotlibRenderer` with bar support**

Write `/Users/dan/LOCALSTAGE/csvviz-project/csvviz/renderers/matplotlib_renderer.py`:
```python
from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure

from csvviz.specs import (
    AreaSpec,
    BarSpec,
    BaseSpec,
    HeatmapSpec,
    HistSpec,
    LineSpec,
    ScatterSpec,
)

DEFAULT_WIDTH_PX = 800
DEFAULT_HEIGHT_PX = 500
DEFAULT_DPI = 100


class MatplotlibRenderer:
    """Renders charts using matplotlib + seaborn. Returns matplotlib.figure.Figure."""

    def render_bar(self, spec: BarSpec, df: pd.DataFrame) -> Figure:
        self._apply_theme(spec)
        fig, ax = self._new_figure(spec)

        x, y = (spec.yvar, spec.xvar) if spec.horizontal else (spec.xvar, spec.yvar)

        if spec.stacked:
            self._draw_stacked_bar(ax, df, spec)
        elif spec.colorvar:
            sns.barplot(
                data=df,
                x=x,
                y=y,
                hue=spec.colorvar,
                ax=ax,
                palette=spec.palette,
                orient="h" if spec.horizontal else "v",
            )
        else:
            sns.barplot(
                data=df,
                x=x,
                y=y,
                ax=ax,
                color=(spec.colors[0] if spec.colors else None),
                orient="h" if spec.horizontal else "v",
            )

        if spec.sort:
            self._apply_bar_sort(ax, spec)

        self._finalize(fig, ax, spec)
        return fig

    def render_line(self, spec: LineSpec, df: pd.DataFrame) -> Figure:
        raise NotImplementedError

    def render_scatter(self, spec: ScatterSpec, df: pd.DataFrame) -> Figure:
        raise NotImplementedError

    def render_hist(self, spec: HistSpec, df: pd.DataFrame) -> Figure:
        raise NotImplementedError

    def render_area(self, spec: AreaSpec, df: pd.DataFrame) -> Figure:
        raise NotImplementedError

    def render_heatmap(self, spec: HeatmapSpec, df: pd.DataFrame) -> Figure:
        raise NotImplementedError

    # --- helpers ---

    def _apply_theme(self, spec: BaseSpec) -> None:
        sns.set_theme(style=spec.theme, palette=spec.palette or "tab10")
        if spec.colors:
            # Override the active color cycle with explicit colors.
            sns.set_palette(spec.colors)

    def _new_figure(self, spec: BaseSpec):
        w_px = spec.width_px or DEFAULT_WIDTH_PX
        h_px = spec.height_px or DEFAULT_HEIGHT_PX
        fig, ax = plt.subplots(figsize=(w_px / DEFAULT_DPI, h_px / DEFAULT_DPI))
        return fig, ax

    def _finalize(self, fig: Figure, ax, spec: BaseSpec) -> None:
        if spec.title:
            ax.set_title(spec.title)
        if spec.xlabel:
            ax.set_xlabel(spec.xlabel)
        if spec.ylabel:
            ax.set_ylabel(spec.ylabel)
        if spec.xlim:
            ax.set_xlim(spec.xlim)
        if spec.ylim:
            ax.set_ylim(spec.ylim)
        if spec.no_legend and ax.get_legend() is not None:
            ax.get_legend().remove()
        fig.tight_layout()

    def _draw_stacked_bar(self, ax, df: pd.DataFrame, spec: BarSpec) -> None:
        pivot = df.pivot_table(
            index=spec.xvar, columns=spec.colorvar, values=spec.yvar, aggfunc="sum"
        ).fillna(0)
        if spec.normalized:
            pivot = pivot.div(pivot.sum(axis=1), axis=0) * 100.0
        kind = "barh" if spec.horizontal else "bar"
        pivot.plot(kind=kind, stacked=True, ax=ax, color=spec.colors)

    def _apply_bar_sort(self, ax, spec: BarSpec) -> None:
        # Sort affects the categorical axis ordering. For seaborn barplot output,
        # we sort the tick labels by the value of the other axis.
        reverse = spec.sort.startswith("-")
        key = spec.sort.lstrip("-")
        if key not in ("x", "y"):
            return
        # Gather (label, value) pairs from the patches.
        labels = [t.get_text() for t in ax.get_xticklabels()]
        heights = [p.get_height() for p in ax.patches[: len(labels)]]
        order = sorted(
            range(len(labels)),
            key=lambda i: heights[i],
            reverse=reverse if key == "y" else not reverse,
        )
        ax.set_xticks(range(len(order)))
        ax.set_xticklabels([labels[i] for i in order])
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
.venv/bin/pytest tests/test_renderer_matplotlib.py -v
```

Expected: 5 passed.

- [ ] **Step 5: Format and commit**

```bash
.venv/bin/black csvviz tests
git add csvviz/renderers/matplotlib_renderer.py tests/test_renderer_matplotlib.py
git commit -m "implement MatplotlibRenderer.render_bar"
```

---

## Task 9: MatplotlibRenderer — line and scatter

**Files:**
- Modify: `csvviz/renderers/matplotlib_renderer.py`
- Modify: `tests/test_renderer_matplotlib.py`

- [ ] **Step 1: Append failing tests for line and scatter**

Append to `/Users/dan/LOCALSTAGE/csvviz-project/tests/test_renderer_matplotlib.py`:
```python
from csvviz.specs import LineSpec, ScatterSpec


def test_render_line_single_series(renderer):
    spec = LineSpec(input_path=str(FIXTURES / "stocks.csv"), xvar="date", yvar="price")
    df = _load(spec)
    fig = renderer.render_line(spec, df)
    assert isinstance(fig, Figure)
    assert len(fig.axes[0].get_lines()) >= 1


def test_render_line_multi_series_via_colorvar(renderer):
    spec = LineSpec(
        input_path=str(FIXTURES / "stocks.csv"),
        xvar="date",
        yvar="price",
        colorvar="company",
    )
    df = _load(spec)
    fig = renderer.render_line(spec, df)
    # seaborn lineplot draws one line per hue level
    assert len(fig.axes[0].get_lines()) >= 2


def test_render_scatter_returns_figure(renderer, tmp_path):
    p = tmp_path / "scatter.csv"
    p.write_text("x,y,c\n1,2,A\n3,4,B\n5,6,A\n7,8,B\n")
    spec = ScatterSpec(input_path=str(p), xvar="x", yvar="y", colorvar="c", alpha=0.5)
    df = _load(spec)
    fig = renderer.render_scatter(spec, df)
    assert isinstance(fig, Figure)


def test_render_scatter_with_sizevar(renderer, tmp_path):
    p = tmp_path / "sc.csv"
    p.write_text("x,y,s\n1,2,10\n3,4,20\n5,6,30\n")
    spec = ScatterSpec(input_path=str(p), xvar="x", yvar="y", sizevar="s")
    df = _load(spec)
    fig = renderer.render_scatter(spec, df)
    assert isinstance(fig, Figure)
```

- [ ] **Step 2: Run tests to verify they fail**

Run:
```bash
.venv/bin/pytest tests/test_renderer_matplotlib.py -v -k "line or scatter"
```

Expected: 4 tests fail with `NotImplementedError`.

- [ ] **Step 3: Implement `render_line` and `render_scatter` in the renderer**

Edit `/Users/dan/LOCALSTAGE/csvviz-project/csvviz/renderers/matplotlib_renderer.py`. Replace the `render_line` and `render_scatter` stubs with:

```python
    def render_line(self, spec: LineSpec, df: pd.DataFrame) -> Figure:
        self._apply_theme(spec)
        fig, ax = self._new_figure(spec)
        sns.lineplot(
            data=df,
            x=spec.xvar,
            y=spec.yvar,
            hue=spec.colorvar,
            ax=ax,
            palette=spec.palette,
        )
        self._finalize(fig, ax, spec)
        return fig

    def render_scatter(self, spec: ScatterSpec, df: pd.DataFrame) -> Figure:
        self._apply_theme(spec)
        fig, ax = self._new_figure(spec)
        sns.scatterplot(
            data=df,
            x=spec.xvar,
            y=spec.yvar,
            hue=spec.colorvar,
            size=spec.sizevar,
            alpha=spec.alpha,
            ax=ax,
            palette=spec.palette,
        )
        self._finalize(fig, ax, spec)
        return fig
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
.venv/bin/pytest tests/test_renderer_matplotlib.py -v
```

Expected: 9 passed.

- [ ] **Step 5: Format and commit**

```bash
.venv/bin/black csvviz tests
git add csvviz/renderers/matplotlib_renderer.py tests/test_renderer_matplotlib.py
git commit -m "implement render_line and render_scatter"
```

---

## Task 10: MatplotlibRenderer — hist and area

**Files:**
- Modify: `csvviz/renderers/matplotlib_renderer.py`
- Modify: `tests/test_renderer_matplotlib.py`

- [ ] **Step 1: Append failing tests for hist and area**

Append to `tests/test_renderer_matplotlib.py`:
```python
from csvviz.specs import AreaSpec, HistSpec


def test_render_hist_returns_figure(renderer):
    spec = HistSpec(input_path=str(FIXTURES / "tings.csv"), xvar="amount", bins=5)
    df = _load(spec)
    fig = renderer.render_hist(spec, df)
    assert isinstance(fig, Figure)


def test_render_hist_cumulative(renderer):
    spec = HistSpec(
        input_path=str(FIXTURES / "tings.csv"), xvar="amount", cumulative=True
    )
    df = _load(spec)
    fig = renderer.render_hist(spec, df)
    assert isinstance(fig, Figure)


def test_render_area_single_series(renderer):
    spec = AreaSpec(
        input_path=str(FIXTURES / "stocks.csv"), xvar="date", yvar="price"
    )
    df = _load(spec)
    fig = renderer.render_area(spec, df)
    assert isinstance(fig, Figure)


def test_render_area_stacked(renderer):
    spec = AreaSpec(
        input_path=str(FIXTURES / "stocks.csv"),
        xvar="date",
        yvar="price",
        colorvar="company",
        stacked=True,
    )
    df = _load(spec)
    fig = renderer.render_area(spec, df)
    assert isinstance(fig, Figure)


def test_render_area_normalized(renderer):
    spec = AreaSpec(
        input_path=str(FIXTURES / "stocks.csv"),
        xvar="date",
        yvar="price",
        colorvar="company",
        normalized=True,
    )
    df = _load(spec)
    fig = renderer.render_area(spec, df)
    assert isinstance(fig, Figure)
```

- [ ] **Step 2: Run tests to verify they fail**

Run:
```bash
.venv/bin/pytest tests/test_renderer_matplotlib.py -v -k "hist or area"
```

Expected: 5 tests fail with `NotImplementedError`.

- [ ] **Step 3: Implement `render_hist` and `render_area`**

Replace the `render_hist` and `render_area` stubs in `csvviz/renderers/matplotlib_renderer.py` with:

```python
    def render_hist(self, spec: HistSpec, df: pd.DataFrame) -> Figure:
        self._apply_theme(spec)
        fig, ax = self._new_figure(spec)
        sns.histplot(
            data=df,
            x=spec.xvar,
            hue=spec.colorvar,
            bins=spec.bins or "auto",
            cumulative=spec.cumulative,
            ax=ax,
            palette=spec.palette,
        )
        self._finalize(fig, ax, spec)
        return fig

    def render_area(self, spec: AreaSpec, df: pd.DataFrame) -> Figure:
        self._apply_theme(spec)
        fig, ax = self._new_figure(spec)

        if spec.colorvar and spec.stacked:
            pivot = df.pivot_table(
                index=spec.xvar,
                columns=spec.colorvar,
                values=spec.yvar,
                aggfunc="sum",
            ).fillna(0)
            if spec.normalized:
                pivot = pivot.div(pivot.sum(axis=1), axis=0) * 100.0
            ax.stackplot(
                pivot.index, pivot.T.values, labels=list(pivot.columns)
            )
            ax.legend(loc="best")
        elif spec.colorvar:
            # Overlapping (non-stacked) multi-series areas.
            for series_name, group in df.groupby(spec.colorvar):
                ax.fill_between(
                    group[spec.xvar], group[spec.yvar], alpha=0.4, label=str(series_name)
                )
            ax.legend(loc="best")
        else:
            ax.fill_between(df[spec.xvar], df[spec.yvar], alpha=0.6)

        self._finalize(fig, ax, spec)
        return fig
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
.venv/bin/pytest tests/test_renderer_matplotlib.py -v
```

Expected: 14 passed.

- [ ] **Step 5: Format and commit**

```bash
.venv/bin/black csvviz tests
git add csvviz/renderers/matplotlib_renderer.py tests/test_renderer_matplotlib.py
git commit -m "implement render_hist and render_area"
```

---

## Task 11: MatplotlibRenderer — heatmap

**Files:**
- Modify: `csvviz/renderers/matplotlib_renderer.py`
- Modify: `tests/test_renderer_matplotlib.py`

- [ ] **Step 1: Append failing test for heatmap**

Append to `tests/test_renderer_matplotlib.py`:
```python
from csvviz.specs import HeatmapSpec


def test_render_heatmap_returns_figure(renderer):
    spec = HeatmapSpec(input_path=str(FIXTURES / "hot.csv"))
    df = _load(spec)
    fig = renderer.render_heatmap(spec, df)
    assert isinstance(fig, Figure)
    # One axes for the heatmap; seaborn adds a colorbar axes as a sibling
    assert len(fig.axes) >= 1
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
.venv/bin/pytest tests/test_renderer_matplotlib.py::test_render_heatmap_returns_figure -v
```

Expected: fails with `NotImplementedError`.

- [ ] **Step 3: Implement `render_heatmap`**

Replace the `render_heatmap` stub in `csvviz/renderers/matplotlib_renderer.py` with:

```python
    def render_heatmap(self, spec: HeatmapSpec, df: pd.DataFrame) -> Figure:
        self._apply_theme(spec)
        fig, ax = self._new_figure(spec)
        pivot = df.pivot_table(
            index=spec.yvar, columns=spec.xvar, values=spec.valuevar, aggfunc="sum"
        )
        sns.heatmap(pivot, ax=ax)
        self._finalize(fig, ax, spec)
        return fig
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
.venv/bin/pytest tests/test_renderer_matplotlib.py -v
```

Expected: 15 passed.

- [ ] **Step 5: Format and commit**

```bash
.venv/bin/black csvviz tests
git add csvviz/renderers/matplotlib_renderer.py tests/test_renderer_matplotlib.py
git commit -m "implement render_heatmap"
```

---

## Task 12: MatplotlibRenderer — faceting (small multiples)

Add `spec.facet` support to all six `render_*` methods. When `spec.facet` is set, the renderer uses seaborn's faceted constructors (`relplot`/`catplot`/`displot`) or a manual `subplots` loop, and returns the FacetGrid's underlying `Figure`.

**Files:**
- Modify: `csvviz/renderers/matplotlib_renderer.py`
- Modify: `tests/test_renderer_matplotlib.py`
- Modify: `tests/fixtures/` (add a small CSV with a facet column)

- [ ] **Step 1: Create a facetable fixture**

Write `/Users/dan/LOCALSTAGE/csvviz-project/tests/fixtures/facetable.csv`:
```
region,product,sales
N,A,10
N,B,20
N,C,5
S,A,15
S,B,25
S,C,10
E,A,12
E,B,18
E,C,7
```

- [ ] **Step 2: Append failing facet tests**

Append to `tests/test_renderer_matplotlib.py`:
```python
def test_render_bar_with_facet(renderer):
    spec = BarSpec(
        input_path=str(FIXTURES / "facetable.csv"),
        xvar="product",
        yvar="sales",
        facet="region",
        facet_cols=3,
    )
    df = _load(spec)
    fig = renderer.render_bar(spec, df)
    assert isinstance(fig, Figure)
    # One axes per region (3), plus possibly seaborn-added artifacts
    assert len(fig.axes) >= 3


def test_render_line_with_facet(renderer):
    spec = LineSpec(
        input_path=str(FIXTURES / "facetable.csv"),
        xvar="product",
        yvar="sales",
        facet="region",
    )
    df = _load(spec)
    fig = renderer.render_line(spec, df)
    assert isinstance(fig, Figure)
    assert len(fig.axes) >= 3


def test_render_scatter_with_facet(renderer):
    spec = ScatterSpec(
        input_path=str(FIXTURES / "facetable.csv"),
        xvar="product",
        yvar="sales",
        facet="region",
    )
    df = _load(spec)
    fig = renderer.render_scatter(spec, df)
    assert isinstance(fig, Figure)
    assert len(fig.axes) >= 3


def test_render_hist_with_facet(renderer):
    spec = HistSpec(
        input_path=str(FIXTURES / "facetable.csv"),
        xvar="sales",
        facet="region",
        bins=3,
    )
    df = _load(spec)
    fig = renderer.render_hist(spec, df)
    assert isinstance(fig, Figure)
    assert len(fig.axes) >= 3
```

- [ ] **Step 3: Run tests to verify they fail**

Run:
```bash
.venv/bin/pytest tests/test_renderer_matplotlib.py -v -k facet
```

Expected: 4 tests fail — non-faceted code path returns a single-axes Figure.

- [ ] **Step 4: Refactor renderer methods to branch on `spec.facet`**

Edit `/Users/dan/LOCALSTAGE/csvviz-project/csvviz/renderers/matplotlib_renderer.py`. Add this helper method to the `MatplotlibRenderer` class (before the existing helpers, after `render_heatmap`):

```python
    def _facet_figure(self, spec: BaseSpec, df: pd.DataFrame, kind: str, **kwargs) -> Figure:
        """Use seaborn's faceted constructors. Returns g.fig from the FacetGrid."""
        common = dict(
            data=df,
            col=spec.facet,
            col_wrap=spec.facet_cols,
            palette=spec.palette,
        )
        if kind in ("bar", "count", "box", "violin", "strip", "swarm", "boxen", "point"):
            g = sns.catplot(kind=kind, **common, **kwargs)
        elif kind in ("scatter", "line"):
            g = sns.relplot(kind=kind, **common, **kwargs)
        elif kind == "hist":
            g = sns.displot(kind="hist", **common, **kwargs)
        else:
            raise ValueError(f"no faceted constructor for kind={kind!r}")
        # Apply size + finalize on the underlying figure
        w_px = spec.width_px or DEFAULT_WIDTH_PX
        h_px = spec.height_px or DEFAULT_HEIGHT_PX
        g.fig.set_size_inches(w_px / DEFAULT_DPI, h_px / DEFAULT_DPI)
        if spec.title:
            g.fig.suptitle(spec.title)
        return g.fig
```

Now modify each `render_*` method to branch on `spec.facet`. Replace the body of `render_bar` with:

```python
    def render_bar(self, spec: BarSpec, df: pd.DataFrame) -> Figure:
        self._apply_theme(spec)
        x, y = (spec.yvar, spec.xvar) if spec.horizontal else (spec.xvar, spec.yvar)

        if spec.facet:
            return self._facet_figure(
                spec, df, kind="bar", x=x, y=y, hue=spec.colorvar,
                orient="h" if spec.horizontal else "v",
            )

        fig, ax = self._new_figure(spec)
        if spec.stacked:
            self._draw_stacked_bar(ax, df, spec)
        elif spec.colorvar:
            sns.barplot(
                data=df, x=x, y=y, hue=spec.colorvar, ax=ax,
                palette=spec.palette,
                orient="h" if spec.horizontal else "v",
            )
        else:
            sns.barplot(
                data=df, x=x, y=y, ax=ax,
                color=(spec.colors[0] if spec.colors else None),
                orient="h" if spec.horizontal else "v",
            )
        if spec.sort:
            self._apply_bar_sort(ax, spec)
        self._finalize(fig, ax, spec)
        return fig
```

Replace the body of `render_line` with:

```python
    def render_line(self, spec: LineSpec, df: pd.DataFrame) -> Figure:
        self._apply_theme(spec)
        if spec.facet:
            return self._facet_figure(
                spec, df, kind="line",
                x=spec.xvar, y=spec.yvar, hue=spec.colorvar,
            )
        fig, ax = self._new_figure(spec)
        sns.lineplot(
            data=df, x=spec.xvar, y=spec.yvar, hue=spec.colorvar,
            ax=ax, palette=spec.palette,
        )
        self._finalize(fig, ax, spec)
        return fig
```

Replace the body of `render_scatter` with:

```python
    def render_scatter(self, spec: ScatterSpec, df: pd.DataFrame) -> Figure:
        self._apply_theme(spec)
        if spec.facet:
            return self._facet_figure(
                spec, df, kind="scatter",
                x=spec.xvar, y=spec.yvar, hue=spec.colorvar,
                size=spec.sizevar, alpha=spec.alpha,
            )
        fig, ax = self._new_figure(spec)
        sns.scatterplot(
            data=df, x=spec.xvar, y=spec.yvar, hue=spec.colorvar,
            size=spec.sizevar, alpha=spec.alpha, ax=ax, palette=spec.palette,
        )
        self._finalize(fig, ax, spec)
        return fig
```

Replace the body of `render_hist` with:

```python
    def render_hist(self, spec: HistSpec, df: pd.DataFrame) -> Figure:
        self._apply_theme(spec)
        if spec.facet:
            return self._facet_figure(
                spec, df, kind="hist",
                x=spec.xvar, hue=spec.colorvar,
                bins=spec.bins or "auto", cumulative=spec.cumulative,
            )
        fig, ax = self._new_figure(spec)
        sns.histplot(
            data=df, x=spec.xvar, hue=spec.colorvar,
            bins=spec.bins or "auto", cumulative=spec.cumulative,
            ax=ax, palette=spec.palette,
        )
        self._finalize(fig, ax, spec)
        return fig
```

For `render_area` and `render_heatmap`, faceting is not supported in v0.5 (no clean seaborn equivalent for stacked-area-by-facet, and heatmap-by-facet is unusual). Add at the very top of each method body:

```python
        if spec.facet:
            raise ConflictingFlagsError(
                f"{spec.__class__.__name__} does not support faceting in v0.5"
            )
```

Add to the imports at the top of `csvviz/renderers/matplotlib_renderer.py`:
```python
from csvviz.exceptions import ConflictingFlagsError
```

- [ ] **Step 5: Run all renderer tests**

Run:
```bash
.venv/bin/pytest tests/test_renderer_matplotlib.py -v
```

Expected: all tests pass (existing 15 + 4 new facet tests = 19).

- [ ] **Step 6: Format and commit**

```bash
.venv/bin/black csvviz tests
git add csvviz/renderers/matplotlib_renderer.py tests/test_renderer_matplotlib.py tests/fixtures/facetable.csv
git commit -m "add faceting (small multiples) support for bar/line/scatter/hist"
```

---

## Task 13: CLI scaffold — Click group, version, error wrapper

**Files:**
- Create: `csvviz/cli.py`
- Create: `tests/test_cli.py`

- [ ] **Step 1: Write failing tests for the CLI scaffold and `--version`**

Write `/Users/dan/LOCALSTAGE/csvviz-project/tests/test_cli.py`:
```python
from pathlib import Path

from click.testing import CliRunner

from csvviz import __version__
from csvviz.cli import cli

FIXTURES = Path(__file__).parent / "fixtures"


def test_version_flag():
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_help_lists_subcommands():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    for cmd in ("bar", "line", "scatter", "hist", "area", "heatmap"):
        assert cmd in result.output
```

- [ ] **Step 2: Run tests to verify they fail**

Run:
```bash
.venv/bin/pytest tests/test_cli.py -v
```

Expected: ImportError on `csvviz.cli`.

- [ ] **Step 3: Implement the CLI scaffold**

Write `/Users/dan/LOCALSTAGE/csvviz-project/csvviz/cli.py`:
```python
from __future__ import annotations

import os
import sys
from functools import wraps
from pathlib import Path
from typing import Callable

import click

from csvviz import __version__
from csvviz.data import load_csv
from csvviz.exceptions import CsvvizError
from csvviz.output import deliver
from csvviz.renderers.matplotlib_renderer import MatplotlibRenderer
from csvviz.specs import (
    AreaSpec,
    BarSpec,
    BaseSpec,
    HeatmapSpec,
    HistSpec,
    LineSpec,
    ScatterSpec,
)


def _handle_errors(func: Callable) -> Callable:
    """Wrap a subcommand so CsvvizError prints a friendly message and exits 1."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except CsvvizError as err:
            click.echo(f"error: {err}", err=True)
            sys.exit(1)
        except Exception:
            if os.environ.get("CSVVIZ_DEBUG"):
                raise
            click.echo("error: unexpected failure (set CSVVIZ_DEBUG=1 for traceback)", err=True)
            sys.exit(2)

    return wrapper


def _parse_lim(value: str | None) -> tuple[float, float] | None:
    if not value:
        return None
    parts = [p.strip() for p in value.split(",")]
    if len(parts) != 2:
        raise click.BadParameter("must be MIN,MAX")
    return (float(parts[0]), float(parts[1]))


def _parse_colors(value: str | None) -> list[str] | None:
    if not value:
        return None
    return [c.strip() for c in value.split(",") if c.strip()]


# --- common options ---


def common_options(f: Callable) -> Callable:
    """Decorator stack for flags shared by every subcommand."""
    decorators = [
        click.argument("input_file", type=click.Path(dir_okay=False), required=False),
        click.option("-x", "--xvar", default=None, help="x column (default: first column)"),
        click.option("-y", "--yvar", default=None, help="y column (default: second column)"),
        click.option("-c", "--colorvar", default=None, help="color/series column"),
        click.option("-f", "--facet", default=None, help="facet column for small multiples"),
        click.option("--facet-cols", type=int, default=3, show_default=True),
        click.option("-T", "--title", default=None),
        click.option("-W", "--width", "width_px", type=int, default=None, help="width in pixels"),
        click.option("-H", "--height", "height_px", type=int, default=None, help="height in pixels"),
        click.option("--xlim", default=None, help="x-axis MIN,MAX"),
        click.option("--ylim", default=None, help="y-axis MIN,MAX"),
        click.option("--xlabel", default=None),
        click.option("--ylabel", default=None),
        click.option("--no-legend", is_flag=True),
        click.option(
            "--theme",
            type=click.Choice(["whitegrid", "darkgrid", "white", "dark", "ticks"]),
            default="whitegrid",
            show_default=True,
        ),
        click.option("--palette", default=None, help="seaborn/matplotlib palette name"),
        click.option("--colors", default=None, help="comma-delimited explicit colors"),
        click.option("-o", "--output", type=click.Path(dir_okay=False), default=None),
        click.option("--no-show", is_flag=True, help="suppress window (saves to fallback PNG)"),
        click.option("--dpi", type=int, default=100, show_default=True),
    ]
    for dec in reversed(decorators):
        f = dec(f)
    return f


def _build_base_kwargs(input_file, kw):
    """Extract BaseSpec kwargs from Click's kwargs dict (in place)."""
    return dict(
        input_path=input_file,
        xvar=kw.pop("xvar"),
        yvar=kw.pop("yvar"),
        colorvar=kw.pop("colorvar"),
        facet=kw.pop("facet"),
        facet_cols=kw.pop("facet_cols"),
        title=kw.pop("title"),
        width_px=kw.pop("width_px"),
        height_px=kw.pop("height_px"),
        xlim=_parse_lim(kw.pop("xlim")),
        ylim=_parse_lim(kw.pop("ylim")),
        xlabel=kw.pop("xlabel"),
        ylabel=kw.pop("ylabel"),
        no_legend=kw.pop("no_legend"),
        theme=kw.pop("theme"),
        palette=kw.pop("palette"),
        colors=_parse_colors(kw.pop("colors")),
    )


def _run(spec: BaseSpec, chart_type: str, render_fn: Callable, output, no_show, dpi):
    df = load_csv(spec)
    renderer = MatplotlibRenderer()
    fig = render_fn(renderer, spec, df)
    deliver(
        fig,
        chart_type=chart_type,
        input_path=spec.input_path,
        output=Path(output) if output else None,
        no_show=no_show,
        dpi=dpi,
    )


@click.group()
@click.version_option(__version__, "--version", prog_name="csvviz")
def cli() -> None:
    """csvviz — quick charts from CSV files."""
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
.venv/bin/pytest tests/test_cli.py -v
```

Expected: `test_version_flag` passes; `test_help_lists_subcommands` fails (no subcommands registered yet). Leave the failure — Task 13 adds the subcommands.

- [ ] **Step 5: Commit the scaffold**

```bash
.venv/bin/black csvviz tests
git add csvviz/cli.py tests/test_cli.py
git commit -m "add CLI scaffold: group, version, common options, error wrapper"
```

---

## Task 14: CLI subcommands — bar, line, scatter

**Files:**
- Modify: `csvviz/cli.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Append failing CLI integration tests**

Append to `tests/test_cli.py`:
```python
def test_bar_simple_writes_png(tmp_path):
    runner = CliRunner()
    out = tmp_path / "out.png"
    result = runner.invoke(
        cli,
        ["bar", "--no-show", "-o", str(out), str(FIXTURES / "tings.csv")],
    )
    assert result.exit_code == 0, result.output
    assert out.exists() and out.stat().st_size > 0


def test_bar_invalid_column_exits_1(tmp_path):
    runner = CliRunner()
    out = tmp_path / "out.png"
    result = runner.invoke(
        cli,
        ["bar", "-x", "nope", "--no-show", "-o", str(out), str(FIXTURES / "tings.csv")],
    )
    assert result.exit_code == 1
    assert "nope" in result.output


def test_line_multi_series_writes_png(tmp_path):
    runner = CliRunner()
    out = tmp_path / "out.png"
    result = runner.invoke(
        cli,
        [
            "line", "-x", "date", "-y", "price", "-c", "company",
            "--no-show", "-o", str(out), str(FIXTURES / "stocks.csv"),
        ],
    )
    assert result.exit_code == 0, result.output
    assert out.exists()


def test_scatter_writes_png(tmp_path):
    p = tmp_path / "sc.csv"
    p.write_text("x,y\n1,2\n3,4\n5,6\n")
    out = tmp_path / "out.png"
    runner = CliRunner()
    result = runner.invoke(
        cli, ["scatter", "--no-show", "-o", str(out), str(p)]
    )
    assert result.exit_code == 0, result.output
    assert out.exists()
```

- [ ] **Step 2: Run tests to verify they fail**

Run:
```bash
.venv/bin/pytest tests/test_cli.py -v
```

Expected: new tests fail (no `bar`, `line`, `scatter` commands yet); `test_help_lists_subcommands` still failing.

- [ ] **Step 3: Add bar/line/scatter subcommands**

Append to `/Users/dan/LOCALSTAGE/csvviz-project/csvviz/cli.py`:

```python
@cli.command("bar")
@common_options
@click.option("--horizontal", is_flag=True, help="horizontal bar chart")
@click.option("--stacked", is_flag=True, help="stack bars (requires -c)")
@click.option("--normalized", is_flag=True, help="normalize stacks to 100%% (implies --stacked)")
@click.option(
    "--sort",
    type=click.Choice(["x", "y", "-x", "-y"]),
    default=None,
    help="sort bars by axis",
)
@_handle_errors
def bar_cmd(input_file, output, no_show, dpi, horizontal, stacked, normalized, sort, **kw):
    """A bar/column chart."""
    base = _build_base_kwargs(input_file, kw)
    spec = BarSpec(
        **base, horizontal=horizontal, stacked=stacked, normalized=normalized, sort=sort
    )
    _run(spec, "bar", MatplotlibRenderer.render_bar, output, no_show, dpi)


@cli.command("line")
@common_options
@_handle_errors
def line_cmd(input_file, output, no_show, dpi, **kw):
    """A line chart."""
    base = _build_base_kwargs(input_file, kw)
    spec = LineSpec(**base)
    _run(spec, "line", MatplotlibRenderer.render_line, output, no_show, dpi)


@cli.command("scatter")
@common_options
@click.option("-s", "--sizevar", default=None, help="column to map to marker size")
@click.option("--alpha", type=float, default=None, help="marker opacity (0..1)")
@_handle_errors
def scatter_cmd(input_file, output, no_show, dpi, sizevar, alpha, **kw):
    """A scatter plot."""
    base = _build_base_kwargs(input_file, kw)
    spec = ScatterSpec(**base, sizevar=sizevar, alpha=alpha)
    _run(spec, "scatter", MatplotlibRenderer.render_scatter, output, no_show, dpi)
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
.venv/bin/pytest tests/test_cli.py -v
```

Expected: `test_version_flag`, `test_bar_simple_writes_png`, `test_bar_invalid_column_exits_1`, `test_line_multi_series_writes_png`, `test_scatter_writes_png` pass. `test_help_lists_subcommands` still fails (missing hist/area/heatmap — Task 14 fixes).

- [ ] **Step 5: Commit**

```bash
.venv/bin/black csvviz tests
git add csvviz/cli.py tests/test_cli.py
git commit -m "add bar, line, scatter CLI subcommands"
```

---

## Task 15: CLI subcommands — hist, area, heatmap

**Files:**
- Modify: `csvviz/cli.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Append failing tests for remaining subcommands**

Append to `tests/test_cli.py`:
```python
def test_hist_writes_png(tmp_path):
    runner = CliRunner()
    out = tmp_path / "out.png"
    result = runner.invoke(
        cli,
        ["hist", "-x", "amount", "--no-show", "-o", str(out), str(FIXTURES / "tings.csv")],
    )
    assert result.exit_code == 0, result.output
    assert out.exists()


def test_area_writes_png(tmp_path):
    runner = CliRunner()
    out = tmp_path / "out.png"
    result = runner.invoke(
        cli,
        ["area", "-x", "date", "-y", "price", "--no-show", "-o", str(out),
         str(FIXTURES / "stocks.csv")],
    )
    assert result.exit_code == 0, result.output
    assert out.exists()


def test_heatmap_writes_png(tmp_path):
    runner = CliRunner()
    out = tmp_path / "out.png"
    result = runner.invoke(
        cli, ["heatmap", "--no-show", "-o", str(out), str(FIXTURES / "hot.csv")]
    )
    assert result.exit_code == 0, result.output
    assert out.exists()


def test_conflict_normalized_without_colorvar_exits_1(tmp_path):
    runner = CliRunner()
    out = tmp_path / "out.png"
    result = runner.invoke(
        cli,
        ["bar", "--normalized", "--no-show", "-o", str(out), str(FIXTURES / "tings.csv")],
    )
    assert result.exit_code == 1
    assert "colorvar" in result.output or "-c" in result.output
```

- [ ] **Step 2: Run tests to verify they fail**

Run:
```bash
.venv/bin/pytest tests/test_cli.py -v
```

Expected: hist/area/heatmap tests fail.

- [ ] **Step 3: Add hist, area, heatmap subcommands**

Append to `csvviz/cli.py`:

```python
@cli.command("hist")
@common_options
@click.option("--bins", type=int, default=None, help="number of bins")
@click.option("--cumulative", is_flag=True, help="cumulative histogram")
@_handle_errors
def hist_cmd(input_file, output, no_show, dpi, bins, cumulative, **kw):
    """A histogram."""
    base = _build_base_kwargs(input_file, kw)
    spec = HistSpec(**base, bins=bins, cumulative=cumulative)
    _run(spec, "hist", MatplotlibRenderer.render_hist, output, no_show, dpi)


@cli.command("area")
@common_options
@click.option("--stacked", is_flag=True, help="stack areas (requires -c)")
@click.option("--normalized", is_flag=True, help="normalize stacks to 100%% (implies --stacked)")
@_handle_errors
def area_cmd(input_file, output, no_show, dpi, stacked, normalized, **kw):
    """An area chart."""
    base = _build_base_kwargs(input_file, kw)
    spec = AreaSpec(**base, stacked=stacked, normalized=normalized)
    _run(spec, "area", MatplotlibRenderer.render_area, output, no_show, dpi)


@cli.command("heatmap")
@common_options
@_handle_errors
def heatmap_cmd(input_file, output, no_show, dpi, **kw):
    """A heatmap (x=col1, y=col2, value=col3 by default)."""
    base = _build_base_kwargs(input_file, kw)
    spec = HeatmapSpec(**base)
    _run(spec, "heatmap", MatplotlibRenderer.render_heatmap, output, no_show, dpi)
```

- [ ] **Step 4: Run all tests**

Run:
```bash
.venv/bin/pytest -v
```

Expected: every test in the suite passes. `test_help_lists_subcommands` now passes because all 6 subcommands are registered.

- [ ] **Step 5: Commit**

```bash
.venv/bin/black csvviz tests
git add csvviz/cli.py tests/test_cli.py
git commit -m "add hist, area, heatmap CLI subcommands"
```

---

## Task 16: End-to-end smoke test — `csvviz bar examples/tings.csv` just works

**Files:**
- Create: `examples/tings.csv`, `examples/stocks.csv`, `examples/hot.csv`, `examples/cars.csv`

- [ ] **Step 1: Copy a useful subset of example CSVs**

Run:
```bash
mkdir -p examples
cp old-csvviz/examples/tings.csv examples/tings.csv
cp old-csvviz/examples/stocks.csv examples/stocks.csv
cp old-csvviz/examples/hot.csv examples/hot.csv
cp old-csvviz/examples/cars.csv examples/cars.csv
```

- [ ] **Step 2: Verify the headline use case from CLAUDE.md works headlessly**

Run:
```bash
.venv/bin/csvviz bar --no-show examples/tings.csv
ls -la tings-bar.png
```

Expected:
- Command exits 0.
- Prints `wrote /Users/dan/LOCALSTAGE/csvviz-project/tings-bar.png` (or similar) to stderr.
- `tings-bar.png` exists and is non-empty.

- [ ] **Step 3: Verify the multi-series line use case**

Run:
```bash
.venv/bin/csvviz line -x date -y price -c company --no-show examples/stocks.csv
ls -la stocks-line.png
```

Expected: exits 0; `stocks-line.png` exists and is non-empty.

- [ ] **Step 4: Verify stdin works**

Run:
```bash
cat examples/tings.csv | .venv/bin/csvviz hist -x amount --bins 3 --no-show
ls -la stdin-hist.png
```

Expected: exits 0; `stdin-hist.png` exists.

- [ ] **Step 5: Clean up generated PNGs and commit examples**

Run:
```bash
rm -f tings-bar.png stocks-line.png stdin-hist.png
git add examples/
git commit -m "add example CSVs"
```

---

## Task 17: README and final pass

**Files:**
- Create: `README.md`

- [ ] **Step 1: Write `README.md`**

Write `/Users/dan/LOCALSTAGE/csvviz-project/README.md`:
```markdown
# csvviz

Quick charts from CSV files on the command line.

```bash
csvviz bar examples/tings.csv
csvviz line -x date -y price -c company examples/stocks.csv
csvviz scatter -x weight -y mpg -c origin examples/cars.csv
csvviz heatmap examples/hot.csv
```

## Install

```bash
pip install -e ".[dev]"
```

## Chart types

`bar`, `line`, `scatter`, `hist`, `area`, `heatmap`.

Defaults: first column → x, second → y. For `heatmap`, third column → value.

## Common flags

| Flag | What |
|---|---|
| `-x`, `-y`, `-c`, `-f` | column mappings (x, y, color/series, facet) |
| `-T`, `-W`, `-H` | title, width (px), height (px) |
| `--xlim MIN,MAX`, `--ylim MIN,MAX` | axis limits |
| `--theme`, `--palette`, `--colors` | styling |
| `-o PATH`, `--no-show`, `--dpi N` | output |

Without `-o`: opens a window when a display is available, otherwise saves to `./<csvstem>-<charttype>.png`.

Per-chart-type flags: `csvviz <type> --help`.

## Development

```bash
pip install -e ".[dev]"
pytest
black csvviz tests
```
```

- [ ] **Step 2: Run the full test suite one final time**

Run:
```bash
.venv/bin/pytest -v
```

Expected: all tests pass.

- [ ] **Step 3: Run black to confirm formatting is clean**

Run:
```bash
.venv/bin/black --check csvviz tests
```

Expected: `All done!` (no files would be reformatted).

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "add README"
```

- [ ] **Step 5: Tag v0.5.0**

Run:
```bash
git tag v0.5.0
git log --oneline
```

Expected: a clean linear history of ~17 commits ending at `v0.5.0`.

---

## Self-review notes

- **Spec coverage:** Every spec section maps to at least one task. §1 goals → demonstrated by Task 16. §2 CLI surface → Tasks 13–15. §3 architecture → realized by the file boundaries in Tasks 5–15. §4 specs → Task 3. §5 renderer protocol → Task 7; chart implementations Tasks 8–11; faceting in Task 12. §6 data + output → Tasks 5 and 6. §7 errors → Task 2 + the `_handle_errors` wrapper in Task 13. §8 testing → tests built incrementally in every task. §9 layout & deps → Task 1.
- **Deferred items from §10** (annotate, cmap, streamgraph, info, png-stdout, vega renderer): intentionally not in the plan.
- **Type consistency check:** `BaseSpec`, `BarSpec`, etc. are spelled consistently across Tasks 3, 5, 7, 8–12, 13–15. `MatplotlibRenderer` and its `render_*` method names match the protocol in Task 7. `deliver()` signature matches between Task 6 (definition) and Task 13 (`_run` helper).
- **Faceting:** Wired end-to-end via Task 12 for bar/line/scatter/hist. `AreaSpec` and `HeatmapSpec` with `--facet` raise `ConflictingFlagsError` (no clean seaborn API in v0.5); document as a known limitation in the README during Task 17 if desired.
