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
    viz_type = "line"
    viz_info = f"""A line chart"""
    # viz_epilog = (
    #     f"""Example:\t $ csvviz line -x date -y price -c company examples/stocks.csv"""
    # )

    def finalize_channels(self, channels):
        self._set_channel_colorscale("stroke", channels)
        return channels

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
            "strokevar",
            type=click.STRING,
            help="The name of the column for mapping line colors. This is required for creating a multi-series line chart.",
        ),
    )
