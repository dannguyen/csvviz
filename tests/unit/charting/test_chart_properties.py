"""
Basically more specific tests vs test_chart.py

These tests are isolated from CliRunner, i.e. does not show integrated cli output

They are mostly isolated from Vizkit...depends on (mocked) Vizkit.viz_commandname and chart_defaults()

They are mostly isolated from ChannelGroup...depends on:
    - channels['facet'] for is_faceted
"""

import pytest

import altair as alt
import pandas as pd
from pathlib import Path
from typing import Dict as DictType

from csvviz.exceptions import *
import csvviz.settings
from csvviz.vizkit.chart import Chart
from csvviz.vizkit.channel_group import ChannelGroup

INPUT_PATH = "examples/fruits.csv"

SETUP_OPTS = {
    "xvar": "product",
    "yvar": "revenue",
    "colorvar": "season",
}
MOCK_COMMAND_NAME = "bar"
MOCK_DEFAULTS = {
    "chart_height": 2000,
    "chart_width": 1000,
    "faceted_height": 420,
    "faceted_width": 240,
}


def setup_viz(options={}) -> Chart:
    opts = SETUP_OPTS.copy()
    opts.update(options)
    dataframe = pd.read_csv(INPUT_PATH)
    channels = ChannelGroup(options=opts, data=dataframe, color_channel_name="fill")

    return Chart(
        viz_name=MOCK_COMMAND_NAME,
        channels=channels,
        data=dataframe,
        defaults=MOCK_DEFAULTS,
        options=opts,
    )


def chartprops(options={}) -> DictType:
    return setup_viz(options).to_dict()


def test_chart_and_chart_defaults():
    """
    Chart defaults should be equal to Vizkit.chart_defaults()
    """
    p = chartprops()
    assert "title" not in p
    assert p["height"] == MOCK_DEFAULTS["chart_height"]
    assert p["width"] == MOCK_DEFAULTS["chart_width"]
    assert p["autosize"] == {
        "type": "pad",
        "contains": "padding",
    }


@pytest.mark.curious("this should be deprecated/fixed or whatever later TK")
def test_chart_default_config():
    p = chartprops()
    assert p["config"]["view"] == {"continuousWidth": 400, "continuousHeight": 300}


##############################################################################################################
# chart style properties
##############################################################################################################
def test_set_title():
    p = chartprops({"title": "My Title"})
    assert p["title"] == "My Title"


def test_set_width_height():
    p = chartprops({"height": 42, "width": 100})
    assert p["width"] == 100
    assert p["height"] == 42


def test_set_auto_width_height():
    p = chartprops({"height": 0})
    assert p["height"] == 0
    assert p["width"] == MOCK_DEFAULTS["chart_width"]

    p = chartprops({"width": 0})
    assert p["height"] == MOCK_DEFAULTS["chart_height"]
    assert p["width"] == 0


#####################
# legend stuff
#####################
def test_chart_default_legend():
    p = chartprops({"colorvar": "season"})
    fill = p["encoding"]["fill"]
    assert fill["legend"]["orient"] == csvviz.settings.DEFAULT_LEGEND_ORIENTATION


@pytest.mark.curious(
    "legend disabling is also tested at the channel_group(options={}) level..."
)
def test_chart_disable_legend():
    """encoding's legend prop is explicitly set to None"""
    p = chartprops({"colorvar": "season", "no_legend": True})
    fill = p["encoding"]["fill"]
    assert fill["legend"] is None


##############################################################################################################
# chart style interactivity
##############################################################################################################
def test_is_interactive():
    p = chartprops({"is_interactive": True})
    sel = list(p["selection"].keys())[0]
    s = p["selection"][sel]
    assert isinstance(s, dict)
    assert s["type"] == "interval"
    assert s["bind"] == "scales"
    assert s["encodings"] == ["x", "y"]


def test_is_static():
    p = chartprops({"is_interactive": False})
    assert "selection" not in p
