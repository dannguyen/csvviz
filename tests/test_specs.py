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
