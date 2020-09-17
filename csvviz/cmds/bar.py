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
@click.option('--fill', '-f', type=click.STRING, help='The column used to specify fill color')
@click.option('--horizontal', '-h', is_flag=True, help='Orient the bars horizontally')


# common options
@click.option('--theme', type=click.Choice(alt.themes.names(), case_sensitive=False),
    default='default', help="choose a built-in theme for chart") # refactor alt.themes.names() to constant
@click.option('--json/--no-json', '-j /', 'to_json',default=False, help='Output to stdout the Vega JSON representation')
@click.option('--no-preview/--show-preview', 'do_not_preview', default=False, help='Preview the chart in the web browser')
def bar(input_file, xvar, yvar, fill, horizontal, **kwargs):
    """
    Prints a horizontal bar chart.

    https://altair-viz.github.io/gallery/bar_chart_horizontal.html

    If the -x and -y flags aren't supplied, we assume they are represented by the 1st
        and 2nd columns, respectively,
    """


    dk = Datakit(input_file)
    chart = alt.Chart(dk.df).mark_bar()
    # set up encoding
    _xvar, _yvar = (yvar, xvar) if horizontal else (xvar, yvar)

    x_id, x_col = dk.resolve_column(_xvar)
    y_id, y_col = dk.resolve_column(_yvar)
    encode_kwargs = {'x': alt.X(x_col), 'y': alt.Y(y_col)}

    # if colors:
    #     color_scale = alt.Scale(range=colors)
    #     alt.Color('product', scale= )

    if fill:
        s_id, fill_col = dk.resolve_column(fill)
        encode_kwargs['fill'] = alt.Fill(fill_col)


    chart = chart.encode(**encode_kwargs)


    # set up visual config
    alt.themes.enable(kwargs.get('theme'))


    if kwargs.get('to_json'):
        clout(chart.to_json(indent=2))

    if not kwargs.get('do_not_preview'):
        altview.show(chart.interactive())


__command__ = bar

"""
Notes:

## Stacked

As long as --fill and -x are different, y is implicitly taken as a sum:

    csvviz bars examples/fruits.csv -x product -y revenue -f region

However, if x and fill are the same:

    csvviz bars examples/fruits.csv -x product -y revenue -f region

Then there is no stacked sum. It has to be set in Altair explicitly:

    altview.show(alt.Chart(df).mark_bar().encode(x='product', y='sum(revenue)', fill="product"))


## Legend and colors and fill

- When fill is set, legend is automatically set
- When color range is set explicitly,


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
