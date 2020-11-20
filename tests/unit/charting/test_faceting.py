"""
Basically more specific tests vs test_chart.py

These tests are isolated from CliRunner, i.e. does not show integrated cli output

They are mostly isolated from Vizkit...depends on (mocked) Vizkit.viz_commandname and chart_defaults()

They are mostly isolated from ChannelGroup (created in setup())

Overlaps with test_channel_group.test_facetize and clicky/test_facet_flags,
    but more unit based
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


INPUT_PATH = "examples/jobless.csv"
SETUP_OPTS = {
    "xvar": "month:O",
    "yvar": "rate",
    "colorvar": "sector",
    "facetvar": "year:O",
}
MOCK_COMMAND_NAME = "line"
MOCK_DEFAULTS = {
    "chart_height": 666,
    "chart_width": 1000,
    "faceted_height": 420,
    "faceted_width": 240,
}


def setup_viz(options={}) -> Chart:
    opts = SETUP_OPTS.copy()
    opts.update(options)
    dataframe = pd.read_csv(INPUT_PATH)
    channels = ChannelGroup(options=opts, data=dataframe, color_channel_name="stroke")
    return Chart(
        viz_name=MOCK_COMMAND_NAME,
        channels=channels,
        data=dataframe,
        defaults=MOCK_DEFAULTS,
        options=opts,
    )


def chartprops(options={}) -> DictType:
    return setup_viz(options).to_dict()


# def vfoo(options=COMMON_OPTIONS, input_file=INPUT_PATH) -> Gkit:
#     return Gkit(input_file, options=options)


def test_chart_and_encoding_defaults():
    """
    Chart defaults should be equal to Vizkit.chart_defaults()
    """
    c = chartprops()
    assert c["resolve"] == {"axis": {"x": "independent"}}
    assert c["encoding"]["facet"] == {
        "field": "year",
        "type": "ordinal",
        "columns": csvviz.settings.DEFAULT_FACET_COLUMNS,
        "spacing": csvviz.settings.DEFAULT_FACET_SPACING,
    }

    assert c["height"] == MOCK_DEFAULTS["faceted_height"]
    assert c["width"] == MOCK_DEFAULTS["faceted_width"]
    assert c["autosize"] == {
        "type": "pad",
        "contains": "padding",
    }


def test_set_facet_columns():
    c = chartprops({"facet_columns": 42})
    assert c["encoding"]["facet"]["columns"] == 42


def test_set_ininite_facet_columns():
    c = chartprops({"facet_columns": 0})
    assert c["encoding"]["facet"]["columns"] is 0


def test_set_faceted_width_and_height():
    """no different in effect than non-faceted chart"""
    c = chartprops({"chart_height": 42, "chart_width": 100})
    assert c["width"] == 100
    assert c["height"] == 42


def test_set_facted_auto_width_height():
    """basically same as effect in non-faceted chart"""
    c = chartprops({"chart_height": 0})
    assert c["height"] == 0
    assert c["width"] == MOCK_DEFAULTS["faceted_width"]

    c = chartprops({"chart_width": 0})
    assert c["height"] == MOCK_DEFAULTS["faceted_height"]
    assert c["width"] == 0
