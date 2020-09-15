"""
bar.py

basically a Click.subcommand
"""

import click
from pathlib import Path

from typing import Mapping as typeMapping, NoReturn as typeNoReturn
from typing import List as typeList, Tuple as typeTuple, Union as typeUnion
from typing import IO as typeIO

# TODO: move to csvviz and generalize to a constant
import altair_viewer as altview
import altair as alt

from csvviz.utils.datakit import Datakit


@click.command()
@click.argument('input_file', type=click.File('r'))

# TODO:
# ycol, i.e. value columns, can accept more than one
@click.option('--xcol', '-x', type=click.STRING, default='0', help='the label column')
@click.option('--ycol', '-y', type=click.STRING, default='1', help='the value column')
def bars(input_file, xcol, ycol):
    """
    Prints a horizontal bar chart.

    https://altair-viz.github.io/gallery/bar_chart_horizontal.html

    If the -x and -y flags aren't supplied, we assume they are represented by the 1st
        and 2nd columns, respectively,
    """


    dk = Datakit(input_file)
    x_id, x_name = dk.resolve_column(xcol)
    y_id, y_name = dk.resolve_column(ycol)

    chart = alt.Chart(dk.df).mark_bar().encode(x=x_name, y=y_name)

    altview.show(chart.interactive())



__command__ = bars
