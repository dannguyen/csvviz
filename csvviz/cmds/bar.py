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
from csvviz.csvviz import clout, clerr


@click.command()
@click.argument('input_file', type=click.File('r'))

# TODO:
# ycol, i.e. value columns, can accept more than one
@click.option('--xvar', '-x', type=click.STRING, default='0', help='the label column')
@click.option('--yvar', '-y', type=click.STRING, default='1', help='the value column')
@click.option('--series', '-s', type=click.STRING, help='the column to use for series')
@click.option('--theme', type=click.Choice(alt.themes.names(), case_sensitive=False),
    default='default', help="choose a built-in theme for chart") # refactor alt.themes.names() to constant

# common options
@click.option('to_json', '--json/--no-json', '-j /', default=False, help='Output to stdout the Vega JSON representation')
@click.option('do_not_preview', '--no-preview/--show-preview', default=False, help='Preview the chart in the web browser')
def bars(input_file, xvar, yvar, series, **kwargs):
    """
    Prints a horizontal bar chart.

    https://altair-viz.github.io/gallery/bar_chart_horizontal.html

    If the -x and -y flags aren't supplied, we assume they are represented by the 1st
        and 2nd columns, respectively,
    """


    dk = Datakit(input_file)

    # set up encoding
    x_id, x_col = dk.resolve_column(xvar)
    y_id, y_col = dk.resolve_column(yvar)
    encode_kwargs = {'x': x_col, 'y': y_col}
    if series:
        s_id, series_col = dk.resolve_column(series)
        encode_kwargs['color'] = series_col

    # set up visual config
    alt.themes.enable(kwargs.get('theme'))

    chart = alt.Chart(dk.df).mark_bar().encode(**encode_kwargs)


    if kwargs.get('to_json'):
        clout(chart.to_json(indent=2))

    if not kwargs.get('do_not_preview'):
        altview.show(chart.interactive())



__command__ = bars


"""
Notes:

## Stacked

As long as --series and -x are different, y is implicitly taken as a sum:

    csvviz bars examples/fruits.csv -x product -y revenue -s region

However, if x and series are the same:

    csvviz bars examples/fruits.csv -x product -y revenue -s product

Then there is no stacked sum. It has to be set in Altair explicitly:

    altview.show(alt.Chart(df).mark_bar().encode(x='product', y='sum(revenue)', color="product"))



- bar/column charts
    - stacked
        - https://altair-viz.github.io/gallery/stacked_bar_chart.html
        - https://altair-viz.github.io/user_guide/transform/stack.html?highlight=stack
        - use `color=` to set stacks
    - grouped
        - https://altair-viz.github.io/gallery/grouped_bar_chart.html
        - https://altair-viz.github.io/gallery/grouped_bar_chart_horizontal.html
        - use `color=` to set number of bars per group
        - use `column=` to set number of groups
    - ggplot2: https://www.r-graph-gallery.com/48-grouped-barplot-with-ggplot2.html



colors:
https://altair-viz.github.io/user_guide/customization.html?highlight=colors#color-schemes


"""
