"""
scatter.py
"""
from pathlib import Path

import altair as alt
import click
from csvviz.cli_utils import clout, clerr, clexit
from csvviz.cli_utils import input_file_decor, output_options_decor, visual_options_decor
from csvviz.exceptions import *
from csvviz.kits.vizkit import Vizkit


@click.command()
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
    "--size", "sizevar", type=click.STRING, help="The column used to specify dot size",
)


@visual_options_decor
@output_options_decor
@input_file_decor
def scatter(**kwargs):
    """
    Prints a horizontal bar chart.

    https://altair-viz.github.io/gallery/bar_chart_horizontal.html

    If the -x and -y flags aren't supplied, we assume they are represented by the 1st
        and 2nd columns, respectively,
    """
    # set up theme config
    try:
        vk = ScatterKit(input_file=kwargs.get('input_file'), kwargs=kwargs)
    except InvalidColumnName as err:
        clexit(1, err)
    else:
        vk.output_chart()


class ScatterKit(Vizkit):

    def __init__(self, input_file, kwargs):
        super().__init__(viz_type='scatter', input_file=input_file, kwargs=kwargs)


    def declare_channels(self): # -> typeDict[str, typeUnion[alt.X, alt.Y, alt.Fill, alt.Size]]:

        channels = self._init_channels(self.channel_kwargs, self.datakit)

        # unneeded: no horizontal thingy
        # if self.kwargs.get("flipxy"): # i.e. -H/--horizontal flag
        #     channels["x"], channels["y"] = (channels["y"], channels["x"])

        if _fill := channels.get("fill"):
            _fill.scale = alt.Scale(**self._config_colors(self.color_kwargs))
            # TODO: deal with legend being created for fill and size channels
            _legend = self._config_legend(self.legend_kwargs, colname=_fill.shorthand)
            if _legend is False:  # then hide_legend was explicitly specified
                _fill.legend = None
            else:
                _fill.legend = _legend

        # unneeded for scatter charts
        # if _sort_config := self._config_sorting(self.kwargs, self.datakit):
        #     channels["x"].sort = _sort_config

        return channels



__command__ = scatter
