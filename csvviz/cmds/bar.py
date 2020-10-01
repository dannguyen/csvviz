import altair as alt
import click


from csvviz.exceptions import *
from csvviz.vizkit import Vizkit


class Barkit(Vizkit):
    viz_type = "bar"
    viz_info = f"""An bar/column chart"""
    viz_epilog = """Example:\tcsvviz bar -x name -y amount data.csv"""

    COMMAND_DECORATORS = (
        click.option(
            "--xvar",
            "-x",
            type=click.STRING,
            help="The name of the column for mapping x-axis values; if empty, the first (columns[0]) column is used",
        ),
        click.option(
            "--yvar",
            "-y",
            type=click.STRING,
            help="The name of the column for mapping y-axis values; if empty, the second (columns[1]) column is used",
        ),
        click.option(
            "--colorvar",
            "-c",
            "fillvar",
            type=click.STRING,
            help="The name of the column for mapping bar colors. This is required for creating a stacked chart.",
        ),
        # https://altair-viz.github.io/user_guide/encoding.html?#ordering-marks
        click.option(
            "--color-sort",
            "-cs",
            "fillsort",
            type=click.Choice(("asc", "desc"), case_sensitive=False),
            help="For stacked bar charts, the sort order of the color variable: 'asc' for ascending, 'desc' for descending/reverse",
        ),
        # https://altair-viz.github.io/user_guide/encoding.html#sorting
        click.option(
            "--x-sort",
            "-xs",
            "sortx_var",
            type=click.STRING,
            help="Sort the x-axis by the values of the x/y/fill channel. Prefix with '-' to do reverse sort, e.g. 'y' vs '-y'",
        ),
        ###### specific to bar charts
        click.option(
            "--horizontal",
            "-H",
            "flipxy",
            is_flag=True,
            help="Make a horizontal bar chart",
        ),
        click.option(
            "--normalized",
            "-N",
            is_flag=True,
            help="For stacked bar charts, normalize the total bar heights to 100%",
        ),
    )

    def finalize_channels(self, channels):

        self._set_channel_colorscale("fill", channels)

        if self.kwargs.get("flipxy"):  # i.e. -H/--horizontal flag
            channels["x"], channels["y"] = (channels["y"], channels["x"])

        # https://altair-viz.github.io/gallery/normalized_stacked_bar_chart.html
        if self.kwargs.get("normalized"):
            if not channels.get("fill"):
                raise MissingDataReference(
                    "-c/--colorvar needs to be specified when creating a normalized (i.e. stacked) chart"
                )
            else:
                channels["y"].stack = "normalize"
                channels["y"].axis = alt.Axis(format="%")

        # sorting by x-axis var is unique to bar charts, and not like color/fill/facet sort,
        # because we are sorting by channel, e.g. x/y/etc
        _sortvar = self.kwargs.get("sortx_var")  # walrus
        if _sortvar:  # /walrus
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
