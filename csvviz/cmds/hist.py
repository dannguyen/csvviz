"""
hist.py


csvviz hist 'year(birthday)' examples/real/congress.csv
"""

import altair as alt
import click

from csvviz.exceptions import *
from csvviz.cmds.bar import Barkit
from csvviz.cli_utils import clerr

BINNING_OPTS = (
    "bincount",
    "binstepsize",
)


class Histkit(Barkit):
    viz_type = "hist"
    viz_info = f"""A bar chart that maps the frequency count of a given variable. Can be stacked."""
    viz_epilog = """Example:\t csvviz hist -x Horsepower examples/cars.csv"""

    COMMAND_DECORATORS = (
        click.option(
            "--xvar",
            "-x",
            type=click.STRING,
            help="The name of the column for mapping frequency count to the x-axis",
        ),
        click.option(
            "--colorvar",
            "-c",
            "fillvar",
            type=click.STRING,
            help="The name of the column for mapping bar colors. This is required for creating a stacked chart.",
        ),
        click.option(
            "--horizontal",
            "-H",
            "flipxy",
            is_flag=True,
            help="Make a horizontal bar chart",
        ),
        click.option(
            "--bins",
            "-n",
            "bincount",
            type=click.INT,
            help="Specify a max number of bins (overridden by -s/--bin-size)",
        ),
        click.option(
            "--bin-size",
            "-s",
            "binstepsize",
            type=click.FLOAT,
            help="Specify a size for each bin (overrides -n/--bins)",
        ),
    )

    def finalize_channels(self, channels):

        bwargs = {k: self.kwargs[k] for k in BINNING_OPTS if self.kwargs.get(k)}

        # deal with special case in which xvar is a nominal field, which means user
        # is trying to do a standard frequency count
        if channels["x"].type == "nominal":
            xname = self.resolve_channel_name(channels["x"])
            channels["y"] = {"aggregate": "count", "field": xname, "type": "nominal"}

            # issue warning if any binning options were set:
            if bwargs:
                self.warnings.append(
                    f"""Since '{xname}' consists of nominal values, csvviz will ignore bin-specific settings, e.g. -n/--bins and -s/--bin-size"""
                )

        else:
            channels[
                "y"
            ] = "count()"  # explicitly set/override y to always be an aggregate count
            # if no bin opts are set, then encoding.x.bins is just True
            #   and Vega defaults are used
            #   https://vega.github.io/vega-lite/docs/bin.html#bin-parameters
            channels["x"].bin = True
            if bwargs:
                bdict = {}
                _n = bwargs.get("bincount")  # walrus
                if _n:  # /walrus
                    bdict["maxbins"] = _n

                _s = bwargs.get("binstepsize")  # walrus

                if _s:  # /walrus
                    bdict["step"] = _s
                    bdict.pop("maxbins", None)  # override maxbins

                channels["x"].bin = alt.Bin(**bdict)

        return channels
