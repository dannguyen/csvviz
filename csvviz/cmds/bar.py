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
from csvviz.utils.datakit import Datakit


@click.command()
@click.option('--xvar', '-x', type=click.STRING, default='', help='the label column')
@click.option('--yvar', '-y', type=click.STRING, default='', help='the value column')
@click.option('--fill', '-f', 'fillvar', type=click.STRING, help='The column used to specify fill color')
# @click.option('--sort-x',  type=click.Choice(['x', '-x', 'y', '-y', 'fill', '-fill'], case_sensitive=False), help='Optional: which axis to sort the marks by (e.g. x, y)')
@click.option('--sort-x',  type=click.STRING, help='Optional: sort the x-axis by a field other than the field specified by -x/--xvar')

# unique to bar viz
@click.option('--horizontal', '-H', is_flag=True, help='Orient the bars horizontally')

# common visual options
@click.option('-c', '--colors', type=click.STRING, help='A comma-delimited list of colors to use for the bar fill')
@click.option('-C', '--color-scheme', type=click.STRING, help='The name of a Vega color scheme to use for fill (this is overridden by -c/--colors)')
@click.option('--theme', type=click.Choice(alt.themes.names(), case_sensitive=False),
    default='default', help="choose a built-in theme for chart") # refactor alt.themes.names() to constant

@click.option('--title', '-t', type=click.STRING, help='A title for the chart')

@click.option('--hide-legend', is_flag=True, help='Omits the legend')


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
    chart = alt.Chart(dk.df).mark_bar()

    # global settings, e.g. theme
    alt.themes.enable(kwargs.get('theme'))


    # encode stuff
    try:
        eargs = _encode_vars(dk, kwargs)
    except InvalidColumnName as err:
        clexit(1, err)

    if horizontal:
        eargs['x'], eargs['y'] = (eargs['y'], eargs['x'])

    chart = chart.encode(**eargs)


    # chart properties
    sprops = _style_chart(kwargs)
    chart = chart.properties(**sprops)

    _output_chart(chart, kwargs)



def _encode_vars(dk:Datakit, encoding_args:typeDict) -> typeDict:
    ed = {}

    _x = encoding_args.get('xvar') if encoding_args.get('xvar') else dk.column_names[0]
    _y = encoding_args.get('yvar') if encoding_args.get('yvar') else dk.column_names[1]


    ed['x'], _z = dk.resolve_column(_x)
    ed['y'], _z = dk.resolve_column(_y)




    if fill := encoding_args.get('fillvar'):
        _fill, _z = dk.resolve_column(fill)

        ## fill color stuff
        scale_kwargs = {'scheme': DEFAULT_COLOR_SCHEME}

        if _cs := encoding_args.get('color_scheme'):
            scale_kwargs['scheme'] = _cs
            # TODO: if _cs does not match a valid color scheme, then raise a warning/error

        if _colors := encoding_args['colors']:
            # don't think this needs to be a formal parser
            scale_kwargs['range'] = _colors.strip().split(',')
            # for now, only colors OR color_scheme can be set, not both
            scale_kwargs.pop('scheme', None)

        """
        note: it currently stinks that legend stuff is buried in the encoding part.

        Ideally, we would use alt.Chart.configure_legend to customize chart legend, but
          that doesn't let us do a configure_legend(none/False) when we want to hdie it
        """
        if encoding_args['hide_legend']:
            _legend = None
        else:
            _legend = alt.Legend(title=_fill, orient=DEFAULT_LEGEND_ORIENTATION)

        ed['fill'] = alt.Fill(_fill, legend=_legend, scale=alt.Scale(**scale_kwargs))


    # TODO: refactor, error handle
    if _sortx := encoding_args.get('sort_x'):
        _sign, _colname = re.match(r'(-?)(.+)', _sortx).groups()
        _order = 'descending' if _sign == '-' else 'ascending'
        sortobj = {'field': _colname, 'order': _order}

        ed['x'] = alt.X(ed['x'], sort=sortobj)

        #   _colname = ed[_channel]
        #   channel = getattr(alt, _channel.capitalize())
        #   e.g. ed['x'] = alt.X('name', '-x')
        #        ed[_channel] = channel(_colname, sort=_order)


    return ed


def _style_chart(style_args:typeDict) -> typeDict:
    sd = {}

    if _title := style_args.get('title'):
        sd['title'] = _title

    return sd


def _output_chart(chart:alt.Chart, render_args:typeDict) -> typeNoReturn:

    # --interactive/--static chart is independent of whether or not we're previewing it,
    #  which is reflected in its JSON representation
    if render_args['is_interactive']:
        chart = chart.interactive()

    # echo JSON before doing a preview
    if render_args.get('to_json'):
        clout(chart.to_json(indent=2))

    if render_args['do_preview']:
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
