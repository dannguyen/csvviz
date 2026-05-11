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
