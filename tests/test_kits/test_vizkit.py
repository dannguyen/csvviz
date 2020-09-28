import pytest
from csvviz.vizkit import Vizkit, lookup_mark_method
from csvviz.cmds.scatter import Scatterkit

import altair as alt
import pandas as pd


@pytest.fixture
def tvk():
    SRC_PATH = "examples/tings.csv"
    return Vizkit(
        input_file=SRC_PATH,
        kwargs={
            "xvar": "name",
            "yvar": "amount",
            "fillvar": "name",
            "is_interactive": True,
            "no_preview": True,
            "to_json": True,
        },
    )


@pytest.fixture
def dotvk():
    SRC_PATH = "examples/vals.csv"
    return Scatterkit(
        input_file=SRC_PATH,
        kwargs={
            "xvar": "mass",
            "yvar": "volume",
            "fillvar": "breed",
            "is_interactive": True,
            "no_preview": True,
            "to_json": True,
        },
    )


def test_vizkit_basic_init(tvk):
    assert isinstance(tvk, Vizkit)
    assert isinstance(tvk.chart, alt.Chart)


def test_vizkit_properties(tvk, dotvk):
    assert tvk.viz_type == "abstract"
    assert tvk.mark_type == "mark_bar"
    assert isinstance(tvk.df, pd.DataFrame)
    assert tvk.column_names == ["name", "amount"]

    assert dotvk.name == "scatter"
    assert dotvk.mark_type == "mark_point"


def test_vizkit_unneeded_properties_to_deprecate(tvk):
    assert tvk.name == "abstract"  # maybe viz_type isn't needed?


def test_vizkit_kwarg_properties(tvk):
    """
    these internal helpers copy from self.kwargs
    """

    #    import pdb; pdb.set_trace()
    assert tvk.channel_kwargs["xvar"] == "name"
    assert tvk.channel_kwargs["yvar"] == "amount"
    assert tvk.channel_kwargs["fillvar"] == "name"

    assert tvk.output_kwargs["to_json"] is True
    assert tvk.output_kwargs["no_preview"] is True

    # duh:
    assert tvk.color_kwargs["colors"] is None
    assert tvk.color_kwargs["color_scheme"] is None


@pytest.mark.skip(reason="TODO")
def test_vizkit_declarations(tvk):
    pass
    # assert isinstance(tvk.prepare_channels['x'], alt.X)
    # assert isinstance(tvk.prepare_channels['fill'], alt.Fill)

    # assert tvk.declare_legend['orient'] == DEFAULT_LEGEND_ORIENTATION
    # assert tvk.declare_legend['title'] == 'name'
    # assert tvk.declare_output['to_json'] is True


###################################################################################
# chart building
###################################################################################
def test_vizkit_chart_basic(tvk):
    chart = tvk.chart
    vega = chart.to_dict()
    assert "selection" in vega  # because of is_interactive

    # import pdb; pdb.set_trace()
    assert vega["mark"]["type"] == "bar"
    assert vega["mark"]["clip"] is True

    assert vega["encoding"]["y"]["field"] == "amount"
    assert vega["encoding"]["fill"]["field"] == "name"


def test_vizkit_output_basic(tvk, capsys):
    tvk.output_chart()
    outs = capsys.readouterr().out
    assert "{" == outs.splitlines()[0]
    assert '"amount": 20' in outs
    assert '"type": "bar"' in outs
    assert '"$schema"' in outs


#####################################
# get_chart_methodname
#####################################
def test_lookup_mark_method():
    assert "mark_bar" == lookup_mark_method("bar")
    assert "mark_line" == lookup_mark_method("line")
    assert "mark_point" == lookup_mark_method("scatter")
