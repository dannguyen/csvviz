import pytest
import altair as alt
import pandas as pd

from csvviz.vizkit.channel_group import ChannelGroup

# parse_channel_arg
@pytest.fixture
def parsefoo():
    return ChannelGroup.parse_channel_arg


def test_parse_channel_arg_default_name(parsefoo):
    assert parsefoo("id") == ("id", None)
    assert parsefoo("id|") == ("id", None)
    assert parsefoo("sum(thing)|") == ("sum(thing)", None)


def test_parse_channel_arg_specified_name(parsefoo):
    assert parsefoo("id|Foo") == ("id", "Foo")
    assert parsefoo("sum(thing)|Bar") == ("sum(thing)", "Bar")


@pytest.fixture
def mydata():
    return pd.DataFrame(
        [
            {"name": "Alice", "amount": 10, "category": "cat"},
            {"name": "Bob", "amount": 20, "category": "dog"},
        ]
    )


def test_shorthand_typecodes(mydata):
    opts = {
        "xvar": "name",
        "yvar": "amount:O",
        "fillvar": "max(amount)",
        "sizevar": "mean(amount):O",
    }
    cg = ChannelGroup(opts, mydata)

    assert cg == {
        "x": alt.X(**{"field": "name", "type": "nominal"}),
        "y": alt.Y(**{"field": "amount", "type": "ordinal"}),
        "fill": alt.Fill(
            **{
                "field": "amount",
                "type": "quantitative",
                "aggregate": "max",
            }
        ),
        "size": alt.Size(
            **{
                "field": "amount",
                "type": "ordinal",
                "aggregate": "mean",
            }
        ),
    }


def test_titled_vars(mydata):
    opts = {
        "xvar": "name",
        "yvar": "amount:O|The Amount",
        "fillvar": "category|Cats",
        "sizevar": "mean(amount):O| Big Ups!",
    }
    cg = ChannelGroup(opts, mydata)

    assert cg == {
        "x": alt.X(**{"field": "name", "type": "nominal"}),
        "y": alt.Y(
            **{
                "field": "amount",
                "title": "The Amount",
                "type": "ordinal",
            }
        ),
        "fill": alt.Fill(
            **{
                "field": "category",
                "title": "Cats",
                "type": "nominal",
            }
        ),
        "size": alt.Size(
            **{
                "field": "amount",
                "type": "ordinal",
                "aggregate": "mean",
                "title": " Big Ups!",
            }
        ),
    }
