"""
hist.py


csvviz hist 'year(birthday)' examples/real/congress.csv
"""

import altair as alt
import click
from typing import Dict as DictType

from csvviz.exceptions import *
from csvviz.vizzes.bar import Barkit
from csvviz.vizkit.chart import Chart

BINNING_OPTS = (
    "bincount",
    "binstepsize",
)


class Histkit(Barkit):
    viz_commandname = "hist"
    help_info = f"""A bar chart that maps the frequency count of a given variable. Can be stacked."""
    help_epilog = """Example:\t csvviz hist -x Horsepower examples/cars.csv"""
    color_channel_name = "fill"

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
        click.option(
            "--horizontal",
            "-H",
            "is_horizontal",
            is_flag=True,
            help="Make a horizontal bar chart",
        ),
    )

    def validate_options(self, options: dict) -> bool:
        super().validate_options(options)
        return True

    def finalize_channels(self, channels):
        bwargs = {k: self.options[k] for k in BINNING_OPTS if self.options.get(k)}
        # deal with special case in which xvar is a nominal field, which means user
        # is trying to do a standard frequency count
        if channels["x"].type == "nominal":
            xname = channels.get_data_field("x")
            channels["y"] = {"aggregate": "count", "field": xname, "type": "nominal"}

            # issue warning if any binning options were set:
            if bwargs:
                self.warnings.append(
                    f"""Since '{xname}' consists of nominal values, csvviz will ignore bin-specific settings, e.g. -n/--bins and -s/--bin-size"""
                )

        else:
            channels["y"] = "count()"
            # explicitly set/override y to always be an aggregate count
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

        if self.options.get("is_horizontal"):  # i.e. -H/--horizontal flag
            channels["x"], channels["y"] = (channels["y"], channels["x"])

        return channels

    def finalize_chart(self, chart: Chart) -> Chart:
        # ok, horizontal bar charts are confusing because by default, cvz bar makes a COLUMN chart
        # TK: make cvz column type
        if self.is_horizontal:
            w = chart.get_prop("width")
            h = chart.get_prop("height")
            chart.set_props({"width": h, "height": w})
        return chart
