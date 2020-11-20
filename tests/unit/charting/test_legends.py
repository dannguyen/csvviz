import pytest

import altair as alt
import pandas as pd
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
