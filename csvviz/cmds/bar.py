"""
bar.py

Make a bar/column chart
"""
from pathlib import Path

import altair as alt
import click
from csvviz.cli_utils import clout, clerr, clexit
from csvviz.cli_utils import (
    input_file_decor,
    output_options_decor,
    visual_options_decor,
)
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
# @click.option('--sort-x',  type=click.Choice(['x', '-x', 'y', '-y', 'fill', '-fill'], case_sensitive=False), help='Optional: which axis to sort the marks by (e.g. x, y)')
@click.option(
    "--sort",
    "sortx_var",
    type=click.STRING,
    help="Optional: sort the x-axis by a field other than the field specified by -x/--xvar",
)

# unique to bar viz
@click.option(
    "--horizontal", "-H", "flipxy", is_flag=True, help="Orient the bars horizontally"
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

# axis stuff
@click.option("--x-title", type=click.STRING, help="TK TK testing")
@click.option("--x-min", type=click.STRING, help="TK TK testing")
@click.option("--x-max", type=click.STRING, help="TK TK testing")
@visual_options_decor
@output_options_decor
@input_file_decor
def bar(**kwargs):
    """
    Prints a horizontal bar chart.

    https://altair-viz.github.io/gallery/bar_chart_horizontal.html

    If the -x and -y flags aren't supplied, we assume they are represented by the 1st
        and 2nd columns, respectively,
    """
    # set up theme config
    try:
        vk = Barkit(input_file=kwargs.get("input_file"), kwargs=kwargs)
    except InvalidDataReference as err:
        clexit(1, err)
    except ValueError as err:
        clexit(1, err)
    else:
        vk.output_chart()


__command__ = bar


class Barkit(Vizkit):
    def __init__(self, input_file, kwargs):
        super().__init__(viz_type="bar", input_file=input_file, kwargs=kwargs)

    def prepare_channels(
        self,
    ):  # -> typeDict[str, typeUnion[alt.X, alt.Y, alt.Fill, alt.Size]]:

        channels = self._init_channels(self.channel_kwargs, self.datakit)

        if self.kwargs.get("flipxy"):  # i.e. -H/--horizontal flag
            channels["x"], channels["y"] = (channels["y"], channels["x"])

        if the_fill := channels.get("fill"):
            the_fill.scale = alt.Scale(**self._config_colors(self.color_kwargs))
            _legend = self._config_legend(self.legend_kwargs, colname=the_fill.field)

            # legend = None effectively hides it, which is what we want
            the_fill.legend = None if _legend is False else _legend
            # emphasize that we're editing channels['fill']
            channels["fill"] = the_fill

        if _sort_config := self._config_sorting(self.kwargs, self.datakit):
            channels["x"].sort = _sort_config

        return channels


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
