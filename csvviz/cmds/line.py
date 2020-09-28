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


@click.command(name="line")
@standard_options_decor
@click.option("--xvar", "-x", type=click.STRING, default="", help="the label column")
@click.option("--yvar", "-y", type=click.STRING, default="", help="the value column")
@click.option(
    "--stroke",
    "-s",
    "strokevar",
    type=click.STRING,
    help="The column used to specify stroke color",
)
def command(**kwargs):
    """
    Creates a line chart

    https://altair-viz.github.io/gallery/multi_series_line.html

    csvviz line examples/stocks.csv  -x 'date:T' -y price -s company
    """
    # set up theme config
    try:
        vk = Linekit(input_file=kwargs.get("input_file"), kwargs=kwargs)
    except InvalidDataReference as err:
        clexit(1, err)
    else:
        vk.output_chart()


class Linekit(Vizkit):
    def __init__(self, input_file, kwargs):
        super().__init__(viz_type="line", input_file=input_file, kwargs=kwargs)

    def prepare_channels(self):
        channels = self._channels_init(self.channel_kwargs, self.datakit)
        return channels
