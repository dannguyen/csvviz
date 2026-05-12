# csvviz 0.5 — Design

**Date:** 2026-05-11
**Status:** Approved
**Replaces:** csvviz 0.4.9.2 (in `old-csvviz/`)

## 1. Goals & non-goals

### Goals
- `csvviz <charttype> <input.csv>` produces a useful chart with zero flags. First column is x, second is y.
- Common tweaks (color/series, facet, title, axis limits, dimensions) are short flags away.
- Default behavior is "show a window," with automatic fallback to writing a PNG when there is no display (SSH, CI, headless).
- The internal seam between "what the user asked for" (Spec) and "how to draw it" (Renderer) is clean enough that adding a second backend later is a new module, not a rewrite.
- Test suite uses pytest. Code is black-formatted.

### Non-goals for v0.5
- Interactive output (no zoom/hover/tooltips beyond what `plt.show()` gives natively).
- Reusable spec JSON (the old version's Vega-Lite output). Specs are internal, not a public format.
- Streamgraph (deferred — neither matplotlib nor seaborn has a first-class API for it).
- Multi-input / joins / data transforms beyond what `pandas.read_csv` does for free.
- The old version's `info` subcommand and the `cvz` short alias.

## 2. CLI surface

Shape: `csvviz <charttype> [flags] <input.csv>`. Input may be a path, `-` for stdin, or omitted entirely when stdin is piped.

### Common flags (all chart types)

**Data mapping**
- `-x, --xvar COL` — x column (default: first column)
- `-y, --yvar COL` — y column (default: second column; ignored for `hist`)
- `-c, --colorvar COL` — color/series column; meaning varies by chart type
- `-f, --facet COL` — facet column for small multiples
- `--facet-cols N` — columns per facet row (default 3)

**Chart properties**
- `-T, --title STR`
- `-W, --width PX` / `-H, --height PX` — pixels, converted internally to inches × dpi
- `--xlim MIN,MAX` / `--ylim MIN,MAX`
- `--xlabel STR` / `--ylabel STR`
- `--no-legend`
- `--theme {whitegrid,darkgrid,white,dark,ticks}` — seaborn theme (default `whitegrid`)
- `--palette NAME` — seaborn/matplotlib palette (e.g. `viridis`, `tab10`)
- `--colors LIST` — comma-delimited explicit colors; overrides `--palette`

**Output**
- `-o, --output PATH` — save to file; format inferred from extension (`.png`, `.svg`, `.pdf`)
- `--no-show` — suppress window even when one is available
- `--dpi N` — resolution for saved files (default 100)

### Default output behavior

| `--output` given? | `--no-show`? | Display available? | Action |
|---|---|---|---|
| yes | — | — | Save to path. No window. Print `wrote <path>` to stderr. |
| no | yes | — | Save to `./<csvstem>-<charttype>.png`. Print path to stderr. |
| no | no | yes | `plt.show()` (blocks until window closes). No file written. |
| no | no | no | Save to `./<csvstem>-<charttype>.png`. Print path + `no display detected` to stderr. |

### Chart-type-specific flags

- `bar`: `--horizontal`, `--stacked`, `--normalized` (implies `--stacked`), `--sort {x,y,-x,-y}`
- `hist`: `--bins N`, `--cumulative`
- `scatter`: `-s, --sizevar COL`, `--alpha FLOAT`
- `line`: (no extras — `-c` handles multi-series)
- `area`: `--stacked`, `--normalized`
- `heatmap`: defaults are x=col[0], y=col[1], value=col[2]; `--annotate` and `--cmap` are deferred (see §9)

### Examples

```
csvviz bar examples/tings.csv
csvviz line -x date -y price -c company examples/stocks.csv
csvviz bar -x name -y amount --horizontal examples/tings.csv
csvviz bar -c category --stacked --normalized examples/sales.csv
csvviz scatter -x weight -y mpg -c origin -s cylinders examples/cars.csv
csvviz heatmap examples/hot.csv
cat data.csv | csvviz hist -x age --bins 20
```

## 3. Architecture

Five modules, one-way dependencies. The data flows in one direction; no layer reaches back.

```
                    ┌─────────────┐
  user invocation → │   cli.py    │   Click group + 6 subcommands; parses flags
                    └──────┬──────┘
                           ▼
                    ┌─────────────┐
                    │  specs.py   │   Build a typed Spec dataclass (BarSpec, etc.)
                    └──────┬──────┘
                           ▼
                    ┌─────────────┐
                    │   data.py   │   Read CSV (file/stdin), resolve column defaults,
                    └──────┬──────┘   validate referenced columns exist
                           ▼
                    ┌─────────────────────────┐
                    │  renderers/             │   Renderer protocol; matplotlib
                    │   matplotlib_renderer   │   implementation does the actual drawing
                    └──────┬──────────────────┘
                           ▼
                    ┌─────────────┐
                    │  output.py  │   Show window / save file / headless fallback
                    └─────────────┘
```

**Boundaries**
- `cli.py` knows nothing about matplotlib. It builds a Spec and hands it off.
- `specs.py` knows nothing about Click or matplotlib. Just dataclasses and their internal validation.
- `renderers/matplotlib_renderer.py` knows nothing about Click or the filesystem. Returns a `matplotlib.figure.Figure`.
- `output.py` handles display detection and file writes; it does not import chart-type-specific code.

**Why this avoids the old version's tangle**
- No mixins. Five small modules with one-way dependencies.
- A second backend (`renderers/vega_renderer.py`, `renderers/plotly_renderer.py`) is a new file implementing the same protocol — no changes to `cli.py` or `specs.py`.

## 4. Spec dataclasses

All in `specs.py`. Pure data; cross-field validation in `__post_init__`. Backend-agnostic.

```python
@dataclass
class BaseSpec:
    input_path: str | None        # None means stdin
    xvar: str | None = None       # None → resolve to first column
    yvar: str | None = None       # None → resolve to second column
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

@dataclass
class BarSpec(BaseSpec):
    horizontal: bool = False
    stacked: bool = False
    normalized: bool = False
    sort: Literal["x", "y", "-x", "-y"] | None = None

@dataclass
class LineSpec(BaseSpec): pass

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

@dataclass
class HeatmapSpec(BaseSpec):
    valuevar: str | None = None   # None → resolve to third column
```

**Validation rules** (in `__post_init__`):
- `BarSpec`/`AreaSpec`: `normalized=True` implies `stacked=True`.
- `BarSpec`/`AreaSpec`: `normalized` or `stacked` without `colorvar` → `ConflictingFlagsError`.
- `colors` and `palette` cannot both be set.
- `xlim`/`ylim` must parse to two finite floats.
- `facet_cols >= 1`.

## 5. Renderer protocol

`renderers/base.py`:

```python
class Renderer(Protocol):
    def render_bar(self, spec: BarSpec, df: pd.DataFrame) -> Figure: ...
    def render_line(self, spec: LineSpec, df: pd.DataFrame) -> Figure: ...
    def render_scatter(self, spec: ScatterSpec, df: pd.DataFrame) -> Figure: ...
    def render_hist(self, spec: HistSpec, df: pd.DataFrame) -> Figure: ...
    def render_area(self, spec: AreaSpec, df: pd.DataFrame) -> Figure: ...
    def render_heatmap(self, spec: HeatmapSpec, df: pd.DataFrame) -> Figure: ...
```

One method per chart type. Each returns a `matplotlib.figure.Figure` for v0.5. A future backend would return its own figure type; when that happens, the return-type annotation gets promoted to a `Union` or a `Figure` protocol. We don't generalize speculatively.

### Matplotlib renderer notes

- Apply theme/palette via `seaborn.set_theme(style=spec.theme, palette=spec.palette or "tab10")`.
- Build the figure via `plt.subplots()` for non-faceted charts, or use seaborn's faceted constructors (`relplot`, `catplot`, `displot`) for faceted ones — they return `FacetGrid` objects whose `.fig` attribute is the matplotlib Figure we hand back.
- Drawing primitives:
  - `bar` → `seaborn.barplot` (non-stacked) or pandas `.plot.bar(stacked=...)` (stacked/normalized, after a pivot)
  - `line` → `seaborn.lineplot`
  - `scatter` → `seaborn.scatterplot` (size from `sizevar`, alpha from `alpha`)
  - `hist` → `seaborn.histplot`
  - `area` → `matplotlib.axes.Axes.fill_between` (and stack manually for `stacked`/`normalized`)
  - `heatmap` → pivot DataFrame into matrix, then `seaborn.heatmap` (no annotation/cmap overrides in v0.5)
- After drawing, apply title, axis labels, axis limits, legend visibility, and figure dimensions (`fig.set_size_inches(width_px/dpi, height_px/dpi)`).

## 6. Data loading & output

### `data.py — load_csv(spec) -> pd.DataFrame`
- Accepts `spec.input_path` as a path, `"-"` for stdin, or `None` (auto-detect piped stdin via `sys.stdin.isatty()`).
- Reads with `pd.read_csv()`; no separator/header overrides in v0.5.
- Resolves column defaults: if `xvar is None`, set to `df.columns[0]`; same pattern for `yvar` (when used) and `valuevar` (heatmap, `df.columns[2]`).
- Validates that every referenced column (`xvar`, `yvar`, `colorvar`, `facet`, `sizevar`, `valuevar`) exists. Raises `InvalidColumnError` naming the bad column and listing valid ones.
- Empty CSV or fewer columns than the chart type needs → `EmptyDataError`.

### `output.py — deliver(figure, spec, output_path, no_show, dpi)`
- Decision table is in §2 ("Default output behavior").
- Display detection:
  - Linux: display available iff `DISPLAY` or `WAYLAND_DISPLAY` is set.
  - macOS: display available unless `SSH_CONNECTION` is set (SSH session → treat as headless; macOS GUI doesn't use `DISPLAY`).
  - Windows: always treated as having a display.
- If headless detected before rendering, `matplotlib.use("Agg")` is set in `output.py` before any drawing.
- File format inferred from `--output` extension: `.png`, `.svg`, `.pdf`. Unknown extension → `OutputError`.
- Fallback path when `-o` is omitted: `./<csvstem>-<charttype>.png` (csvstem comes from `Path(input_path).stem`; for stdin input, use `stdin-<charttype>.png`).

## 7. Error handling

Hierarchy in `csvviz/exceptions.py`:

```
CsvvizError              # base
├── InvalidColumnError   # -x foo but no 'foo' column
├── ConflictingFlagsError # e.g. --normalized without -c
├── EmptyDataError       # CSV has no rows or no columns
└── OutputError          # bad extension, unwritable path
```

`cli.py` wraps each subcommand body in a single try/except:
- `CsvvizError` → print message to stderr, exit 1, no traceback.
- Any other `Exception` → re-raise if `CSVVIZ_DEBUG=1`, else print one-liner to stderr, exit 2.
- Click's own validation errors keep default behavior (exit 2, usage hint).

## 8. Testing

Mirrors the architecture.

- `tests/test_specs.py` — Spec construction and cross-field validation. Fast, no rendering.
- `tests/test_data.py` — CSV loading from file and stdin, column resolution, `InvalidColumnError` on bad references.
- `tests/test_cli.py` — Click's `CliRunner` end-to-end. Asserts exit codes, error messages on stderr, that an output PNG exists and is non-empty. Always uses `--no-show -o tmpfile.png` to stay headless.
- `tests/test_renderer_matplotlib.py` — Calls each renderer method directly, asserts the returned `Figure` has expected number of axes, title, etc. No image diffing in v0.5 (too brittle); we test structure, not pixels.

Fixtures: a subset of the old `examples/` CSVs copied to `tests/fixtures/` (`tings.csv`, `stocks.csv`, one heatmap-shaped CSV).

`pytest.ini` calls `matplotlib.use("Agg")` at session start so no windows pop up during the test run.

Coverage target: every chart type has at least one happy-path test and one "bad column" test.

## 9. Project layout & dependencies

```
csvviz-project/
├── csvviz/
│   ├── __init__.py          # __version__ = "0.5.0"
│   ├── cli.py
│   ├── specs.py
│   ├── data.py
│   ├── output.py
│   ├── exceptions.py
│   └── renderers/
│       ├── __init__.py
│       ├── base.py
│       └── matplotlib_renderer.py
├── tests/
│   ├── fixtures/
│   │   ├── tings.csv
│   │   ├── stocks.csv
│   │   └── ...
│   ├── test_specs.py
│   ├── test_data.py
│   ├── test_cli.py
│   └── test_renderer_matplotlib.py
├── examples/                # useful subset copied from old-csvviz/examples/
├── pyproject.toml
├── README.md
└── .gitignore
```

**`pyproject.toml`** (PEP 621):
- Python: `>=3.10` (clean union syntax, `Literal`, `match`)
- Runtime: `click>=8.1`, `pandas>=2.0`, `matplotlib>=3.7`, `seaborn>=0.13`
- Dev: `pytest>=8`, `black>=24`
- Entry point: `csvviz = "csvviz.cli:cli"`

## 10. Deferred / out of scope (v0.6+)

- `--annotate` for heatmap (cell value labels) — needs rethinking
- `--cmap` for heatmap — overlaps with `--palette`, naming needs design
- Streamgraph (`stream` subcommand)
- `info` subcommand (list palettes/themes)
- PNG-to-stdout pipe-friendly mode
- Multi-input / data transforms
- Vega-Lite renderer (the swappable-backend payoff)
