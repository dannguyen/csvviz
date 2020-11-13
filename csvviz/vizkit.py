import csv
from io import StringIO
from pathlib import Path
import re


from typing import (
    Any as AnyType,
    Dict as DictType,
    List as ListType,
    Mapping as MappingType,
    NoReturn as NoReturnType,
    Optional as OptionalType,
    Tuple as TupleType,
    Union as UnionType,
)

import altair as alt
from altair.utils import parse_shorthand as alt_parse_shorthand
from altair.utils.schemapi import Undefined as altUndefined
import altair_viewer as altview
import click
import pandas as pd


from csvviz.exceptions import *
from csvviz.helpers import parse_delimited_str
from csvviz.settings import *
from csvviz.vizclick import (
    VizClickCommand,
    general_options_decor,
)  # TODO: general_options_decor should not be knowable here
from csvviz.utils.sysio import (
    clout,
    clerr,
    clexit,
)  # TODO: this should be refactored, vizkit should not know about these

ChannelType = UnionType[alt.X, alt.Y, alt.Fill, alt.Size, alt.Stroke]
ChannelSetType = DictType[str, ChannelType]


MARK_METHOD_LOOKUP = {
    "area": "area",
    "bar": "bar",
    "heatmap": "rect",
    "hist": "bar",
    "line": "line",
    "scatter": "point",
    "abstract": "bar",  # for testing purposes
}

ENCODING_CHANNEL_NAMES = (
    "x",
    "y",
    "fill",
    "size",
    "stroke",
    "facet",
)


class ViewHelpers:
    """a namespace/mixin for functions that output the viz"""

    @staticmethod
    def chart_to_json(chart: alt.Chart) -> str:
        return chart.to_json(indent=2)

    @staticmethod
    def open_chart_in_browser(chart: alt.Chart) -> NoReturnType:
        # a helpful wrapper around altair_viewer.altview
        altview.show(chart)

    def output_chart(self) -> NoReturnType:
        """Send to stdout the desired representation of a chart"""
        if self.output_kwargs["to_json"]:
            clout(self.chart_to_json(self.chart))

    def preview_chart(self) -> UnionType[NoReturnType, bool]:
        if not self.kwargs.get("no_preview"):
            self.open_chart_in_browser(self.chart)
        else:
            return False


class ClickFace:
    """The interface for making a click command, including meta info for generating the help"""

    viz_commandname = "abstract"
    viz_info = f"""A {viz_commandname} visualization"""  # this should be defined in every subclass
    viz_epilog = ""

    @classmethod
    def cmd_wrapper(klass):
        # TODO: this is bad OOP; func should be properly named and in some more logical place
        def func(**kwargs):
            try:
                vk = klass(input_file=kwargs.get("input_file"), kwargs=kwargs)
            except VizValueError as err:
                # TODO: dude what?
                clexit(1, err)
            else:
                vk.output_chart()
                [clerr(f"Warning: {w}") for w in vk.warnings]
                vk.preview_chart()

        return func

    @classmethod
    def register_command(klass):
        command = klass.cmd_wrapper()
        command = click.command(
            cls=VizClickCommand,
            name=klass.viz_commandname,
            help=klass.viz_info,
            epilog=klass.viz_epilog,
        )(command)
        command = general_options_decor(command)
        for decor in klass.COMMAND_DECORATORS:
            command = decor(command)

        return command


class ArgHelpers:
    @staticmethod
    def lookup_mark_method(viz_commandname: str) -> str:
        """
        convenience method that translates our command names, e.g. bar, dot, line, to
        the equivalent in altair
        """
        m = MARK_METHOD_LOOKUP.get(viz_commandname.lower())
        if not m:
            raise ValueError(f"{viz_commandname} is not a recognized viz/chart type")
        else:
            return "mark_%s" % m

    @staticmethod
    def parse_channel_arg(arg: str) -> TupleType[UnionType[str, None]]:
        """
        given an argument like:
            --xvar='id|Product ID'
                return ('id', 'Product ID')
            --yvar='amount'
                eturn ('amount', 'amount')
        """
        shorthand, title = parse_delimited_str(arg, delimiter="|", minlength=2)
        title = title if title else None
        return (
            shorthand,
            title,
        )

    @staticmethod
    def parse_shorthand(
        shorthand: str, data: OptionalType[pd.DataFrame] = None, **kwargs
    ) -> DictType[str, str]:
        return alt_parse_shorthand(shorthand, data, **kwargs)


#####################################################################
# properties
class Props:
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


class Vizkit(ClickFace, Props, ArgHelpers, ViewHelpers):
    """
    The interface between Click.command, Altair.Chart, and Pandas.dataframe
    """

    color_channeltype = "fill"  # can be either 'fill' or 'stroke'

    def __init__(self, input_file, kwargs):
        self.validate_kwargs(kwargs)
        self.kwargs = kwargs
        self.warnings = []
        self.input_file = input_file
        self._dataframe = pd.read_csv(self.input_file)

        self.channels: ChannelSetType = self.build_channels()

    @classmethod
    def validate_kwargs(klass, kwargs: dict) -> bool:
        """
        Raise errors/warnings based on the initial kwarg values; implement in each class
        """
        return True

    def build_channels(self) -> ChannelSetType:
        _channels = self._create_channels()
        _channels = self._colorize_channels(_channels)
        _channels = self._manage_facets(_channels)
        _channels = self._manage_legends(_channels)
        _channels = self.finalize_channels(_channels)
        return _channels

    @property
    def chart(self) -> alt.Chart:
        """this used to be _build_chart(), because it's a hefty method"""
        alt.themes.enable(self.theme)
        chart: alt.Chart = getattr(alt.Chart(self.df), self.mark_method)
        chart = chart(clip=True)

        if self.is_faceted:
            chart = chart.resolve_axis(x="independent")

        chart = chart.encode(**self.channels)
        chart = chart.properties(**self.style_properties)

        if self.interactive_mode:
            chart = chart.interactive()

        return chart

    ##########################################################
    # These are boilerplate methods, unlikely to be subclassed
    ##########################################################

    def _manage_facets(self, channels: dict) -> dict:
        #################################
        # set facets, i.e. grid
        if channels.get("facet"):
            _fc = self.kwargs.get("facetcolumns")  # walrus
            if _fc:  # /walrus
                channels["facet"].columns = _fc

            self.configure_channel_sort(channels["facet"], self.kwargs["facetsort"])

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
                channels[cname].legend = self.configure_legend(self.legend_kwargs)

        return channels

    #################### prepare
    def finalize_channels(self, channels: ChannelSetType) -> ChannelSetType:
        """
        The viz-specific channel set up, i.e. the finishing step.

        Each subclass should implement any necessary channel-changing/configuring callbacks here
        """
        return channels

    def finalize_styles(self, styles: dict) -> dict:
        """another abstract class method, to be implemented when necessary by subclasses"""
        return styles

    #####################################################################
    # internal helpers
    #####################################################################
    def _create_channels(self) -> ChannelSetType:
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
                shorthand, title = self.parse_channel_arg(vartxt)
                ed = self.parse_shorthand(shorthand, data=self.df)

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
                self.configure_channel_sort(channels["order"], _osort)

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

    def _colorize_channels(self, channelset: ChannelSetType) -> ChannelSetType:
        config = {"scheme": self.color_kwargs["color_scheme"] or DEFAULT_COLOR_SCHEME}
        color = channelset.get(self.color_channeltype)
        if not color:
            if self.has_custom_colors:  # but --color-list/--color-scheme was set
                self.warnings.append(
                    f"--colorvar was not specified, so --color-list/--color-scheme is ignored."
                )
        else:
            if self.color_kwargs["color_list"]:
                cx = self.color_kwargs["color_list"]
                config["range"] = [s.strip() for s in cx.split(",")]
                config.pop(
                    "scheme"
                )  # `color_list` kwarg overrides any color_scheme setting

            color.scale = alt.Scale(**config)

        return channelset

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
    def configure_channel_sort(
        channel: ChannelType, sortorder: OptionalType[str]
    ) -> ChannelType:
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

    @staticmethod
    def resolve_channel_name(channel: ChannelType) -> str:
        """TODO: document this"""
        return next(
            (
                getattr(channel, a)
                for a in ("title", "field", "aggregate")
                if getattr(channel, a) != altUndefined
            ),
            altUndefined,
        )
