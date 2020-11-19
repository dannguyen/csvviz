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
    help_info = f"""A TKTKTK"""
    help_epilog = (
        """Example:\t csvviz heatmap -x state -y item -c sold examples/hot.csv"""
    )
    color_channel_name = "fill"
    default_chart_width = 500
    default_chart_height = 500

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
            required=True,  # TODO: should this automatically be set to column_names[2]?
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

    def validate_options(self, options: dict) -> bool:
        # already handled by Click.option constructor
        # if not options.get("fillvar"):  # TK colorvar
        #     raise ConflictingArgs("-c/--colorvar needs to be specified")
        return True

    def finalize_channels(self, channels):
        return channels
