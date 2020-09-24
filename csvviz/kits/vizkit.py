from pathlib import Path
import re

from typing import (
    Any as typeAny,
    Callable as typeCallable,
    Dict as typeDict,
    IO as typeIO,
    List as typeList,
    Mapping as typeMapping,
    NoReturn as typeNoReturn,
    Tuple as typeTuple,
    Union as typeUnion,
)


import altair as alt
import altair_viewer as altview
import pandas as pd

from csvviz.cli_utils import clout, clerr
from csvviz.exceptions import *
from csvviz.kits.datakit import Datakit
from csvviz.settings import *


def get_chart_mark_methodname(viz_type: str) -> alt.Chart:
    """
    convenience method that translates our command names, e.g. bar, dot, line, to
    the equivalent in altair
    """
    vname = viz_type.lower()

    if vname in ("area", "bar", "line",):
        m = f"mark_{vname}"
    elif vname == "scatter":
        m = "mark_point"
    else:
        raise ValueError(f"{viz_type} is not a recognized viz/chart type")
    return m


def preview_chart(chart: alt.Chart) -> typeNoReturn:
    # a helpful wrapper around altair_viewer.altview
    altview.show(chart)


class Vizkit(object):
    """
    The interface between Click.command, Altair.Chart, and Pandas.dataframe
    """

    def __init__(self, viz_type: str, input_file: typeUnion[typeIO, Path, str], kwargs):
        self.kwargs = kwargs
        self.input_file = input_file
        self.datakit = Datakit(input_file)

        # chart-related settings
        self.viz_type = viz_type
        self.theme = kwargs.get("theme")
        self.channels = self.declare_channels()
        self.style_properties = self.declare_styles()
        self.interactive_mode = self.kwargs.get("is_interactive")

        # the chart itself
        self.chart = self.build_chart(
            channels=self.channels,
            style_properties=self.style_properties,
            interactive_mode=self.interactive_mode,
        )

    def build_chart(
        self, channels: dict, style_properties: dict, interactive_mode: bool
    ) -> alt.Chart:

        chart = self._init_chart()
        chart = chart.encode(**channels)
        chart = chart.properties(**style_properties)

        if interactive_mode:
            chart = chart.interactive()

        return chart
        # implementing this for testing ease...
        # raise Exception('Need to implement build_chart for each viz subclass')

    def declare_channels(
        self,
    ) -> typeDict[str, typeUnion[alt.X, alt.Y, alt.Fill, alt.Size]]:
        """
        TK TODO:
        _config_channels seems like the better name, though we're using that
        for the more general/basic initializations (maybe it should be _init_channels?)

        This method does the bespoke work to combine channels with legends/colors/etc
        and should be implemented in every subclass
        """

        channels = self._init_channels(self.channel_kwargs, self.datakit)

        if self.kwargs.get("flipxy"):
            channels["x"], channels["y"] = (channels["y"], channels["x"])

        if _fill := channels.get("fill"):
            _fill.scale = alt.Scale(**self._config_colors(self.color_kwargs))
            # _fill.legend = alt.Legend(title='mah legend', orient='bottom')
            _legend = self._config_legend(self.legend_kwargs, colname=_fill.shorthand)
            if _legend is False:  # then hide_legend was explicitly specified
                _fill.legend = None
            else:
                _fill.legend = _legend

        if _sort_config := self._config_sorting(self.kwargs, self.datakit):
            channels["x"].sort = _sort_config

        return channels

    def declare_styles(self) -> typeDict:
        return self._config_styles(self.kwargs)

    def output_chart(self, oargs={}) -> typeNoReturn:
        # --interactive/--static chart is independent of whether or not we're previewing it,
        #  which is reflected in its JSON representation
        # echo JSON before doing a preview

        oargs = self.output_kwargs if not oargs else oargs

        if oargs["to_json"]:
            clout(self.chart.to_json(indent=2))

        if oargs["do_preview"]:
            preview_chart(self.chart)

    #####################################################################
    # internal helpers

    def _init_channels(
        self, kwargs: typeDict, datakit
    ) -> typeDict[str, typeUnion[alt.X, alt.Y, alt.Fill, alt.Size]]:
        channels = {}

        # configure x and y channels, which default to 0 and 1-indexed column
        # if names aren't specified
        for i, n in enumerate(("x", "y",)):
            _arg = f"{n}var"
            _v = kwargs[_arg] if kwargs[_arg] else datakit.column_names[i]
            vname, _z = datakit.resolve_column(_v)
            channels[n] = getattr(alt, n.capitalize())(vname)

        for n in (
            "fill",
            "size",
        ):
            _arg = f"{n}var"
            if _v := kwargs.get(_arg):
                vname, _z = datakit.resolve_column(_v)
                channels[n] = getattr(alt, n.capitalize())(vname)

        return channels

    def _init_chart(self) -> alt.Chart:
        alt.themes.enable(self.theme)

        chartfoo = getattr(alt.Chart(self.df), self.mark_type)
        return chartfoo()


    #####################################################################
    # properties
    @property
    def name(self) -> str:
        return self.viz_type

    @property
    def mark_type(self) -> str:
        return get_chart_mark_methodname(self.viz_type)

    @property
    def df(self) -> pd.DataFrame:
        return self.datakit.df

    @property
    def column_names(self) -> typeList[str]:
        return list(self.df.columns)

    #####################################################################
    #  kwarg properties
    #  TODO: refactor later
    @property
    def channel_kwargs(self) -> typeDict:
        _ARGKEYS = (
            "xvar",
            "yvar",
            "fillvar",
            "sizevar",
        )
        return {k: self.kwargs.get(k) for k in _ARGKEYS}

    @property
    def color_kwargs(self) -> typeDict:
        _ARGKEYS = (
            "color_scheme",
            "colors",
        )
        return {k: self.kwargs.get(k) for k in _ARGKEYS}

    @property
    def legend_kwargs(self) -> typeDict:
        _ARGKEYS = (
            "hide_legend",
            "TK-orient",
            "TK-title",
        )
        return {k: self.kwargs.get(k) for k in _ARGKEYS}

    @property
    def output_kwargs(self) -> typeDict:
        _ARGKEYS = (
            "to_json",
            "do_preview",
        )
        return {k: self.kwargs.get(k) for k in _ARGKEYS}

    # Not needed if there are no other interactive-like attributes
    # @property
    # def render_kwargs(self) -> typeDict:
    #     _ARGKEYS = ('is_interactive',)
    #     return {k: self.kwargs.get(k) for k in _ARGKEYS}

    @property
    def sorting_kwargs(self) -> typeDict:
        _ARGKEYS = ("sortx_var",)
        return {k: self.kwargs.get(k) for k in _ARGKEYS}

    @property
    def styling_kwargs(self) -> typeDict:
        _ARGKEYS = ("title",)
        return {k: self.kwargs.get(k) for k in _ARGKEYS}

    #####################################################################
    ##### chart aspect configurations (static helper methods)

    @staticmethod
    def _config_colors(kwargs: typeDict) -> typeDict:
        """
        returns a dict for alt.Scale()
        """
        ## fill color stuff
        config = {"scheme": DEFAULT_COLOR_SCHEME}

        if _cs := kwargs.get("color_scheme"):
            config["scheme"] = _cs
            # TODO: if _cs does not match a valid color scheme, then raise a warning/error

        if _colortxt := kwargs["colors"]:
            # don't think this needs to be a formal parser
            config["range"] = _colortxt.strip().split(",")
            # for now, only colors OR color_scheme can be set, not both
            config.pop("scheme", None)

        return config

    @staticmethod
    def _config_legend(kwargs: typeDict, colname: str) -> typeUnion[typeDict, bool]:
        config = {}
        if kwargs["hide_legend"]:
            config = False
        else:
            # TODO: let users configure orientation and title...somehow
            config["title"] = colname if not kwargs.get("TK-column-title") else colname
            if _o := kwargs.get("TK-orientation"):
                config["orient"] = _o
            else:
                config["orient"] = DEFAULT_LEGEND_ORIENTATION

        return config

    @staticmethod
    def _config_sorting(kwargs: typeDict, datakit: Datakit) -> typeDict:
        config = {}
        if _sortx := kwargs.get("sortx_var"):
            _sign, _cname = re.match(r"(-?)(.+)", _sortx).groups()
            colname, _z = datakit.resolve_column(_cname)  # mostly validation

            config["field"] = colname
            config["order"] = "descending" if _sign == "-" else "ascending"

        return config

    @staticmethod
    def _config_styles(kwargs: typeDict) -> typeDict:
        config = {}

        if _title := kwargs.get("title"):
            config["title"] = _title

        return config
