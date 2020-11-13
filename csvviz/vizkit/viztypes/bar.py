import altair as alt
import click


from csvviz.exceptions import *
from csvviz.vizkit import Vizkit


class Barkit(Vizkit):
    viz_commandname = "bar"
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

    @property
    def normalized(self) -> bool:
        return True if self.kwargs.get("normalized") else False

    @classmethod
    def validate_kwargs(klass, kwargs: dict) -> bool:
        if kwargs.get("normalized"):
            if not kwargs.get("fillvar"):  # TK SHOULD BE COLORVAR NOT fillvar
                raise MissingDataReference(
                    "-c/--colorvar needs to be specified when creating a normalized (i.e. stacked) chart"
                )

        # sorting by x-axis var is unique to bar charts, and not like color/fill/facet sort,
        # because we are sorting by channel, e.g. x/y/etc
        # https://altair-viz.github.io/gallery/bar_chart_sorted.html
        s = kwargs.get("sortx_var")
        if s and s.lstrip("-") not in ("x", "y", "color"):
            raise InvalidDataReference(f"'{s}' is not a valid channel to sort by")

        return True

    def finalize_channels(self, channels):

        if self.kwargs.get("flipxy"):  # i.e. -H/--horizontal flag
            channels["x"], channels["y"] = (channels["y"], channels["x"])

        # https://altair-viz.github.io/gallery/normalized_stacked_bar_chart.html
        if self.normalized:
            channels["y"].stack = "normalize"
            channels["y"].axis = alt.Axis(format="%")

        if self.kwargs.get("sortx_var"):
            channels["x"].sort = self.kwargs["sortx_var"]

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
