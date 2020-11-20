import pytest
import altair as alt
import json
import pandas as pd

from csvviz.exceptions import *
from csvviz.vizkit.channel_group import ChannelGroup
from csvviz.vizkit.chart import Chart
from csvviz.vizkit import Vizkit
import csvviz.settings

"""
These tests are isolated from CliRunner, i.e. does not show integrated cli output

They are NOT isolated from Chart or ChannelGroup (see also test_leaks.y)

test_vizkit_is_leaky_to_chart::
Has a dependency on Vizkit/Barkit, but mostly to make sure shared attributes are properly reflected:
    - chart.viz_name == Vizkit.viz_commandname
    - including the sloppy sharing of `options`, that is, that Vizkit(options) gets passed all
        the way down to Chart(options)
"""

VIZKIT = Vizkit
VIZ_NAME = VIZKIT.viz_commandname

SRC_PATH = "examples/fruits.csv"


@pytest.fixture
def mydata():
    return pd.DataFrame(
        [
            {
                "name": "Alice",
                "amount": 10,
                "category": "cat",
                "season": "fall",
            },
            {
                "name": "Bob",
                "amount": 20,
                "category": "dog",
                "season": "winter",
            },
        ]
    )


@pytest.fixture
def mychannels(mydata):
    opts = {
        "xvar": "name",
        "yvar": "category",
        "fillvar": "season",
        "strokevar": "category",
    }
    return ChannelGroup(opts, mydata, color_channel_name="fill")


@pytest.fixture
def bchart(mydata, mychannels):
    c = Chart(
        viz_name=VIZ_NAME,
        data=mydata,
        channels=mychannels,
        defaults=Vizkit.chart_defaults(),
    )
    return c


def test_dataful(bchart):
    assert isinstance(bchart.df, pd.DataFrame)
    bchart.column_names == ["name", "amount", "category", "season"]


def test_to_dict(bchart):
    d = bchart.to_dict()
    assert isinstance(d, dict)
    assert isinstance(d["encoding"], dict)
    assert d["mark"]["type"] == bchart.mark_name


def test_to_json(bchart):
    j = bchart.to_json()
    assert isinstance(j, str)
    assert "{\n" == j[0:2]
    assert json.loads(j) == bchart.to_dict()


def test_has_no_global_config(bchart):
    """
    as a result of `alt.themes.enable('none')`, global config should
    not be present
    """
    d = bchart.to_dict()
    assert "config" not in d


def test_basic_construction(bchart):
    assert isinstance(bchart, Chart)
    assert isinstance(bchart.channels, ChannelGroup)
    assert isinstance(bchart.raw_chart, alt.Chart)
    assert not isinstance(bchart, alt.Chart)

    assert bchart.viz_name == VIZ_NAME


def test_basic_marky(bchart):
    assert bchart.viz_name == VIZ_NAME == "abstract"
    assert bchart.mark_name == "bar"
    assert bchart.mark_method_name == "mark_bar"


def test_bchart_defaults(bchart):
    bchart.interactive_mode is True
    bchart.is_faceted is False


def test_bchart_channels(bchart):
    """kind of pointless"""
    assert bchart.channels["x"].field == "name"
    assert bchart.channels["y"].field == "category"
    assert bchart.channels["fill"].field == "season"
    assert bchart.channels["stroke"].field == "category"


#####################################
# get_chart_methodname
#####################################
def test_lookup_mark_name():
    foo = Chart.lookup_mark_name
    assert foo("abstract") == "bar"
    assert foo("area") == "area"
    assert foo("bar") == "bar"
    assert foo("heatmap") == "rect"
    assert foo("hist") == "bar"
    assert foo("line") == "line"
    assert foo("scatter") == "point"
    assert foo("stream") == "area"
