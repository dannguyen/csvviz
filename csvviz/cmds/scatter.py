"""
scatter.py
"""
from pathlib import Path

import altair as alt
import click
from csvviz.cli_utils import clout, clerr, clexit
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


# common visual options
@click.option(
    "-c",
    "--colors",
    type=click.STRING,
    help="A comma-delimited list of colors to use for the bar fill",
)
@click.option(
    "-C",
    "--color-scheme",
    type=click.STRING,
    help="The name of a Vega color scheme to use for fill (this is overridden by -c/--colors)",
)
@click.option(
    "--theme",
    type=click.Choice(alt.themes.names(), case_sensitive=False),
    default="default",
    help="choose a built-in theme for chart",
)  # refactor alt.themes.names() to constant
@click.option("--title", "-t", type=click.STRING, help="A title for the chart")
@click.option("--hide-legend", is_flag=True, help="Omits the legend")

# # axis stuff
# @click.option("--x-title", type=click.STRING, help="TK TK testing")
# @click.option("--x-min", type=click.STRING, help="TK TK testing")
# @click.option("--x-max", type=click.STRING, help="TK TK testing")

# common input output/options
@click.option(
    "--json/--no-json",
    "-j /",
    "to_json",
    default=False,
    help="Output to stdout the Vega JSON representation",
)
@click.option(
    "--preview/--no-preview",
    "do_preview",
    default=True,
    help="Preview the chart in the web browser",
)
@click.option(
    "--interactive/--static",
    "is_interactive",
    default=True,
    help="Preview an interactive (default) or static version of the chart in the web browser",
)
@click.argument("input_file", type=click.File("r"))
def scatter(**kwargs):
    """
    Prints a horizontal bar chart.

    https://altair-viz.github.io/gallery/bar_chart_horizontal.html

    If the -x and -y flags aren't supplied, we assume they are represented by the 1st
        and 2nd columns, respectively,
    """
    # set up theme config
    input_file = kwargs.get('input_file')


    try:
        vk = Vizkit(viz_type="scatter", input_file=input_file, kwargs=kwargs)
    except InvalidColumnName as err:
        clexit(1, err)
    else:
        vk.output_chart()


__command__ = scatter
