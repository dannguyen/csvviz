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

Faceting (`-f COL`) is supported for `bar`, `line`, `scatter`, and `hist`. `area` and `heatmap` raise an error if faceted in v0.5.

## Development

```bash
pip install -e ".[dev]"
pytest
black csvviz tests
```
