"""vizkit.py basically"""
import altair as alt
import pandas as pd
from pathlib import Path
from typing import (
    Callable as CallableType,
    Dict as DictType,
    List as ListType,
    NoReturn as NoReturnType,
    Optional as OptionalType,
    Union as UnionType,
)


from csvviz.exceptions import ConflictingArgs
from csvviz.helpers import parse_delimited_str
from csvviz.settings import *
from csvviz.vizkit.channel_group import ChannelGroup
from csvviz.vizkit.chart import Chart
from csvviz.vizkit.dataful import Dataful
from csvviz.vizkit.interfaces import ClickFace, OutputFace


class Vizkit(Dataful, ClickFace, OutputFace):
    """
    The interface between Click.command, Altair.Chart, and Pandas.dataframe
    """

    # help meta
    viz_commandname = "abstract"
    help_info = f"""A {viz_commandname} visualization"""  # this should be defined in every subclass
    help_epilog = ""

    color_channel_name = "fill"  # can be either 'fill' or 'stroke'

    default_chart_height = 400
    default_chart_width = 600

    default_faceted_height = 150
    default_faceted_width = 250

    def __init__(self, input_file: UnionType[str, Path], options: DictType):
        self.warnings = []

        self.validate_options(options)
        self.input_file = input_file
        self._dataframe = pd.read_csv(self.input_file)
        # as of now, input_file is supposed to be a Path/str, but
        # in the edge case that it isn't like for testing, filename needs
        # to be something...        self.filename = self.input_file.name
        self.filename = (
            Path(self.input_file).name
            if isinstance(self.input_file, (str, Path))
            else "[input]"
        )

        self.options = self.set_default_channels_and_options(options)

        ch = self.init_channels()
        self.channels = self.finalize_channels(ch)

        c = self.init_chart()
        self.chart = self.finalize_chart(c)

    @classmethod
    def chart_defaults(klass) -> DictType:
        """
        this exists as a method b/c too lazy to figure out how to make a @chartproperty

        TODO: make it a class variable dict, and do away with klass.default_chart_height etc
        """
        return {
            "chart_height": klass.default_chart_height,
            "chart_width": klass.default_chart_width,
            "faceted_height": klass.default_faceted_height,
            "faceted_width": klass.default_faceted_width,
        }

    def validate_options(self, raw_options: DictType) -> bool:
        """
        At this point, raw_options is basically taken directly from the Command kwargs

        raw_options *can* be modified in place

        Raise errors/warnings based on the initial kwarg values; implement in each class
        """
        if raw_options.get("color_list") and raw_options.get("color_scheme"):
            raise ConflictingArgs(
                "--color-list and --color-scheme cannot both be specified."
            )

        if raw_options.get("color_scheme"):
            if not raw_options.get("colorvar"):
                self.warnings.append(
                    f"--colorvar was not specified, so --color-scheme is ignored."
                )
            else:
                cs = raw_options.get("color_scheme")
                if not self.validate_color_scheme(cs):
                    self.warnings.append(
                        f"Using default color scheme because --color-scheme argument '{cs}' does not seem to be a valid color scheme. Run `csvviz info colorschemes` to get a list of valid color schemes."
                    )
                    raw_options.pop("color_scheme")

        return True

    def set_default_channels_and_options(self, options: dict) -> dict:
        """
        some chart-wide options set to defaults if not provided in command-line options
        """
        opts = options.copy()

        # TK: nah, user shouldn't have to explicitly set title to none to disable this
        # if not opts.get('chart_title'):
        #     opts['chart_title'] = self.filename

        # TODO: move to ChannelGroup?
        # returns a copy  of options, in which:
        #     xvar and yvar, if left blank, are set to the 0 and 1 of dataframe.columns

        for i, v in enumerate(
            (
                "xvar",
                "yvar",
            )
        ):
            if not opts.get(v):
                opts[v] = self.column_names[i]

        return opts

    def init_channels(self) -> ChannelGroup:
        """just a wrapper around ChannelGroup constructor"""
        ch = ChannelGroup(
            options=self.options,
            data=self.df,
            color_channel_name=self.color_channel_name,
        )
        return ch

    def finalize_channels(self, channels: ChannelGroup) -> ChannelGroup:
        """
        The viz-specific channel set up, i.e. the finishing step.

        Each subclass should implement any necessary channel-changing/configuring callbacks here
        """
        return channels

    def init_chart(self) -> Chart:
        """
        instantiate and create a Chart object

        prereqs:
            - self.channels has been set up
            - self.chart_defaults() is defined

        Note: `options` is still just a sloppy grabbag from the command-line arg parser, consider
            refactoring Chart to prevent leaky abstraction
        """
        x = Chart(
            viz_name=self.viz_commandname,
            data=self.df,
            channels=self.channels,
            defaults=self.chart_defaults(),
            options=self.options,
        )
        return x

    def finalize_chart(self, chart: Chart) -> Chart:
        """another abstract class method, to be implemented when necessary by subclasses"""
        return chart
        # chart = chart.set_props({})
        # return chart

    @staticmethod
    def validate_color_scheme(scheme: str) -> str:
        # TK: DRY this schema loading with info.py's use
        # also should be lazy loading, etc.
        core = alt.vegalite.core.load_schema()
        defs = core["definitions"]
        cats = [s["$ref"].split("/")[-1] for s in defs["ColorScheme"]["anyOf"]]
        # e.g. ['Categorical', 'SequentialSingleHue', 'SequentialMultiHue', 'Diverging', 'Cyclical']
        all_schemes = []
        for c in cats:
            all_schemes.extend(defs[c]["enum"])

        return scheme in all_schemes

    def chart_dict(self, **kwargs) -> dict:
        """
        Convert the chart to a dictionary suitable for JSON export
        File:   altair/vegalite/v4/api.py
        """
        return self.chart.to_dict(**kwargs)

    def chart_json(self, **kwargs) -> str:
        """
        The JSON specification of the chart object.
        altair/utils/schemapi.py
        """
        return self.chart.to_json(**kwargs)

    @property
    def mark_name(self) -> str:
        return self.chart.mark_name

    @property
    def name(self) -> str:
        """TK: deprecate this? is it ever used?"""
        return self.viz_commandname

    @property
    def raw_chart(self) -> alt.Chart:
        return self.chart.raw_chart

    @property
    def viz_name(self) -> str:
        return self.viz_commandname
