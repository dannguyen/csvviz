"""
line.py

$ csvviz line examples/stocks.csv  -x 'date:T' -y price -s company

$ csvviz line examples/tonk.csv --json -x date:T
"""

import altair as alt
import click
from csvviz.exceptions import *
from csvviz.vizkit import Vizkit


class Linekit(Vizkit):
    viz_commandname = "line"
    help_info = f"""A line chart"""
    # help_epilog = (
    #     f"""Example:\t $ csvviz line -x date -y price -c company examples/stocks.csv"""
    # )
    color_channel_name = "stroke"

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
            help="The name of the column for mapping line colors. This is required for creating a multi-series line chart.",
        ),
    )

    def finalize_channels(self, channels):
        return channels

    def validate_options(self, options: dict) -> bool:
        super().validate_options(options)
        return True
