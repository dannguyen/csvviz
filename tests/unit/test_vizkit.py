import pytest
from io import StringIO
import altair as alt
import pandas as pd


from csvviz.settings import *
from csvviz.vizkit import Vizkit
from csvviz.vizzes.scatter import Scatterkit

from csvviz.helpers import parse_delimited_str

# typically, these are set by Click default= args, which we don't have access to
# when looking at Vizkit

# TODO: messy hack for now, to manually update with REQUIRED_ARGS; maybe indication that
# tests/implementation is too brittle?
REQUIRED_ARGS = {
    # "chart_height": DEFAULT_CHART_HEIGHT,
    # "chart_width": DEFAULT_CHART_WIDTH,
}


@pytest.fixture
def tvk():
    SRC_PATH = "examples/tings.csv"
    options = {
        "xvar": "name",
        "yvar": "amount",
        "fillvar": "name",
        "is_interactive": True,
        "no_preview": True,
        "to_json": True,
    }
    options.update(REQUIRED_ARGS)
    return Vizkit(input_file=SRC_PATH, options=options)


def test_vizkit_basic_init(tvk):
    assert isinstance(tvk, Vizkit)
    assert isinstance(tvk.chart, alt.Chart)


def test_vizkit_properties(tvk):
    assert tvk.viz_commandname == "abstract"
    assert tvk.mark_method_name == "mark_bar"
    assert tvk.color_channel_name == "fill"
    assert isinstance(tvk.df, pd.DataFrame)
    assert tvk.column_names == ["name", "amount"]


def test_vizkit_unneeded_properties_to_deprecate(tvk):
    assert tvk.name == "abstract"  # maybe viz_commandname isn't needed?


def test_vizkit_kwarg_properties(tvk):
    """
    these internal helpers copy from self.options
    """
    #    import pdb; pdb.set_trace()
    assert tvk.options.get("xvar") == "name"
    assert tvk.options.get("yvar") == "amount"
    assert tvk.options.get("fillvar") == "name"
    assert tvk.options.get("to_json") is True
    assert tvk.options.get("no_preview") is True

    # duh:
    assert tvk.options.get("colors") is None
    assert tvk.options.get("color_scheme") is None


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


def test_parse_channel_arg_edge_case_vizkit_channels():
    """more of an integrated test than a unit one; makes sure Vizkit handles shorthand ok"""
    data = StringIO("id,Hello|World\nfoo,42\n")
    options = {
        "xvar": "id",
        "yvar": '"Hello|World"|"hey|world"',
    }
    options.update(REQUIRED_ARGS)
    s = Vizkit(
        input_file=data,
        options=options,
    )
    assert s.channels["y"]["field"] == "Hello|World"
    assert s.channels["y"]["title"] == "hey|world"


#####################################
# get_chart_methodname
#####################################
def test_lookup_mark_method():
    foo = Vizkit.lookup_mark_method
    assert "mark_area" == foo("area")
    assert "mark_bar" == foo("bar")
    assert "mark_bar" == foo("hist")
    assert "mark_line" == foo("line")
    assert "mark_point" == foo("scatter")
