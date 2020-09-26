import altair as alt
import click
from csvviz.cli_utils import clout, clerr, clexit
from csvviz.cli_utils import standard_options_decor

from csvviz.exceptions import *
from csvviz.kits.vizkit import Vizkit


@click.command(name="bar")
@standard_options_decor
@click.option("--xvar", "-x", type=click.STRING, default="", help="the label column")
@click.option("--yvar", "-y", type=click.STRING, default="", help="the value column")
@click.option(
    "--fill",
    "-f",
    "fillvar",
    type=click.STRING,
    help="The column used to specify fill color",
)

###### specific to bar charts
@click.option(
    "--horizontal", "-H", "flipxy", is_flag=True, help="Orient the bars horizontally"
)
@click.option(
    "--sort",
    "sortx_var",
    type=click.STRING,
    help="Sort the x-axis by the values of the x/y/fill channel. Prefix with '-' to do reverse sort",
)  # https://altair-viz.github.io/user_guide/encoding.html#sorting
def command(**kwargs):
    """
    Creates a bar chart

    https://altair-viz.github.io/gallery/simple_bar_chart.html

    If the -x and -y flags aren't supplied, we assume they are represented by the 1st
        and 2nd columns, respectively,
    """
    # set up theme config
    try:
        vk = Barkit(input_file=kwargs.get("input_file"), kwargs=kwargs)
    except InvalidDataReference as err:
        clexit(1, err)
    else:
        vk.output_chart()


class Barkit(Vizkit):
    def __init__(self, input_file, kwargs):
        super().__init__(viz_type="bar", input_file=input_file, kwargs=kwargs)

    def prepare_channels(
        self,
    ):  # -> typeDict[str, typeUnion[alt.X, alt.Y, alt.Fill, alt.Size]]:

        channels = self._init_channels(self.channel_kwargs, self.datakit)

        if self.kwargs.get("flipxy"):  # i.e. -H/--horizontal flag
            channels["x"], channels["y"] = (channels["y"], channels["x"])

        if channels.get("fill"):
            channels["fill"].scale = alt.Scale(**self._config_colors(self.color_kwargs))

        if _sortvar := self.kwargs.get("sortx_var"):
            # _sort_config := self._config_sorting(self.kwargs, self.datakit):
            _cname = _sortvar.lstrip("-")
            if not channels.get(_cname):
                raise InvalidDataReference(
                    f"'{_cname}' is not a valid channel to sort by"
                )
            else:
                channels["x"].sort = _sortvar

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
