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
import altair as alt

from csvviz.utils.datakit import Datakit
from csvviz.cli_utils import clout, clerr, preview_chart
from csvviz.settings import *





@click.command()
@click.argument('input_file', type=click.File('r'))
@click.option('--xvar', '-x', type=click.STRING, default='0', help='the label column')
@click.option('--yvar', '-y', type=click.STRING, default='1', help='the value column')
@click.option('--fill', '-f', type=click.STRING, help='The column used to specify fill color')
@click.option('--horizontal', '-H', is_flag=True, help='Orient the bars horizontally')
@click.option('-c', '--colors', type=click.STRING, help='A comma-delimited list of colors to use for the bar fill')
@click.option('-C', '--color-scheme', type=click.STRING, help='The name of a Vega color scheme to use for fill (this is overridden by -c/--colors)')

# common options
@click.option('--theme', type=click.Choice(alt.themes.names(), case_sensitive=False),
    default='default', help="choose a built-in theme for chart") # refactor alt.themes.names() to constant
@click.option('--json/--no-json', '-j /', 'to_json', default=False, help='Output to stdout the Vega JSON representation')

@click.option('--preview/--no-preview', 'do_preview', default=True, help='Preview the chart in the web browser')
@click.option('--interactive/--static', 'is_interactive', default=False, help='Preview an interactive or static version of the chart in the web browser')

def bar(input_file, xvar, yvar, fill, horizontal, **kwargs):
    """
    Prints a horizontal bar chart.

    https://altair-viz.github.io/gallery/bar_chart_horizontal.html

    If the -x and -y flags aren't supplied, we assume they are represented by the 1st
        and 2nd columns, respectively,
    """


    dk = Datakit(input_file)
    chart = alt.Chart(dk.df).mark_bar()


    # set up theme config
    alt.themes.enable(kwargs.get('theme'))


    # set up encoding
    encode_kwargs = {}

    _xvar, _yvar = (yvar, xvar) if horizontal else (xvar, yvar)
    x_id, encode_kwargs['x'] = dk.resolve_column(_xvar)
    y_id, encode_kwargs['y'] = dk.resolve_column(_yvar)

    fill_scale_kwargs = {'scheme': DEFAULT_COLOR_SCHEME}

    if _cs := kwargs.get('color_scheme'):
        fill_scale_kwargs['scheme'] = _cs
        # TODO: if _cs does not match a valid color scheme, then raise a warning/error

    if _colors := kwargs['colors']:
        # don't think this needs to be a formal parser
        fill_scale_kwargs['range'] = _colors.strip().split(',')
        # for now, only colors OR color_scheme can be set, not both
        fill_scale_kwargs.pop('scheme', None)

    if fill:
        s_id, fill_col = dk.resolve_column(fill)
        encode_kwargs['fill'] = alt.Fill(fill_col, scale=alt.Scale(**fill_scale_kwargs))


    chart = chart.encode(**encode_kwargs)

    # --interactive/--static chart is independent of whether or not we're previewing it,
    #  which is reflected in its JSON representation
    if kwargs['is_interactive']:
        chart = chart.interactive()

    # echo JSON before doing a preview
    if kwargs.get('to_json'):
        clout(chart.to_json(indent=2))

    if kwargs['do_preview']:
        preview_chart(chart)

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
