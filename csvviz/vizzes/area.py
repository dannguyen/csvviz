"""
area.py

$ csvviz line examples/stocks.csv  -x 'date:T' -y price -s company

$ csvviz line examples/tonk.csv --json -x date:T
"""

import altair as alt
import click
from csvviz.exceptions import *
from csvviz.vizkit import Vizkit
from csvviz.vizkit.channel_group import ChannelGroup


class Areakit(Vizkit):
    viz_commandname = "area"
    help_info = f"""An area chart. Can be stacked"""
    help_epilog = """Example:  $ csvviz area -x date -y price -c company stocks.csv"""
    color_channel_name = "fill"

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
        click.option(
            "--normalized",
            "-N",
            is_flag=True,
            help="For stacked bar charts, normalize the total area heights to 100%",
        ),
        # TKD
        # https://altair-viz.github.io/user_guide/encoding.html?#ordering-marks
        # click.option(
        #     "--color-sort",
        #     "--cs",
        #     "color_sort",
        #     type=click.Choice(("asc", "desc"), case_sensitive=False),
        #     help="For stacked charts, the sort order of the color variable: 'asc' for ascending, 'desc' for descending/reverse",
        # ),
    )

    def validate_options(self, options: dict) -> bool:
        super().validate_options(options)

        # TODO: DRY this with bar's implementation
        if not options.get("colorvar"):
            if options.get("normalized"):
                raise ConflictingArgs(
                    "-c/--colorvar needs to be specified when creating a normalized (i.e. stacked) chart"
                )

        # TKD
        #     if options.get("color_sort"):
        #         raise ConflictingArgs(
        #             "--color-sort '{}' was specified, but no --colorvar value was provided".format(
        #                 options["color_sort"]
        #             )
        #         )

        # s = options.get("color_sort")
        # if s:
        #     if s not in (
        #         "asc",
        #         "desc",
        #     ):
        #         raise ValueError(f"Invalid sort order term: {s}")

        return True

    @property
    def normalized(self) -> bool:
        return True if self.options.get("normalized") else False

    def finalize_channels(self, channels: ChannelGroup) -> ChannelGroup:
        # https://altair-viz.github.io/gallery/normalized_stacked_bar_chart.html
        if self.normalized:
            channels["y"].stack = "normalize"
            channels["y"].axis = alt.Axis(format="%")

        return channels

        # TKD
        # color_sort functionality shared by bar and area charts
        ##################################
        # subfunction: --color-sort, i.e. ordering of fill; only valid for area and bar charts
        # somewhat confusingly, sort by fill does NOT alter alt.Fill, but adds an Order channel
        # https://altair-viz.github.io/user_guide/encoding.html?#ordering-marks
        # cs = self.options.get("color_sort")
        # # validation has already been done by this point
        # if cs:
        #     fname = channels.get_data_field(self.color_channel_name)
        #     channels["order"] = alt.Order(fname)
        #     # TK: dry this
        #     channels["order"].sort = "descending" if cs == "desc" else "ascending"
