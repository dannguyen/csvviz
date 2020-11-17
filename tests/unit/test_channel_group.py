import pytest
import altair as alt
import pandas as pd

from csvviz.exceptions import *
from csvviz.vizkit.channel_group import ChannelGroup, altUndefined
import csvviz.settings


@pytest.fixture
def mydata():
    return pd.DataFrame(
        [
            {"name": "Alice", "amount": 10, "category": "cat"},
            {"name": "Bob", "amount": 20, "category": "dog"},
        ]
    )


def test_basic(mydata):
    cg = ChannelGroup({}, mydata)
    assert isinstance(cg, dict)
    assert isinstance(cg.df, pd.DataFrame)


def test_vars_to_channels(mydata):
    kopts = {"xvar": "name", "yvar": "amount"}
    cg = ChannelGroup(kopts, mydata)
    assert cg == {
        "x": alt.X(**{"field": "name", "type": "nominal"}),
        "y": alt.Y(
            **{
                "field": "amount",
                "type": "quantitative",
            }
        ),
    }

    fopts = {
        "xvar": "name",
        "yvar": "amount",
        "fillvar": "category",
        "sizevar": "name",
        "strokevar": "amount",
    }
    assert ChannelGroup(fopts, mydata) == {
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


def test_colorize_default_color_scheme(mydata):
    opts = {"xvar": "name", "yvar": "amount", "fillvar": "category"}
    cg = ChannelGroup(opts, mydata, color_channel="fill")
    assert cg["fill"].scale == alt.Scale(scheme=csvviz.settings.DEFAULT_COLOR_SCHEME)


def test_only_specified_color_channel_gets_scale(mydata):
    opts = {
        "xvar": "name",
        "yvar": "amount",
        "fillvar": "category",
        "strokevar": "category",
    }
    cg = ChannelGroup(opts, mydata, color_channel="stroke")
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
    cg = ChannelGroup(opts, mydata, color_channel="fill")
    assert cg["fill"].scale == alt.Scale(range=["red", "blue"])


def test_colorize_with_color_scheme(mydata):
    opts = {
        "xvar": "name",
        "yvar": "amount",
        "fillvar": "category",
        "color_scheme": "brownbluegreen-10",
    }
    cg = ChannelGroup(opts, mydata, color_channel="fill")
    assert cg["fill"].scale == alt.Scale(scheme="brownbluegreen-10")


def test_facetize_basic(mydata):
    opts = {
        "xvar": "name",
        "yvar": "amount",
        "facetvar": "category",
    }
    cg = ChannelGroup(opts, mydata)
    assert cg["facet"] == alt.Facet(**{"field": "category", "type": "nominal"})


def test_facetize_with_opts(mydata):
    opts = {
        "xvar": "name",
        "yvar": "amount",
        "facetvar": "category",
        "facetcolumns": 5,
        "facetsort": "desc",
    }
    cg = ChannelGroup(opts, mydata)
    assert cg["facet"].columns == 5
    assert cg["facet"].sort == "descending"


def test_legendize_default(mydata):
    opts = {
        "xvar": "name",
        "yvar": "amount",
        "fillvar": "category",
        "sizevar": "amount",
    }
    cg = ChannelGroup(
        opts,
        mydata,
        color_channel="fill",
    )
    assert cg["fill"].legend == alt.Legend(
        orient=csvviz.settings.DEFAULT_LEGEND_ORIENTATION
    )
    assert cg["size"].legend == alt.Legend(
        orient=csvviz.settings.DEFAULT_LEGEND_ORIENTATION
    )


def test_legendize_disabled(mydata):
    opts = {
        "xvar": "name",
        "yvar": "amount",
        "fillvar": "category",
        "sizevar": "amount",
        "no_legend": True,
    }
    cg = ChannelGroup(
        opts,
        mydata,
        color_channel="fill",
    )
    assert cg["fill"].legend is None
    assert cg["size"].legend is None


def test_error_for_invalid_fieldname(mydata):
    opts = {"xvar": "name", "yvar": "WRONG"}
    with pytest.raises(InvalidDataReference) as e:
        cg = ChannelGroup(opts, mydata)

    assert (
        f"'WRONG' is either an invalid column name, or invalid Altair shorthand"
        in str(e.value)
    )


def test_error_for_invalid_shorthand(mydata):
    opts = {"xvar": "name", "yvar": "amount:H"}
    with pytest.raises(InvalidDataReference) as e:
        cg = ChannelGroup(opts, mydata)

    assert (
        f"'amount:H' is either an invalid column name, or invalid Altair shorthand"
        in str(e.value)
    )
