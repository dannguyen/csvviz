"""
copied over from test_chart

Basically, a place to document the ad-hoc leaky abstraction between what should be separated classes
and encapsulation. These tests should properly break when I properly decouple classes
"""

import pytest
import altair as alt
import json
import pandas as pd
from csvviz.exceptions import *
from csvviz.vizkit.channel_group import ChannelGroup
from csvviz.vizkit.chart import Chart
from csvviz.vizkit import Vizkit
import csvviz.settings


VIZKIT_KLASS = Vizkit
VIZKIT_NAME = "abstract"
SRC_PATH = "examples/fruits.csv"


RAW_OPTS = {
    "xvar": "product",
    "yvar": "revenue",
    "colorvar": "season",
    "facetvar": "region",
}


@pytest.fixture
def vk() -> VIZKIT_KLASS:
    vk = VIZKIT_KLASS(input_file=SRC_PATH, options=RAW_OPTS)
    return vk


@pytest.mark.curious(
    "TK: should be testing vizkit.set_default_channels_and_options in test_vizkit.py"
)
def test_vizkit_sets_default_channels_in_options_which_are_passed_to_chart():
    dk = VIZKIT_KLASS(input_file=SRC_PATH, options={})
    c = dk.chart
    assert dk.options["xvar"] == c.options["xvar"] == "product"
    assert dk.options["yvar"] == c.options["yvar"] == "revenue"
    # assert dk.options['chart_title'] == c.options['chart_title'] == 'fruits.csv'


@pytest.mark.curious(
    "basically an integration test...it exists to break when i do future decoupling of Vizkit and Chart"
)
def test_chart_has_leaky_relation_to_vizkit_and_channel_group(vk):
    """fragile, canary test!"""

    chart = vk.chart
    # Vizkit passes raw_chart to things that need an alt.Chart
    assert chart.raw_chart == vk.raw_chart
    # sharing
    ## lol wtf is this
    assert (
        chart.viz_name
        == vk.viz_name
        == vk.viz_commandname
        == VIZKIT_KLASS.viz_commandname
    )
    # shares options
    assert chart.options == vk.options
    # shares helpers
    assert chart.to_dict() == vk.chart_dict()
    assert chart.to_json() == vk.chart_json()
    # shares channels
    assert chart.channels == vk.channels
    # chart doesn't use options['colorvar/facetvar']; instead, it only depends on its own channels
    assert chart.is_faceted and vk.channels["facet"]
    assert chart.channels["fill"]["field"] == RAW_OPTS["colorvar"]
    # shares defaults
    assert chart.defaults["chart_height"] == vk.chart_defaults()["chart_height"]
    assert chart.defaults["faceted_height"] == vk.chart_defaults()["faceted_height"]


def test_chart_leaky_relations_to_channel_group(vk):
    chart = vk.chart
    channels = chart.channels
    assert chart.options == channels.options
