"""
hist.py


csvviz hist 'year(birthday)' examples/real/congress.csv
"""

import altair as alt
import click
from csvviz.cli_utils import clout, clerr, clexit
from csvviz.cli_utils import standard_options_decor
from csvviz.exceptions import *
from csvviz.kits.vizkit import Vizkit


@click.command(name="hist")
@standard_options_decor
@click.option("--xvar", "-x", type=click.STRING, default="", help="the thing to bin TK")
@click.option(
    "--fill",
    "-f",
    "fillvar",
    type=click.STRING,
    help="The column used to specify fill color",
)
@click.option(
    "--horizontal", "-H", "flipxy", is_flag=True, help="Orient the bars horizontally"
)
def command(**kwargs):
    """
    Creates a histogram: a bar chart in which the -x value is binned

    https://altair-viz.github.io/gallery/simple_histogram.html

    csvviz hist 'year(birthday)' examples/real/congress.csv
    """
    # set up theme config
    try:
        vk = Histkit(input_file=kwargs.get("input_file"), kwargs=kwargs)
    except InvalidDataReference as err:
        clexit(1, err)
    else:
        vk.output_chart()


class Histkit(Vizkit):
    def __init__(self, input_file, kwargs):
        super().__init__(viz_type="hist", input_file=input_file, kwargs=kwargs)

    def prepare_channels(self):
        channels = self._channels_init(self.channel_kwargs, self.datakit)

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
