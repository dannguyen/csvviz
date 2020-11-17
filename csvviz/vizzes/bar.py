import altair as alt
import click


from csvviz.exceptions import ConflictingArgs, InvalidDataReference
from csvviz.vizkit import Vizkit
from csvviz.vizkit.channel_group import ChannelGroup


class Barkit(Vizkit):
    viz_commandname = "bar"
    viz_info = f"""An bar/column chart"""
    viz_epilog = """Example:\tcsvviz bar -x name -y amount data.csv"""
    color_channeltype = "fill"

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

    def validate_kwargs(self, kwargs: dict) -> bool:
        super().validate_kwargs(kwargs)

        if kwargs.get("normalized"):
            if not kwargs.get("fillvar"):  # TK SHOULD BE COLORVAR NOT fillvar
                raise ConflictingArgs(
                    "-c/--colorvar needs to be specified when creating a normalized (i.e. stacked) chart"
                )
        # sorting by x-axis var is unique to bar charts, and not like color/fill/facet sort,
        # because we are sorting by channel, e.g. x/y/etc
        # https://altair-viz.github.io/gallery/bar_chart_sorted.html
        s = kwargs.get("sortx_var")
        if s and s.lstrip("-") not in ("x", "y", "color"):
            raise InvalidDataReference(f"'{s}' is not a valid channel to sort by")

        s = kwargs.get("fillsort")
        if s:
            if not kwargs.get("fillvar"):
                raise ConflictingArgs(
                    f"--color-sort '{s}' was specified, but no --colorvar value was provided"
                )

            if s not in (
                "asc",
                "desc",
            ):
                raise ValueError(f"Invalid sort order term: {s}")

        return True

    def finalize_channels(self, channels: ChannelGroup) -> ChannelGroup:

        if self.kwargs.get("flipxy"):  # i.e. -H/--horizontal flag
            channels["x"], channels["y"] = (channels["y"], channels["x"])

        # https://altair-viz.github.io/gallery/normalized_stacked_bar_chart.html
        if self.normalized:
            channels["y"].stack = "normalize"
            channels["y"].axis = alt.Axis(format="%")

        if self.kwargs.get("sortx_var"):
            channels["x"].sort = self.kwargs["sortx_var"]

        # fillsort functionality shared by bar and area charts
        ##################################
        # subfunction: --color-sort, i.e. ordering of fill; only valid for area and bar charts
        # somewhat confusingly, sort by fill does NOT alter alt.Fill, but adds an Order channel
        # https://altair-viz.github.io/user_guide/encoding.html?#ordering-marks
        fsort = self.kwargs.get("fillsort")
        # validation has already been done by this point
        if fsort:
            channels["order"] = alt.Order(channels.get_data_field("fill"))
            channels["order"].sort = "descending" if fsort == "desc" else "ascending"
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
