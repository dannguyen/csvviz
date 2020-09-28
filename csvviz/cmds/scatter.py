"""
scatter.py
"""
from pathlib import Path

import altair as alt
import click
from csvviz.cli_utils import clout, clerr, clexit
from csvviz.cli_utils import standard_options_decor

from csvviz.exceptions import *
from csvviz.vizkit import Vizkit


class Scatterkit(Vizkit):
    viz_type = "scatter"

    def prepare_channels(self):
        channels = self._channels_init(self.channel_kwargs)
        if channels.get("fill"):
            channels["fill"].scale = alt.Scale(**self._config_colors(self.color_kwargs))

        return channels

    COMMAND_DECORATORS = (
        click.option(
            "--xvar", "-x", type=click.STRING, default="", help="the label column"
        ),
        click.option(
            "--yvar", "-y", type=click.STRING, default="", help="the value column"
        ),
        click.option(
            "--fill",
            "-f",
            "fillvar",
            type=click.STRING,
            help="The column used to specify fill color",
        ),
        click.option(
            "--size",
            "-s",
            "sizevar",
            type=click.STRING,
            help="The column used to specify dot size",
        ),
    )
