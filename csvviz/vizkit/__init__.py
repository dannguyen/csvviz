from typing import (
    Any as AnyType,
    Callable as CallableType,
    Dict as DictType,
    List as ListType,
    Mapping as MappingType,
    NoReturn as NoReturnType,
    Optional as OptionalType,
    Tuple as TupleType,
    Union as UnionType,
)

TKTYPE = AnyType

import altair as alt
import pandas as pd


from csvviz.helpers import parse_delimited_str
from csvviz.settings import *
from csvviz.vizkit.channeled import Channeled
from csvviz.vizkit.interfaces import ArgFace, ClickFace, ViewFace

Faces = [ArgFace, ClickFace, ViewFace]


class Vizkit(Channeled, *Faces):
    """
    The interface between Click.command, Altair.Chart, and Pandas.dataframe
    """

    # help meta
    viz_commandname = "abstract"
    viz_info = f"""A {viz_commandname} visualization"""  # this should be defined in every subclass
    viz_epilog = ""

    color_channeltype = "fill"  # can be either 'fill' or 'stroke'

    def __init__(self, input_file, kwargs):
        self.validate_kwargs(kwargs)
        self.kwargs = kwargs
        self.warnings = []
        self.input_file = input_file
        self._dataframe = pd.read_csv(self.input_file)

        self.channels = self.build_channels()
        self.chart = self.build_chart()

    @classmethod
    def validate_kwargs(klass, kwargs: dict) -> bool:
        """
        Raise errors/warnings based on the initial kwarg values; implement in each class
        """
        return True

    def build_chart(self) -> alt.Chart:
        """this used to be _build_chart(), because it's a hefty method"""

        def mark_method_foo() -> CallableType:
            return getattr(alt.Chart(self.df), self.mark_method)

        alt.themes.enable(self.theme)
        ch: alt.Chart
        ch = mark_method_foo()
        ch = ch(clip=True)

        if self.is_faceted:
            ch = ch.resolve_axis(x="independent")

        ch = ch.encode(**self.channels)
        ch = ch.properties(**self.style_properties)

        if self.interactive_mode:
            ch = ch.interactive()

        return ch

    #################### prepare
    def finalize_channels(self, channels: TKTYPE) -> TKTYPE:
        """
        The viz-specific channel set up, i.e. the finishing step.

        Each subclass should implement any necessary channel-changing/configuring callbacks here
        """
        return channels

    def finalize_styles(self, styles: dict) -> dict:
        """another abstract class method, to be implemented when necessary by subclasses"""
        return styles

    def _create_styles(self) -> DictType:
        """assumes self.channels has been set, particularly the types of x/y channels"""
        cargs = self.kwargs.copy()

        styles = {}

        # these atts are only set if a value exists
        for att in (
            "height",
            "width",
            "title",
        ):
            if cargs.get(att):
                styles[att] = cargs[att]

        # if cargs.get("title"):
        #     styles["title"] = cargs["title"]

        # determine width
        # _wvar = 'continuousWidth' if self.channels['x']['type'] in ('quantitative', 'temporal') else 'discreteWidth'
        # styles["width"] = cargs[
        #     "chart_width"
        # ]  # if cargs.get('chart_width') else DEFAULT_CHART_WIDTH
        # # _hvar = 'continuousHeight' if self.channels['x']['type'] in ('quantitative', 'temporal') else 'discreteHeight'
        # styles["height"] = cargs[
        #     "chart_height"
        # ]  # if cargs.get('chart_height') else DEFAULT_CHART_HEIGHT

        return styles

    @staticmethod
    def configure_legend(kwargs: DictType) -> OptionalType[DictType]:
        config = {}
        if kwargs["no_legend"]:
            config = None
        else:
            config["orient"] = DEFAULT_LEGEND_ORIENTATION
        return config

        # not needed; Vega already infers title from channel_name, including aggregate
        # config["title"] = channel_name
        # else:
        #     # TODO: let users configure orientation and title...somehow
        #     config["title"] = colname if not kwargs.get("TK-column-title") else colname
        #     if _o := kwargs.get("TK-orientation"):
        #         config["orient"] = _o
        #     else:
        #         config["orient"] = DEFAULT_LEGEND_ORIENTATION

    #####################################################################
    # properties
    @property
    def column_names(self) -> ListType[str]:
        return list(self.df.columns)

    @property
    def df(self) -> pd.DataFrame:
        return self._dataframe

    @property
    def has_custom_colors(self):  # TODO is needed?
        return any(v for v in self.color_kwargs.values())

    @property
    def interactive_mode(self) -> bool:
        return self.kwargs.get("is_interactive")

    @property
    def is_faceted(self) -> bool:
        return True if self.channels.get("facet") else False

    @property
    def mark_method(self) -> str:
        """e.g. 'mark_rect', 'mark_line'"""
        return self.lookup_mark_method(self.viz_commandname)

    @property
    def name(self) -> str:
        return self.viz_commandname

    @property
    def style_properties(self) -> dict:
        _styles = self._create_styles()
        return self.finalize_styles(_styles)

    @property
    def theme(self) -> str:
        return self.kwargs.get("theme")

    ############################################
    ##  TODO: deprecate these
    @property
    def legend_kwargs(self) -> DictType:
        _ARGKEYS = (
            "no_legend",
            "TK-orient",
            "TK-title",
        )
        return {k: self.kwargs.get(k) for k in _ARGKEYS}

    @property
    def output_kwargs(self) -> DictType:
        _ARGKEYS = (
            "to_json",
            "no_preview",
        )
        return {k: self.kwargs.get(k) for k in _ARGKEYS}

    @property
    def color_kwargs(self) -> DictType:
        return {k: self.kwargs.get(k) for k in ("color_list", "color_scheme")}
