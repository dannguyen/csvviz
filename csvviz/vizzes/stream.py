"""
stream.py

$ csvviz stream examples/stocks.csv  -x 'date:T' -y price -c company --json
"""

import altair as alt
import click
from csvviz.exceptions import *
from csvviz.vizkit import Vizkit
from csvviz.vizkit.channel_group import ChannelGroup


class Streamkit(Vizkit):
    viz_commandname = "stream"
    help_info = f"""A streamgraph. Like an area chart, but streamy TK"""
    help_epilog = """Example:  $ csvviz stream examples/stocks.csv  -x 'date:T' -y price -c company --jsonv"""
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
            required=True,
            type=click.STRING,
            help="The name of the column for mapping bar colors. This is required.",
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
        # if not options.get("colorvar"):
        #     if options.get("color_sort"):
        #         raise ConflictingArgs(
        #             "--color-sort '{}' was specified, but no --colorvar value was provided".format(
        #                 options["color_sort"]
        #             )
        #         )
        # TKD
        # s = options.get("color_sort")
        # if s:
        #     if s not in (
        #         "asc",
        #         "desc",
        #     ):
        #         raise ValueError(f"Invalid sort order term: {s}")

        return True

    def finalize_channels(self, channels: ChannelGroup) -> ChannelGroup:
        # https://altair-viz.github.io/gallery/streamgraph.html
        channels["y"].stack = "center"
        channels["y"].axis = None

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
        #     # TK: dry this
        #     channels["order"].sort = "descending" if cs == "desc" else "ascending"
        return channels
