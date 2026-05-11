from pathlib import Path

import pandas as pd
import pytest
from matplotlib.figure import Figure

from csvviz.data import load_csv
from csvviz.renderers.matplotlib_renderer import MatplotlibRenderer
from csvviz.specs import AreaSpec, BarSpec, HistSpec, LineSpec, ScatterSpec

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def renderer():
    return MatplotlibRenderer()


def _load(spec):
    return load_csv(spec)


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
    assert isinstance(fig, Figure)


def test_render_bar_with_dimensions(renderer):
    spec = BarSpec(input_path=str(FIXTURES / "tings.csv"), width_px=800, height_px=400)
    df = _load(spec)
    fig = renderer.render_bar(spec, df)
    w, h = fig.get_size_inches()
    assert abs(w - 8.0) < 0.01
    assert abs(h - 4.0) < 0.01


def test_render_bar_stacked_requires_colorvar_in_data(renderer, tmp_path):
    p = tmp_path / "stack.csv"
    p.write_text("month,product,sales\n" "Jan,A,10\n" "Jan,B,20\n" "Feb,A,15\n" "Feb,B,25\n")
    spec = BarSpec(input_path=str(p), xvar="month", yvar="sales", colorvar="product", stacked=True)
    df = _load(spec)
    fig = renderer.render_bar(spec, df)
    assert isinstance(fig, Figure)


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


def test_render_hist_returns_figure(renderer):
    spec = HistSpec(input_path=str(FIXTURES / "tings.csv"), xvar="amount", bins=5)
    df = _load(spec)
    fig = renderer.render_hist(spec, df)
    assert isinstance(fig, Figure)


def test_render_hist_cumulative(renderer):
    spec = HistSpec(input_path=str(FIXTURES / "tings.csv"), xvar="amount", cumulative=True)
    df = _load(spec)
    fig = renderer.render_hist(spec, df)
    assert isinstance(fig, Figure)


def test_render_area_single_series(renderer):
    spec = AreaSpec(input_path=str(FIXTURES / "stocks.csv"), xvar="date", yvar="price")
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
