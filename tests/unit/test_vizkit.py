import pytest

import altair as alt
from io import StringIO
import json
import pandas as pd
from pathlib import Path

from csvviz.settings import *
from csvviz.vizkit import Vizkit
from csvviz.vizkit.chart import Chart
from csvviz.vizzes.scatter import Scatterkit

from csvviz.helpers import parse_delimited_str

SRC_PATH = "examples/tings.csv"


@pytest.fixture
def tvk():
    opts = {
        "xvar": "name",
        "yvar": "amount",
        "fillvar": "name",
        "is_interactive": True,
        "no_preview": True,
        "to_json": True,
        "color_list": "red,white,blue",
    }
    return Vizkit(input_file=SRC_PATH, options=opts)


@pytest.fixture
def bare():
    opts = {
        "xvar": "name",
        "yvar": "amount",
    }
    return Vizkit(input_file=SRC_PATH, options=opts)


def test_vizkit_basic_init(bare):
    assert isinstance(bare, Vizkit)
    assert isinstance(bare.chart, Chart)
    # raw_chart is used for handing off to an external process like browser opening
    assert isinstance(bare.raw_chart, alt.Chart)
    assert bare.filename == Path(SRC_PATH).name  # i.e. tings.csv


def test_vizkit_unneeded_properties_to_deprecate(bare):
    assert bare.name == "abstract"  # maybe viz_commandname isn't needed?


def test_vizkit_bare_defaults(bare):
    assert isinstance(bare.options, dict)
    assert bare.options.get("xvar") == "name"
    assert bare.options.get("yvar") == "amount"
    # these are self evident...note that vizkit.__init__ does not yet
    # whitelist what gets sent into "options"...maybe it should TKTK
    assert bare.options.get("color_list") is None
    assert bare.options.get("color_scheme") is None

    # these 2 options are False/True only when the click interface passes in
    # the kwargs...
    assert bare.options.get("to_json") is None
    assert bare.options.get("no_preview") is None


@pytest.mark.curious(
    "this test is basically pointless, as options arg is NOT whitelisted"
)
def test_vizkit_get_specified_options(tvk):
    """
    these internal helpers copy from self.options
    """
    #    import pdb; pdb.set_trace()
    assert tvk.options.get("fillvar") == "name"
    assert tvk.options.get("to_json") is True
    assert tvk.options.get("no_preview") is True
    assert tvk.options.get("color_list") == "red,white,blue"


def test_vizkit_chart_dict(tvk):
    d = tvk.chart_dict()
    assert isinstance(d, dict)


def test_vizkit_chart_json(tvk):
    j = tvk.chart_json()

    assert isinstance(j, str)
    assert json.loads(j) == tvk.chart_dict()


@pytest.mark.curious(
    "exists only to confirm that Vizkit.is_faceted is actually in Vizkit.chart.is_faceted"
)
def test_vizkit_is_faceted_prop_belongs_to_its_chart():
    opts = {
        "xvar": "name",
        "yvar": "amount",
        "facetvar": "name",
    }
    v = Vizkit(input_file=SRC_PATH, options=opts)
    assert v.chart.is_faceted is True


###################################################################################
# chart building
###################################################################################
def test_vizkit_chart_bare_defaults(bare):
    """
    basically, testing that the chart object meets expected spec and
     has our expected defaults
    """
    d = bare.chart_dict()
    # make sure data is there
    assert d["data"]["name"] in d["datasets"]
    # default chart props
    assert d["mark"]["clip"] is True
    assert "type" in d["mark"]
    assert all(
        c in d["encoding"]
        for c in (
            "x",
            "y",
        )
    )


@pytest.mark.curious(
    "should refactor this...and well, this entire test suite and its fixtures..."
)
def test_vizkit_chart_fill_set_and_color_list(tvk):
    """prereq: vizkit.options includes 'color_list' => 'str,str,str'"""
    d = tvk.chart_dict()
    e = d["encoding"]["fill"]
    assert e["field"] == "name"
    assert e["scale"]["range"] == ["red", "white", "blue"]
    # this should be its own test
    assert isinstance(e["legend"], dict)


@pytest.mark.curious("also tested in test_chart_properties...")
@pytest.mark.curious(
    "exists only to confirm that Vizkit.interactive_mode is actually in Vizkit.chart.interactive_mode"
)
def test_vizkit_chart_interactive_mode_ie_option_is_interactive(tvk):
    """
    selection is set when is_interactive option is set to True
    "selection": {
        "selector001": {
          "bind": "scales",
          "encodings": [
            "x",
            "y"
          ],
          "type": "interval"
        }
      }
    """
    assert tvk.chart.interactive_mode is True
    d = tvk.chart_dict()
    sel = list(d["selection"].keys())[0]
    assert "selector" in sel
    s = d["selection"][sel]
    assert isinstance(s, dict)
    assert s["type"] == "interval"
    assert s["bind"] == "scales"
    assert s["encodings"] == ["x", "y"]


@pytest.mark.curious(reason="This is basically covered in test_viz_chart_bare_defaults")
def test_vizkit_chart_basic(tvk):
    chart = tvk.chart
    vega = tvk.chart_dict()
    assert "selection" in vega  # because of is_interactive

    # import pdb; pdb.set_trace()
    assert vega["mark"]["type"] == "bar"
    assert vega["mark"]["clip"] is True

    assert vega["encoding"]["y"]["field"] == "amount"
    assert vega["encoding"]["fill"]["field"] == "name"


def test_vizkit_output_chart_basic(tvk, capsys):
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
    s = Vizkit(
        input_file=data,
        options=options,
    )
    assert s.channels["y"]["field"] == "Hello|World"
    assert s.channels["y"]["title"] == "hey|world"

    # as of now, input_file is supposed to be a Path/str, but
    # in the edge case that it isn't like for testing, filename needs
    # to be something...
    assert s.filename == "[input]"
