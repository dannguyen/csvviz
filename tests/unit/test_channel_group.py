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


def test_facetize_basic(mydata):
    opts = {
        "xvar": "name",
        "yvar": "amount",
        "facetvar": "category",
    }
    cg = ChannelGroup(opts, mydata)
    defaults = {
        "field": "category",
        "type": "nominal",
        "columns": csvviz.settings.DEFAULT_FACET_COLUMNS,
        "spacing": csvviz.settings.DEFAULT_FACET_SPACING,
    }
    assert cg["facet"] == alt.Facet(**defaults)


def test_facetize_with_opts(mydata):
    opts = {
        "xvar": "name",
        "yvar": "amount",
        "facetvar": "category",
        "facet_columns": 5,
        "facet_sort": "desc",
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
        color_channel_name="fill",
    )
    assert cg["fill"].legend == alt.Legend(
        orient=csvviz.settings.DEFAULT_LEGEND_ORIENTATION
    )
    assert cg["size"].legend == alt.Legend(
        orient=csvviz.settings.DEFAULT_LEGEND_ORIENTATION
    )


@pytest.mark.curious(
    "legend disabling is also tested at the vizkit(options={}).chart level..."
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
        color_channel_name="fill",
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


# get_data_field
def test_get_data_field(mydata):
    opts = {
        "xvar": "name",
        "yvar": "amount",
        "sizevar": "amount:O",
        "fillvar": "category|Cats!",
        "strokevar": "sum(amount)",
    }
    cg = ChannelGroup(opts, mydata)
    assert cg.get_data_field("x") == "name"
    assert cg.get_data_field("y") == "amount"
    assert cg.get_data_field("size") == "amount"
    assert cg.get_data_field("fill") == "category"  # title is ignored
    assert (
        cg.get_data_field("stroke") == "amount"
    )  # ignore aggregate function (for now)
