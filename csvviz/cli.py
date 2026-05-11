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
        click.option(
            "-H", "--height", "height_px", type=int, default=None, help="height in pixels"
        ),
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
    """Extract BaseSpec kwargs from Click's kwargs dict (mutates kw)."""
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
    spec = BarSpec(**base, horizontal=horizontal, stacked=stacked, normalized=normalized, sort=sort)
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
