import pytest
import altair as alt
import pandas as pd

from csvviz import altUndefined
from csvviz.exceptions import *
from csvviz.vizkit.channel_group import ChannelGroup
import csvviz.settings


@pytest.fixture
def mydata():
    return pd.DataFrame(
        [
            {"name": "Alice", "amount": 10, "category": "cat"},
            {"name": "Bob", "amount": 20, "category": "dog"},
        ]
    )


def test_colorize_default_color_schemes(mydata):
    # when fill is categorical (i.e. nominal) variable
    opts = {"xvar": "name", "yvar": "amount", "fillvar": "category"}
    cg = ChannelGroup(opts, mydata, color_channel_name="fill")
    assert cg["fill"].scale == alt.Scale(
        scheme=csvviz.settings.DEFAULT_COLOR_SCHEMES["category"]
    )

    # when fill is quantitative variable
    opts = {"xvar": "name", "yvar": "amount", "fillvar": "amount:Q"}
    cg = ChannelGroup(opts, mydata, color_channel_name="fill")
    assert cg["fill"].scale == alt.Scale(
        scheme=csvviz.settings.DEFAULT_COLOR_SCHEMES["ramp"]
    )


def test_only_specified_color_channel_gets_scale(mydata):
    opts = {
        "xvar": "name",
        "yvar": "amount",
        "fillvar": "category",
        "strokevar": "category",
    }
    cg = ChannelGroup(opts, mydata, color_channel_name="stroke")
    assert cg["stroke"].scale is not altUndefined
    assert cg["fill"].scale is altUndefined


def test_colorize_with_color_list(mydata):
    opts = {
        "xvar": "name",
        "yvar": "amount",
        "fillvar": "category",
        "strokevar": "category",
        "color_list": "red,blue",
    }
    cg = ChannelGroup(opts, mydata, color_channel_name="fill")
    assert cg["fill"].scale == alt.Scale(range=["red", "blue"])


def test_colorize_with_color_scheme(mydata):
    opts = {
        "xvar": "name",
        "yvar": "amount",
        "fillvar": "category",
        "color_scheme": "brownbluegreen-10",
    }
    cg = ChannelGroup(opts, mydata, color_channel_name="fill")
    assert cg["fill"].scale == alt.Scale(scheme="brownbluegreen-10")
