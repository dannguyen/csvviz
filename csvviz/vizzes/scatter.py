"""
scatter.py
"""
from pathlib import Path

import altair as alt
import click

from csvviz.exceptions import *
from csvviz.vizkit import Vizkit


class Scatterkit(Vizkit):
    viz_commandname = "scatter"
    help_info = f"""A scatterplot for showing relationship between two independent variables x and y. Set -s/--sizevar to create a bubble (variable dot size) chart"""
    help_epilog = (
        """Example:  $ csvviz scatter -x mass -y volume -s velocity data.csv"""
    )
    color_channel_name = "fill"

    COMMAND_DECORATORS = (
        click.option(
            "--xvar",
            "-x",
            type=click.STRING,
            help="The name of the column for mapping x-axis values; if empty, the first (columns[0]) column is used",
        ),
        click.option(
            "--yvar",
            "-y",
            type=click.STRING,
            help="The name of the column for mapping y-axis values; if empty, the second (columns[1]) column is used",
        ),
        click.option(
            "--colorvar",
            "-c",
            "colorvar",
            type=click.STRING,
            help="The name of the column for mapping dot colors. This is required for creating a multi-series scatter chart.",
        ),
        click.option(
            "--sizevar",
            "-s",
            "sizevar",
            type=click.STRING,
            help="The name of the column for mapping dot size. This effectively creates a bubble chart.",
        ),
    )

    def finalize_channels(self, channels):
        return channels

    def validate_options(self, options: dict) -> bool:
        super().validate_options(options)
        return True
