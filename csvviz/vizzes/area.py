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
    viz_info = f"""An area chart. Can be stacked"""
    viz_epilog = """Example:  $ csvviz area -x date -y price -c company stocks.csv"""
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
            help="For stacked charts, the sort order of the color variable: 'asc' for ascending, 'desc' for descending/reverse",
        ),
        click.option(
            "--normalized",
            "-N",
            is_flag=True,
            help="For stacked bar charts, normalize the total area heights to 100%",
        ),
    )

    def validate_kwargs(self, kwargs: dict) -> bool:
        super().validate_kwargs(kwargs)

        # TODO: DRY this with bar's implementation
        if kwargs.get("normalized"):
            if not kwargs.get("fillvar"):  # TK SHOULD BE COLORVAR NOT fillvar
                raise ConflictingArgs(
                    "-c/--colorvar needs to be specified when creating a normalized (i.e. stacked) chart"
                )
        # TODO: DRY this with bar's imp
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

    @property
    def normalized(self) -> bool:
        return True if self.kwargs.get("normalized") else False

    def finalize_channels(self, channels: ChannelGroup) -> ChannelGroup:
        # https://altair-viz.github.io/gallery/normalized_stacked_bar_chart.html
        if self.normalized:
            channels["y"].stack = "normalize"
            channels["y"].axis = alt.Axis(format="%")

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
