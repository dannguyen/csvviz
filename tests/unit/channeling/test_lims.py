import pytest
import altair as alt
import pandas as pd

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


@pytest.mark.curious(
    "this is non-sensical and a user error, but silently fail for now..."
)
def test_xlim(mydata):
    opts = {
        "xvar": "name",
        "yvar": "amount",
        "xlim": "-20,42",
    }
    cg = ChannelGroup(opts, mydata)
    assert cg["x"]["scale"]["domain"] == ["-20", "42"]


def test_ylim(mydata):
    opts = {
        "xvar": "name",
        "yvar": "amount",
        "ylim": "-10,30",
    }
    cg = ChannelGroup(opts, mydata)
    assert cg["y"]["scale"]["domain"] == ["-10", "30"]
