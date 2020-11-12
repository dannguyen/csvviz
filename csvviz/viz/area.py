"""
area.py

$ csvviz line examples/stocks.csv  -x 'date:T' -y price -s company

$ csvviz line examples/tonk.csv --json -x date:T
"""

import altair as alt
import click
from csvviz.exceptions import *
from csvviz.vizkit import Vizkit


class Areakit(Vizkit):
    viz_commandname = "area"
    viz_info = f"""An area chart. Can be stacked"""
    viz_epilog = """Example:  $ csvviz area -x date -y price -c company stocks.csv"""

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

    def finalize_channels(self, channels):
        self._set_channel_colorscale("fill", channels)

        # Todo: DRY to a method shared by area and b ar
        # https://altair-viz.github.io/gallery/normalized_stacked_area_chart.html
        if self.kwargs.get("normalized"):
            if not channels.get("fill"):
                raise MissingDataReference(
                    "-c/--colorvar needs to be specified when creating a normalized (i.e. stacked) chart"
                )
            else:
                channels["y"].stack = "normalize"
                channels["y"].axis = alt.Axis(format="%")

        return channels