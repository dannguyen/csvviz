import altair as alt
import click
from typing import Dict as DictType


from csvviz.exceptions import ConflictingArgs, InvalidDataReference
from csvviz.vizkit import Vizkit
from csvviz.vizkit.channel_group import ChannelGroup
from csvviz.vizkit.chart import Chart


class Barkit(Vizkit):
    viz_commandname = "bar"
    help_info = f"""A bar/column chart"""  # TK change this when we make Columnkit
    help_epilog = """Example:\tcsvviz bar -x name -y amount data.csv"""
    color_channel_name = "fill"

    # ok, horizontal bar charts are confusing because by default, cvz bar makes a COLUMN chart
    # TK: make cvz column type
    default_chart_width = 400
    default_chart_height = 600

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
            "colorvar",
            type=click.STRING,
            help="The name of the column for mapping bar colors. This is required for creating a stacked chart.",
        ),
        # TKD: DEPRECATED FOR NOW
        # # https://altair-viz.github.io/user_guide/encoding.html?#ordering-marks
        # click.option(
        #     "--color-sort",
        #     "--cs",
        #     "color_sort",
        #     type=click.Choice(("asc", "desc"), case_sensitive=False),
        #     help="For stacked bar charts, the sort order of the color variable: 'asc' for ascending, 'desc' for descending/reverse",
        # ),
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
            "--HZ",  # TK kill this...
            "is_horizontal",
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
    def is_horizontal(self) -> bool:
        return self.options.get("is_horizontal") is True

    @property
    def normalized(self) -> bool:
        return True if self.options.get("normalized") else False

    def validate_options(self, options: dict) -> bool:
        super().validate_options(options)

        if not options.get("colorvar"):
            if options.get("normalized"):
                raise ConflictingArgs(
                    "-c/--colorvar needs to be specified when creating a normalized (i.e. stacked) chart"
                )

            # TKD
            # if options.get("color_sort"):
            #     raise ConflictingArgs(
            #         "--color-sort '{}' was specified, but no --colorvar value was provided".format(
            #             options["color_sort"]
            #         )
            #     )

        # sorting by x-axis var is unique to bar charts, and not like color/fill/facet sort,
        # because we are sorting by channel, e.g. x/y/etc
        # https://altair-viz.github.io/gallery/bar_chart_sorted.html
        s = options.get("sortx_var")
        if s and s.lstrip("-") not in ("x", "y", "color"):
            raise InvalidDataReference(f"'{s}' is not a valid channel to sort by")

        # TKD
        # TODO: DRY this with area's code
        # s = options.get("color_sort")
        # if s:
        #     if s not in (
        #         "asc",
        #         "desc",
        #     ):
        #         raise ValueError(f"Invalid sort order term: {s}")

        return True

    def finalize_channels(self, channels: ChannelGroup) -> ChannelGroup:

        if self.options.get("is_horizontal"):  # i.e. -H/--horizontal flag
            channels["x"], channels["y"] = (channels["y"], channels["x"])

        # https://altair-viz.github.io/gallery/normalized_stacked_bar_chart.html
        if self.normalized:
            channels["y"].stack = "normalize"
            channels["y"].axis = alt.Axis(format="%")

        if self.options.get("sortx_var"):
            channels["x"].sort = self.options["sortx_var"]

        return channels
        # color_sort functionality shared by bar and area charts
        ##################################
        # subfunction: --color-sort, i.e. ordering of fill; only valid for area and bar charts
        # somewhat confusingly, sort by fill does NOT alter alt.Fill, but adds an Order channel
        # https://altair-viz.github.io/user_guide/encoding.html?#ordering-marks

        # TKD
        # cs = self.options.get("color_sort")
        # # validation has already been done by this point
        # if cs:
        #     fname = channels.get_data_field(self.color_channel_name)
        #     channels["order"] = alt.Order(fname)
        #     channels["order"].sort = "descending" if cs == "desc" else "ascending"

    def finalize_chart(self, chart: Chart) -> Chart:
        # ok, horizontal bar charts are confusing because by default, cvz bar makes a COLUMN chart
        # TK: make cvz column type
        if self.is_horizontal:
            w = chart.get_prop("width")
            h = chart.get_prop("height")
            chart.set_props({"width": h, "height": w})
        return chart


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
