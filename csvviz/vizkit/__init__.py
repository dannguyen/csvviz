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
from csvviz.vizkit.interfaces import ClickFace, OutputFace


class Vizkit(ClickFace, OutputFace):
    """
    The interface between Click.command, Altair.Chart, and Pandas.dataframe
    """

    # help meta
    viz_commandname = "abstract"
    viz_info = f"""A {viz_commandname} visualization"""  # this should be defined in every subclass
    viz_epilog = ""

    color_channel_name = "fill"  # can be either 'fill' or 'stroke'

    default_chart_height = 400
    default_chart_width = 600

    default_faceted_height = 150
    default_faceted_width = 250

    def __init__(self, input_file: UnionType[str, Path], options: dict):
        self.warnings = []

        self.validate_options(options)
        self.input_file = input_file
        self._dataframe = pd.read_csv(self.input_file)
        self.options = self.set_channel_defaults(options)

        ch = self.init_channels()
        self.channels = self.finalize_channels(ch)

        c = self.init_chart()
        self.chart = self.stylize_chart(c)
        # TK: init_styles/finalize_styles is buried in style_chart

    def validate_options(self, raw_options: dict) -> bool:
        """
        At this point, raw_options is basically taken directly from the Command kwargs

        raw_options *can* be modified in place

        Raise errors/warnings based on the initial kwarg values; implement in each class
        """
        if raw_options.get("color_list") and raw_options.get("color_scheme"):
            raise ConflictingArgs(
                "--color-list and --color-scheme cannot both be specified."
            )

        if raw_options.get("color_list") or raw_options.get("color_scheme"):
            if not raw_options.get("colorvar"):
                self.warnings.append(
                    f"--colorvar was not specified, so --color-list and --color-scheme is ignored."
                )
            elif raw_options.get("color_scheme"):
                cs = raw_options.get("color_scheme")
                if not self.validate_color_scheme(cs):
                    self.warnings.append(
                        f"Using default color scheme because --color-scheme argument '{cs}' does not seem to be a valid color scheme. Run `csvviz info colorschemes` to get a list of valid color schemes."
                    )
                    raw_options.pop("color_scheme")

        return True

    def set_channel_defaults(self, options: dict) -> dict:
        """
        TODO: move to ChannelGroup?
        returns a copy  of options, in which:
            xvar and yvar, if left blank, are set to the 0 and 1 of dataframe.columns
        """
        opts = options.copy()
        for i, v in enumerate(
            (
                "xvar",
                "yvar",
            )
        ):
            if not opts.get(v):
                opts[v] = self.column_names[i]

        return opts

    def init_chart(self) -> alt.Chart:
        """
        instantiate a Chart object and encode its channels

        prereq: self.channels has been set up
        """

        alt.themes.enable(self.theme)
        c: alt.Chart
        c = self.mark_method_foo(clip=True)
        c = c.encode(**self.channels)

        if self.is_faceted:
            c = c.resolve_axis(x="independent")

        if self.interactive_mode:
            c = c.interactive()

        return c

    def init_channels(self) -> ChannelGroup:
        """just a wrapper around ChannelGroup constructor"""
        ch = ChannelGroup(
            options=self.options,
            df=self._dataframe,
            color_channel_name=self.color_channel_name,
        )
        return ch

    def finalize_channels(self, channels: ChannelGroup) -> ChannelGroup:
        """
        The viz-specific channel set up, i.e. the finishing step.

        Each subclass should implement any necessary channel-changing/configuring callbacks here
        """
        return channels

    def stylize_chart(self, chart: alt.Chart) -> alt.Chart:
        styleprops = self.init_styles()
        styleprops = self.finalize_styles(styleprops)

        chart = chart.properties(**styleprops)

        return chart

    def init_styles(self) -> DictType:
        """assumes self.channels has been set, particularly the types of x/y channels"""
        styles = {}

        # TODO: refactor this
        styles["autosize"] = {"type": "pad", "contains": "padding"}

        STYLE_ATTRS = {
            "height": self.default_chart_height,
            "width": self.default_chart_width,
            "title": None,
        }

        # TK messy messy!
        if self.is_faceted:
            STYLE_ATTRS["height"] = self.default_faceted_height
            STYLE_ATTRS["width"] = self.default_faceted_width

        for att, default_val in STYLE_ATTRS.items():
            setval = self.options.get(att)
            if setval == 0 or setval:
                styles[att] = setval
            elif default_val:
                styles[att] = default_val
            else:
                pass
                # do nothing, including don't add :att to styles

        return styles

    def finalize_styles(self, styles: DictType) -> DictType:
        """another abstract class method, to be implemented when necessary by subclasses"""
        return styles

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

    #####################################################################
    # properties
    @property
    def column_names(self) -> ListType[str]:
        return list(self.df.columns)

    @property
    def df(self) -> pd.DataFrame:
        return self._dataframe

    @property
    def interactive_mode(self) -> bool:
        return self.options.get("is_interactive")

    @property
    def is_faceted(self) -> bool:
        """should throw error if accessed before self.channels is set"""
        return True if self.channels.get("facet") else False

    @property
    def mark_method_name(self) -> str:
        """e.g. 'mark_rect', 'mark_line'"""
        return self.lookup_mark_method(self.viz_commandname)

    @property
    def mark_method_foo(self) -> CallableType:
        return getattr(alt.Chart(self.df), self.mark_method_name)

    @property
    def name(self) -> str:
        return self.viz_commandname

    @property
    def theme(self) -> str:
        return self.options.get("theme")

    # TK: untested props; maybe should be methods?
    @property
    def chart_dict(self) -> dict:
        """
        Convert the chart to a dictionary suitable for JSON export
        File:   altair/vegalite/v4/api.py
        """
        return self.chart.to_dict()

    @property
    def chart_json(self) -> str:
        """
        The JSON specification of the chart object.
        altair/utils/schemapi.py
        """
        return self.chart.to_json(indent=2, sort_keys=False, validate=True)
