"""
hist.py


csvviz hist 'year(birthday)' examples/real/congress.csv
"""

import altair as alt
import click
from csvviz.cli_utils import clout, clerr, clexit
from csvviz.cli_utils import standard_options_decor
from csvviz.exceptions import *
from csvviz.vizkit import Vizkit


class Histkit(Vizkit):
    viz_type = "hist"

    def prepare_channels(self):
        channels = self._channels_init(self.channel_kwargs)

        ##### bin time
        channels["x"].bin = True
        channels["y"] = "count()"
        #####

        if self.kwargs.get("flipxy"):  # i.e. -H/--horizontal flag
            channels["x"], channels["y"] = (channels["y"], channels["x"])

        if channels.get("fill"):
            channels["fill"].scale = alt.Scale(**self._config_colors(self.color_kwargs))
            channels["fill"].legend = None

        return channels

    COMMAND_DECORATORS = (
        click.option(
            "--xvar", "-x", type=click.STRING, default="", help="the thing to bin TK"
        ),
        click.option(
            "--fill",
            "-f",
            "fillvar",
            type=click.STRING,
            help="The column used to specify fill color",
        ),
        click.option(
            "--horizontal",
            "-H",
            "flipxy",
            is_flag=True,
            help="Orient the bars horizontally",
        ),
    )
