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
    viz_info = f"""A line chart TK"""

    def prepare_channels(self):
        channels = self._create_channels(self.channel_kwargs)
        return channels

    COMMAND_DECORATORS = (
        click.option(
            "--xvar", "-x", type=click.STRING, default="", help="the label column"
        ),
        click.option(
            "--yvar", "-y", type=click.STRING, default="", help="the value column"
        ),
        click.option(
            "--color",
            "-c",
            "strokevar",
            type=click.STRING,
            help="The column used to specify stroke color",
        ),
    )
