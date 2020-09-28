"""
scatter.py
"""
from pathlib import Path

import altair as alt
import click

from csvviz.exceptions import *
from csvviz.vizkit import Vizkit


class Scatterkit(Vizkit):
    viz_type = "scatter"
    viz_info = f"""A scatterplot for showing relationship between two independent variables x and y. Can vary by size and fill too. TK"""

    def prepare_channels(self):
        channels = self._create_channels(self.channel_kwargs)
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
