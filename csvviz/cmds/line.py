"""
line.py

$ csvviz line examples/stocks.csv  -x 'date:T' -y price -s company

$ csvviz line examples/tonk.csv --json -x date:T
"""

import altair as alt
import click
from csvviz.cli_utils import clout, clerr, clexit
from csvviz.cli_utils import standard_options_decor
from csvviz.exceptions import *
from csvviz.kits.vizkit import Vizkit, get_channel_name



class Linekit(Vizkit):
    viz_type = 'line'

    def prepare_channels(self):
        channels = self._channels_init(self.channel_kwargs)
        return channels

    command_decorators = (
    standard_options_decor,
    click.option("--xvar", "-x", type=click.STRING, default="", help="the label column"),
    click.option("--yvar", "-y", type=click.STRING, default="", help="the value column"),
    click.option(
        "--stroke",
        "-s",
        "strokevar",
        type=click.STRING,
        help="The column used to specify stroke color",
    ),

    )
