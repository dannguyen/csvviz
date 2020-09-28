import altair as alt
import click
from csvviz.cli_utils import clout, clerr, clexit
from csvviz.cli_utils import standard_options_decor

from csvviz.exceptions import *
from csvviz.vizkit import Vizkit


class Barkit(Vizkit):
    viz_type = "bar"

    def prepare_channels(self):

        channels = self._channels_init(self.channel_kwargs)

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

    COMMAND_DECORATORS = (
        click.option(
            "--xvar", "-x", type=click.STRING, default="", help="the label column"
        ),
        click.option(
            "--yvar", "-y", type=click.STRING, default="", help="the value column"
        ),
        click.option(
            "--fill",
            "-f",
            "fillvar",
            type=click.STRING,
            help="The column used to specify fill color",
        ),
        ###### specific to bar charts
        click.option(
            "--horizontal",
            "-H",
            "flipxy",
            is_flag=True,
            help="Orient the bars horizontally",
        ),
        click.option(
            "--sort",  # https://altair-viz.github.io/user_guide/encoding.html#sorting
            "sortx_var",
            type=click.STRING,
            help="Sort the x-axis by the values of the x/y/fill channel. Prefix with '-' to do reverse sort",
        ),
    )


"""
Notes:

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
