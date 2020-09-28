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
    viz_type = "area"
    viz_info = f"""An area chart. Can be stacked"""

    COMMAND_DECORATORS = (
        click.option(
            "--xvar", "-x", type=click.STRING, default="", help="the label column"
        ),
        click.option(
            "--yvar", "-y", type=click.STRING, default="", help="the value column"
        ),
        click.option(
            "--color",
            "-c",
            "fillvar",
            type=click.STRING,
            help="The column used to specify fill color",
        ),
        # https://altair-viz.github.io/user_guide/encoding.html?#ordering-marks
        click.option(
            "--color-sort",
            "-cs",
            "fillsort",
            type=click.Choice(("+", "-")),
            help="Whether to sort the fill stack in ascending (+) or descending (-) order by nominal name TKTK",
        ),
    )

    def prepare_channels(self):
        channels = self._create_channels(self.channel_kwargs)

        # sort by fill/stack is not the same as sorting the x-axis:
        # https://altair-viz.github.io/user_guide/encoding.html?#ordering-marks
        if _fillsort := self.kwargs.get("fillsort"):
            if not channels.get("fill"):
                raise MissingDataReference(
                    f"--color-sort '{_fillsort}' was specified, but no --color value was provided"
                )
            else:
                fname = self.resolve_channel_name(channels["fill"])
                fsort = "descending" if _fillsort == "-" else "ascending"
                channels["order"] = alt.Order(fname, sort=fsort)

        return channels
