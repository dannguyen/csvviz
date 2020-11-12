"""
heatmap.py


csvviz heatmap -x state -y item -c sold examples/hot.csv

"""

import altair as alt
import click
from csvviz.exceptions import *
from csvviz.vizkit import Vizkit


class Heatmapkit(Vizkit):

    viz_commandname = "heatmap"
    viz_info = f"""A TKTKTK"""
    viz_epilog = (
        """Example:\t csvviz heatmap -x state -y item -c sold examples/hot.csv"""
    )

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
            help="The name of the column for mapping TK colors.",
        ),
        # # https://altair-viz.github.io/user_guide/encoding.html#sorting
        # click.option(
        #     "--x-sort",
        #     "-xs",
        #     "sortx_var",
        #     type=click.STRING,
        #     help="Sort the x-axis by the values of the x/y/fill channel. Prefix with '-' to do reverse sort, e.g. 'y' vs '-y'",
        # ),
    )

    def finalize_channels(self, channels):

        if not channels.get("fill"):
            raise MissingDataReference("-c/--colorvar needs to be specified")

        return channels
