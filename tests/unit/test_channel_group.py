import pytest
import altair as alt
import pandas as pd

from csvviz.exceptions import *
from csvviz.vizkit.channel_group import ChannelGroup


@pytest.fixture
def mydata():
    return pd.DataFrame(
        [
            {"name": "Alice", "amount": 10, "category": "cat"},
            {"name": "Bob", "amount": 20, "category": "dog"},
        ]
    )


def test_basic(mydata):
    kargs = {"xvar": "name", "yvar": "amount"}
    cg = ChannelGroup(mydata, kargs)
    assert cg.channels == {
        "x": alt.X(**{"field": "name", "type": "nominal"}),
        "y": alt.Y(
            **{
                "field": "amount",
                "type": "quantitative",
            }
        ),
    }

    fargs = {
        "xvar": "name",
        "yvar": "amount",
        "fillvar": "category",
        "sizevar": "name",
        "strokevar": "amount",
    }
    assert ChannelGroup(mydata, fargs).channels == {
        "x": alt.X(**{"field": "name", "type": "nominal"}),
        "y": alt.Y(
            **{
                "field": "amount",
                "type": "quantitative",
            }
        ),
        "fill": alt.Fill(
            **{
                "field": "category",
                "type": "nominal",
            }
        ),
        "size": alt.Size(**{"field": "name", "type": "nominal"}),
        "stroke": alt.Stroke(
            **{
                "field": "amount",
                "type": "quantitative",
            }
        ),
    }


def test_shorthand_typecodes(mydata):
    args = {
        "xvar": "name",
        "yvar": "amount:O",
        "fillvar": "max(amount)",
        "sizevar": "mean(amount):O",
    }
    cg = ChannelGroup(mydata, args)

    assert cg.channels == {
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
    args = {
        "xvar": "name",
        "yvar": "amount:O|The Amount",
        "fillvar": "category|Cats",
        "sizevar": "mean(amount):O| Big Ups!",
    }
    cg = ChannelGroup(mydata, args)

    assert cg.channels == {
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




def test_error_for_invalid_fieldname(mydata):
    args = {"xvar": "name", "yvar": 'WRONG'}
    with pytest.raises(InvalidDataReference) as e:
        cg = ChannelGroup(mydata, args)

