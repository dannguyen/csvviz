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


    def prepare_channels(self): # -> typeDict[str, typeUnion[alt.X, alt.Y, alt.Fill, alt.Size]]:

        channels = self._init_channels(self.channel_kwargs, self.datakit)
        if the_fill := channels.get("fill"):
            the_fill.scale = alt.Scale(**self._config_colors(self.color_kwargs))
            _legend = self._config_legend(self.legend_kwargs, colname=the_fill.field)

            # legend = None effectively hides it, which is what we want
            the_fill.legend = None if _legend is False else _legend
            # emphasize that we're editing channels['fill']
            channels['fill'] = the_fill


        return channels



__command__ = scatter
