import csv
from io import StringIO
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
from altair.utils.schemapi import Undefined as altUndefined
import altair_viewer as altview
import click
import pandas as pd


from csvviz.exceptions import *
from csvviz.settings import *
from csvviz.utils.cmd import (
    MyCliCommand,
    general_options_decor,
)  # TODO: general_options_decor should not be knowable here
from csvviz.utils.sysio import (
    clout,
    clerr,
    clexit,
)  # TODO: this should be refactored, vizkit should not know about these

typeChannel = typeUnion[alt.X, alt.Y, alt.Fill, alt.Size, alt.Stroke]
typeChannelSet = typeDict[str, typeChannel]

ENCODING_CHANNEL_NAMES = (
    "x",
    "y",
    "fill",
    "size",
    "stroke",
    "facet",
)


class VizkitViewMixin:
    """
    a namespace/mixin for functions that output the viz
    """

    @staticmethod
    def chart_to_json(chart: alt.Chart) -> str:
        return chart.to_json(indent=2)

    @staticmethod
    def open_chart_in_browser(chart: alt.Chart) -> typeNoReturn:
        # a helpful wrapper around altair_viewer.altview
        altview.show(chart)

    def output_chart(self, oargs={}) -> typeNoReturn:
        """
        Send to stdout the desired representation of a chart
        """
        # --interactive/--static chart is independent of whether or not we're previewing it,
        #  which is reflected in its JSON representation
        # echo JSON before doing a preview
        oargs = self.output_kwargs if not oargs else oargs
        if oargs["to_json"]:
            clout(self.chart_to_json(self.chart))

    def preview_chart(self) -> typeUnion[typeNoReturn, bool]:
        if not self.kwargs.get("no_preview"):
            self.open_chart_in_browser(self.chart)
        else:
            return False


class VizkitCommandMixin:
    viz_commandname = "abstract"

    viz_info = f"""A {viz_commandname} visualization"""  # this should be defined in every subclass
    viz_epilog = ""

    @staticmethod
    def _basecommand(klass):
        def _foo(**kwargs):
            try:
                vk = klass(input_file=kwargs.get("input_file"), kwargs=kwargs)
            except VizValueError as err:
                clexit(1, err)
            else:
                vk.output_chart()
                for w in vk.warnings:
                    clerr(f"Warning: {w}")
                vk.preview_chart()

        return _foo

    @classmethod
    def register_command(klass):
        # TODO: this is bad OOP; _foo should be properly named and in some more logical place
        command = klass._basecommand(klass)
        command = click.command(
            cls=MyCliCommand,
            name=klass.viz_commandname,
            help=klass.viz_info,
            epilog=klass.viz_epilog,
        )(command)
        command = general_options_decor(command)
        for decor in klass.COMMAND_DECORATORS:
            command = decor(command)

        return command

    @staticmethod
    def lookup_mark_method(viz_commandname: str) -> alt.Chart:
        """
        convenience method that translates our command names, e.g. bar, dot, line, to
        the equivalent in altair
        """
        vname = viz_commandname.lower()

        if vname in (
            "area",
            "bar",
            "line",
        ):
            m = f"mark_{vname}"
        elif vname == "hist":
            m = "mark_bar"
        elif vname == "scatter":
            m = "mark_point"
        elif vname == "abstract":
            m = "mark_bar"  # for testing purposes
        else:
            raise ValueError(f"{viz_commandname} is not a recognized viz/chart type")
        return m

    @staticmethod
    def parse_var_str(var: str) -> typeTuple[typeUnion[str, None]]:
        """
        given an argument like:
            --xvar='id|Product ID', return ('id', 'Product ID')
            --yvar='amount', return ('amount', 'amount')
        """
        x = next(csv.reader(StringIO(var), delimiter="|"))
        if len(x) == 1:
            x.append(None)
        elif not x[1]:
            x[1] = None
        return tuple(x)


class Vizkit(VizkitCommandMixin, VizkitViewMixin):
    """
    The interface between Click.command, Altair.Chart, and Pandas.dataframe
    """

    def __init__(self, input_file, kwargs):
        self.kwargs = kwargs
        self.warnings = []

        self.input_file = input_file
        self._dataframe = pd.read_csv(self.input_file)
        # TODO: too many properties?
        self.interactive_mode = self.kwargs.get("is_interactive")
        self.theme = kwargs.get("theme")

        _channels = self._create_channels()
        _channels = self._manage_facets(_channels)
        _channels = self._manage_legends(_channels)
        _channels = self.finalize_channels(_channels)
        self.channels = _channels

        _styles = self._create_styles()
        self.style_properties = self.finalize_styles(_styles)

        self.chart = self.build_chart()

    ##########################################################
    # These are boilerplate methods, unlikely to be subclassed
    ##########################################################
    # def build_chart(
    #     self, channels: dict, style_properties: dict, interactive_mode: bool
    # ) -> alt.Chart:
    def build_chart(self) -> alt.Chart:
        chart = self._create_chart()
        # TODO: _set_chart_axes is only here b/c no better place to put it yet

        chart = self._set_chart_axes(chart)
        chart = chart.encode(**self.channels)
        chart = chart.properties(**self.style_properties)

        if self.interactive_mode:
            chart = chart.interactive()

        return chart

    def _manage_facets(self, channels: dict) -> dict:
        #################################
        # set facets, i.e. grid
        if channels.get("facet"):
            _fc = self.kwargs.get("facetcolumns")  # walrus
            if _fc:  # /walrus
                channels["facet"].columns = _fc

            self._config_channel_sort(channels["facet"], self.kwargs["facetsort"])

        return channels

    def _manage_legends(self, channels: dict) -> dict:
        """

        TODO: no idea where to put this, other than to make it an internal method used by build_chart()
        """
        for cname in (
            "fill",
            "size",
            "stroke",
        ):
            if channels.get(cname):
                channels[cname].legend = self._config_legend(self.legend_kwargs)

        return channels

    #################### prepare
    def finalize_channels(self, channels: typeChannelSet) -> typeChannelSet:
        """
        The viz-specific channel set up, i.e. the finishing step.

        Each subclass should implement any necessary channel-changing/configuring callbacks here
        """
        return channels

    def finalize_styles(self, styles: dict) -> dict:
        """another abstract class method, to be implemented when necessary by subclasses"""
        return styles

    def _set_chart_axes(self, chart) -> alt.Chart:
        """
        expects self.chart and self.channels to have been initialized; alters alt.chart inplace

        TODO: no idea where to put this, other than to make it an internal method used by build_chart()

        """
        if self.channels.get("facet"):
            chart = chart.resolve_axis(x="independent")
        return chart

    #####################################################################
    # internal helpers
    #####################################################################
    def _create_channels(self) -> typeChannelSet:
        def _set_default_xyvar_args(kargs) -> dict:
            """
            configure x and y channels, which default to 0 and 1-indexed column
            if names aren't specified
            """
            cargs = kargs.copy()
            for i, z in enumerate(("xvar", "yvar")):
                cargs[z] = cargs[z] if cargs.get(z) else self.column_names[i]
            return cargs

        def _validate_fieldname(shorthand: str, fieldname: str) -> bool:
            if fieldname not in self.column_names:
                return False
            else:
                return True

        cargs = _set_default_xyvar_args(self.kwargs)
        channels = {}

        for n in ENCODING_CHANNEL_NAMES:
            argname = f"{n}var"
            vartxt = cargs.get(argname)  # walrus
            if vartxt:  # e.g. 'name', 'amount|Amount', 'sum(amount)|Amount'  # /walrus
                shorthand, title = self.parse_var_str(vartxt)
                ed = parse_shorthand(shorthand, data=self.df)

                if _validate_fieldname(shorthand=shorthand, fieldname=ed["field"]):
                    _channel = getattr(alt, n.capitalize())  # e.g. alt.X or alt.Y
                    channels[n] = _channel(**ed)
                    if title:
                        channels[n].title = title
                else:
                    raise InvalidDataReference(
                        f"""'{shorthand}' is either an invalid column name, or invalid Altair shorthand"""
                    )

        ##################################
        # subfunction: --color-sort, i.e. ordering of fill; only valid for area and bar charts
        # somewhat confusingly, sort by fill does NOT alter alt.Fill, but adds an Order channel
        # https://altair-viz.github.io/user_guide/encoding.html?#ordering-marks
        _osort = cargs.get("fillsort")  # walrus
        if _osort:  # /walrus
            if not channels.get("fill"):
                raise MissingDataReference(
                    f"--color-sort '{_osort}' was specified, but no --colorvar value was provided"
                )
            else:
                # create an 'order' channel, with sort attribute
                fname = self.resolve_channel_name(channels["fill"])
                channels["order"] = alt.Order(fname)
                self._config_channel_sort(channels["order"], _osort)

        ##################################
        # subfunction: set limits of x-axis and y-axis, via --xlim and --ylim
        for i in (
            "x",
            "y",
        ):
            j = f"{i}lim"
            limstr = cargs.get(j)  # walrus
            if limstr:  # /walrus
                channels[
                    i
                ].scale = (
                    alt.Scale()
                )  # if channels[i].scale == alt.Undefined else channels[i].scale
                _min, _max = [k.strip() for k in limstr.split(",")]
                channels[i].scale.domain = [_min, _max]

        return channels

    def _create_chart(self) -> alt.Chart:
        alt.themes.enable(self.theme)

        chartfoo = getattr(alt.Chart(self.df), self.mark_type)
        return chartfoo(clip=True)

    def _create_styles(self) -> typeDict:
        cargs = self.kwargs.copy()

        styles = {}
        if cargs.get("title"):
            styles["title"] = cargs["title"]

        return styles

    def _set_channel_colorscale(self, channelvar: str, channels: dict) -> typeNoReturn:
        """
        Given a channelvar, e.g. 'fill', 'stroke'

        Check self.channels[channelvar] to see if it's been created

        If so, modify self.channels[channelvar].range

        If not, do nothing, but issue a warning that self.channels[channelvar] was expected

        """
        ## fill color stuff
        #         channel = self.channels.get(channelvar)
        colorargs = {
            k: self.kwargs[k]
            for k in (
                "colors",
                "color_scheme",
            )
            if self.kwargs.get(k)
        }

        channel = channels.get(channelvar)  # walrus

        if channel:  # /walrus
            config = {"scheme": DEFAULT_COLOR_SCHEME}
            if colorargs:
                _cs = colorargs.get("color_scheme")  # walrus
                if _cs:  # /walrus
                    config["scheme"] = _cs
                    # TODO: if _cs does not match a valid color scheme, then raise a warning/error

                _cx = colorargs.get("colors")  # walrus

                if _cx:  # /walrus
                    # don't think this needs to be a formal parser
                    config["range"] = _cx.strip().split(",")
                    # for now, only colors OR color_scheme can be set, not both
                    config.pop("scheme", None)
            channel.scale = alt.Scale(**config)
        else:  # optional expected channel is not present
            if colorargs:  # but color settings were present
                self.warnings.append(
                    f"The {channelvar} variable was not specified, so colors/color_scheme is ignored."
                )

    #####################################################################
    # properties
    @property
    def name(self) -> str:
        return self.viz_commandname

    @property
    def mark_type(self) -> str:
        return self.lookup_mark_method(self.viz_commandname)

    @property
    def df(self) -> pd.DataFrame:
        return self._dataframe

    @property
    def column_names(self) -> typeList[str]:
        return list(self.df.columns)

    #####################################################################
    #  kwarg properties
    #  TODO: refactor later
    @property
    def channel_kwargs(self) -> typeDict:
        # TODO: handling facet stuff here is BAD
        _ARGKEYS = [f"{n}var" for n in ENCODING_CHANNEL_NAMES]
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
            "no_legend",
            "TK-orient",
            "TK-title",
        )
        return {k: self.kwargs.get(k) for k in _ARGKEYS}

    @property
    def output_kwargs(self) -> typeDict:
        _ARGKEYS = (
            "to_json",
            "no_preview",
        )
        return {k: self.kwargs.get(k) for k in _ARGKEYS}

    # Not needed if there are no other interactive-like attributes
    # @property
    # def render_kwargs(self) -> typeDict:
    #     _ARGKEYS = ('is_interactive',)
    #     return {k: self.kwargs.get(k) for k in _ARGKEYS}

    # @property
    # def sorting_kwargs(self) -> typeDict:
    #     _ARGKEYS = ("sortx_var",)
    #     return {k: self.kwargs.get(k) for k in _ARGKEYS}

    @property
    def styling_kwargs(self) -> typeDict:
        _ARGKEYS = ("title",)
        return {k: self.kwargs.get(k) for k in _ARGKEYS}

    #####################################################################
    ##### chart aspect configurations (static helper methods)

    @staticmethod
    def _config_channel_sort(
        channel: typeChannel, sortorder: typeUnion[str, None]
    ) -> typeChannel:
        """inplace modification of channel"""
        if sortorder:  # /walrus
            if sortorder == "asc":
                channel.sort = "ascending"
            elif sortorder == "desc":
                channel.sort = "descending"
            else:
                raise ValueError(f"Invalid sort order term: {sortorder}")
        return channel

    @staticmethod
    def _config_legend(kwargs: typeDict) -> typeUnion[typeDict, bool]:

        config = {}
        if kwargs["no_legend"]:
            config = None
        else:
            config["orient"] = DEFAULT_LEGEND_ORIENTATION
            # not needed; Vega already infers title from channel_name, including aggregate
            # config["title"] = channel_name
        # else:
        #     # TODO: let users configure orientation and title...somehow
        #     config["title"] = colname if not kwargs.get("TK-column-title") else colname
        #     if _o := kwargs.get("TK-orientation"):
        #         config["orient"] = _o
        #     else:
        #         config["orient"] = DEFAULT_LEGEND_ORIENTATION
        return config

    @staticmethod
    def resolve_channel_name(
        channel: typeUnion[alt.X, alt.Y, alt.Fill, alt.Size]
    ) -> str:
        return next(
            (
                getattr(channel, a)
                for a in ("title", "field", "aggregate")
                if getattr(channel, a) != altUndefined
            ),
            altUndefined,
        )
