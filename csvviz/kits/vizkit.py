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
from altair.utils import parse_shorthand
import altair_viewer as altview
import pandas as pd

from csvviz.cli_utils import clout, clerr
from csvviz.exceptions import *
from csvviz.kits.datakit import Datakit
from csvviz.settings import *

ENCODING_CHANNEL_NAMES = ("x", "y", "fill", "size",)



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

        # TODO: too many properties?
        # chart-related settings
        self.viz_type = viz_type
        self.theme = kwargs.get("theme")
        self.channels = self.prepare_channels()
        self.style_properties = self.prepare_styles()
        self.interactive_mode = self.kwargs.get("is_interactive")

        # the chart itself
        self.chart = self.build_chart(
            channels=self.channels,
            style_properties=self.style_properties,
            interactive_mode=self.interactive_mode,
        )


    def prepare_styles(self) -> typeDict:
        return self._config_styles(self.kwargs)

    def prepare_channels(
        self,
    ) -> typeDict[str, typeUnion[alt.X, alt.Y, alt.Fill, alt.Size]]:
        """
        TK TODO:
        prepare_channels is the better name
        # TODO: this should be an abstract method in the base class, but for now, it's
        #   an obsolete version of Barkit

        This method does the bespoke work to combine channels with legends/colors/etc
        and should be implemented in every subclass
        """

        channels = self._init_channels(self.channel_kwargs, self.datakit)

        if self.kwargs.get("flipxy"):
            channels["x"], channels["y"] = (channels["y"], channels["x"])

        if _fill := channels.get("fill"):
            _fill.scale = alt.Scale(**self._config_colors(self.color_kwargs))


            _legend = self._config_legend(self.legend_kwargs, colname=_fill.field)
            if _legend is False:  # then hide_legend was explicitly specified
                _fill.legend = None
            else:
                _fill.legend = _legend

        if _sort_config := self._config_sorting(self.kwargs, self.datakit):
            channels["x"].sort = _sort_config

        return channels



    ##########################################################
    # These are boilerplate methods, unlikely to be subclassed
    ##########################################################
    def build_chart(
        self, channels: dict, style_properties: dict, interactive_mode: bool
    ) -> alt.Chart:

        chart = self._init_chart()
        chart = chart.encode(**channels)

        # # import IPython; IPython.embed()
        # try:
        #     chart.to_dict(validate=True) # just triggering validation; we don't use the dict
        # except ValueError as err:
        #     msg = str(err).replace('ValueError', 'InvalidColumnName')
        #     raise InvalidColumnName(msg)

        chart = chart.properties(**style_properties)

        if interactive_mode:
            chart = chart.interactive()

        return chart
        # implementing this for testing ease...
        # raise Exception('Need to implement build_chart for each viz subclass')


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
    #####################################################################
    def _init_channels(
        self, kwargs:typeDict, datakit
    ) -> typeDict[str, typeUnion[alt.X, alt.Y, alt.Fill, alt.Size]]:

        def _validate_fieldname(shorthand:str, fieldname:str) -> bool:
            if fieldname not in self.column_names:
                return False
            else:
                return True

        channels = {}
        # configure x and y channels, which default to 0 and 1-indexed column
        # if names aren't specified

        cargs = kwargs.copy()
        for i, n in enumerate(("xvar", "yvar",)):
            # TODO: this kind of rickety tbh
            #   colstr can be either a column name or Altair's shorthand syntax, e.g. 'sum(amount):Q'
            #   if kwargs['xvar/yvar'] isn't defined, then pull 0/1 index from column_names
            cargs[n] = cargs[n] if cargs[n] else self.column_names[i]


        for n in ENCODING_CHANNEL_NAMES:
            argname = f"{n}var"
            if shorthand := cargs[argname]:
                ed = parse_shorthand(shorthand, data=self.df)

                if _validate_fieldname(shorthand=shorthand, fieldname=ed['field']):
                    _channel = getattr(alt, n.capitalize()) # e.g. alt.X or alt.Y
                    channels[n] = _channel(**ed)
                else:
                    raise InvalidColumnName(f"""'{shorthand}' is either an invalid column name, or invalid Altair shorthand""")
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
        _ARGKEYS = [f'{n}var' for n in ENCODING_CHANNEL_NAMES]
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
    def _config_legend(kwargs:typeDict, colname:str) -> typeUnion[typeDict, bool]:
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
