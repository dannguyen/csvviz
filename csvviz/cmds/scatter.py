"""
scatter.py
"""
from pathlib import Path

import altair as alt
import click
from csvviz.cli_utils import clout, clerr, clexit
from csvviz.cli_utils import (
    input_file_decor,
    output_options_decor,
    visual_options_decor,
)
from csvviz.exceptions import *
from csvviz.kits.vizkit import Vizkit


@click.command(name="scatter")
@input_file_decor
@output_options_decor
@visual_options_decor
@click.option("--xvar", "-x", type=click.STRING, default="", help="the label column")
@click.option("--yvar", "-y", type=click.STRING, default="", help="the value column")
@click.option(
    "--fill",
    "-f",
    "fillvar",
    type=click.STRING,
    help="The column used to specify fill color",
)
@click.option(
    "--size",
    "-s",
    "sizevar",
    type=click.STRING,
    help="The column used to specify dot size",
)
def command(**kwargs):
    """
    Prints a horizontal bar chart.

    https://altair-viz.github.io/gallery/bar_chart_horizontal.html

    If the -x and -y flags aren't supplied, we assume they are represented by the 1st
        and 2nd columns, respectively,
    """
    # set up theme config
    try:
        vk = ScatterKit(input_file=kwargs.get("input_file"), kwargs=kwargs)
    except InvalidDataReference as err:
        clexit(1, err)
    else:
        vk.output_chart()


class ScatterKit(Vizkit):
    def __init__(self, input_file, kwargs):
        super().__init__(viz_type="scatter", input_file=input_file, kwargs=kwargs)

    def prepare_channels(
        self,
    ):  # -> typeDict[str, typeUnion[alt.X, alt.Y, alt.Fill, alt.Size]]:

        channels = self._init_channels(self.channel_kwargs, self.datakit)
        if channels.get("fill"):
            channels["fill"].scale = alt.Scale(**self._config_colors(self.color_kwargs))

        return channels
