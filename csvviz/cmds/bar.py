"""
bar.py

basically a Click.subcommand
"""


from pathlib import Path
import re
from typing import Mapping as typeMapping, NoReturn as typeNoReturn
from typing import List as typeList, Tuple as typeTuple, Union as typeUnion, Dict as typeDict
from typing import IO as typeIO

# TODO: move to csvviz and generalize to a constant
import altair as alt
import click

from csvviz.cli_utils import clout, clerr, clexit, preview_chart
from csvviz.exceptions import *
from csvviz.settings import *
from csvviz.kits.datakit import Datakit


@click.command()
@click.option('--xvar', '-x', type=click.STRING, default='', help='the label column')
@click.option('--yvar', '-y', type=click.STRING, default='', help='the value column')
@click.option('--fill', '-f', 'fillvar', type=click.STRING, help='The column used to specify fill color')
# @click.option('--sort-x',  type=click.Choice(['x', '-x', 'y', '-y', 'fill', '-fill'], case_sensitive=False), help='Optional: which axis to sort the marks by (e.g. x, y)')
@click.option('--sort', 'sort_x',  type=click.STRING, help='Optional: sort the x-axis by a field other than the field specified by -x/--xvar')

# unique to bar viz
@click.option('--horizontal', '-H', is_flag=True, help='Orient the bars horizontally')

# common visual options
@click.option('-c', '--colors', type=click.STRING, help='A comma-delimited list of colors to use for the bar fill')
@click.option('-C', '--color-scheme', type=click.STRING, help='The name of a Vega color scheme to use for fill (this is overridden by -c/--colors)')
@click.option('--theme', type=click.Choice(alt.themes.names(), case_sensitive=False),
    default='default', help="choose a built-in theme for chart") # refactor alt.themes.names() to constant

@click.option('--title', '-t', type=click.STRING, help='A title for the chart')
@click.option('--hide-legend', is_flag=True, help='Omits the legend')

# axis stuff
@click.option('--x-title', type=click.STRING, help='TK TK testing')
@click.option('--x-min', type=click.STRING, help='TK TK testing')
@click.option('--x-max', type=click.STRING, help='TK TK testing')

# common input output/options
@click.option('--json/--no-json', '-j /', 'to_json', default=False, help='Output to stdout the Vega JSON representation')
@click.option('--preview/--no-preview', 'do_preview', default=True, help='Preview the chart in the web browser')
@click.option('--interactive/--static', 'is_interactive', default=False, help='Preview an interactive or static version of the chart in the web browser')
@click.argument('input_file', type=click.File('r'))
def bar(horizontal, input_file, **kwargs):
    """
    Prints a horizontal bar chart.

    https://altair-viz.github.io/gallery/bar_chart_horizontal.html

    If the -x and -y flags aren't supplied, we assume they are represented by the 1st
        and 2nd columns, respectively,
    """
    # set up theme config

    dk = Datakit(input_file)

    # global settings, e.g. theme
    alt.themes.enable(kwargs.get('theme'))

    # encode stuff
    try:
        _encoding = _handle_encoding(dk, kwargs)
    except InvalidColumnName as err:
        clexit(1, err)

    if horizontal:
        _encoding['x'], _encoding['y'] = (_encoding['y'], _encoding['x'])

    if _fill := _encoding.get('fill'):
        _fill.scale  = alt.Scale(**_handle_fill_color(kwargs))
        # _fill.legend = alt.Legend(title='mah legend', orient='bottom')
        if kwargs.get('hide_legend'):
            _fill.legend = None
        else:
            _fill.legend = alt.Legend(**_handle_legend(kwargs, colname=_fill.shorthand))


    try:
        if _sort_config := _handle_sorting(dk, kwargs):
            _encoding['x'].sort = _sort_config
    except InvalidColumnName as err:
        clexit(1, err)

    chart = alt.Chart(dk.df).mark_bar()
    chart = chart.encode(**_encoding)


    # chart properties
    _styling = _handle_styling(kwargs)
    chart = chart.properties(**_styling)

    _output_chart(chart, kwargs)



def _handle_encoding(dk:Datakit, args:typeDict) -> typeDict[str, typeUnion[alt.X, alt.Y, alt.Fill]]:
    config = {}

    _x = args.get('xvar') if args.get('xvar') else dk.column_names[0]
    _y = args.get('yvar') if args.get('yvar') else dk.column_names[1]


    _x, _z = dk.resolve_column(_x)
    config['x'] = alt.X(_x)
    _y, _z = dk.resolve_column(_y)
    config['y'] = alt.Y(_y)

    if _fill := args.get('fillvar'):
        _fill, _z = dk.resolve_column(_fill)
        config['fill'] = alt.Fill(_fill)

    return config



def _handle_fill_color(args:typeDict) -> typeDict:
    """
    returns a dict for alt.Scale()
    """
    ## fill color stuff
    config = {'scheme': DEFAULT_COLOR_SCHEME}

    if _cs := args.get('color_scheme'):
        config['scheme'] = _cs
        # TODO: if _cs does not match a valid color scheme, then raise a warning/error

    if _colors := args['colors']:
        # don't think this needs to be a formal parser
        config['range'] = _colors.strip().split(',')
        # for now, only colors OR color_scheme can be set, not both
        config.pop('scheme', None)

    return config


def _handle_legend(args:typeDict, colname:str) -> typeDict:
    config = {}
    # if args['hide_legend']:
    #     config = None
    # else:
    config['title'] = colname if not args.get('TK-column-title') else colname
    config['orient'] = DEFAULT_LEGEND_ORIENTATION
    # TODO: let users configure orientation and title...somehow

    return config



def _handle_sorting(dk:Datakit, args:typeDict) -> typeDict:
    config = {}
    if _sortx := args.get('sort_x'):
        _sign, _cname = re.match(r'(-?)(.+)', _sortx).groups()
        colname, _z = dk.resolve_column(_cname)  # mostly validation

        config['field'] = colname
        config['order'] = 'descending' if _sign == '-' else 'ascending'

    return config



def _handle_styling(args:typeDict) -> typeDict:
    config = {}

    if _title := args.get('title'):
        config['title'] = _title

    return config


def _output_chart(chart:alt.Chart, args:typeDict) -> typeNoReturn:

    # --interactive/--static chart is independent of whether or not we're previewing it,
    #  which is reflected in its JSON representation
    if args.get('is_interactive'):
        chart = chart.interactive()

    # echo JSON before doing a preview
    if args.get('to_json'):
        clout(chart.to_json(indent=2))

    if args['do_preview']:
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
