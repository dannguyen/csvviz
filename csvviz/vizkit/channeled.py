import altair as alt
from altair.utils.schemapi import Undefined as altUndefined
from typing import (
    # Any as AnyType,
    Dict as DictType,
    # List as ListType,
    # Mapping as MappingType,
    # NoReturn as NoReturnType,
    Optional as OptionalType,
    # Tuple as TupleType,
    Union as UnionType,
)

from csvviz.settings import *
from csvviz.exceptions import InvalidDataReference, MissingDataReference


ChannelType = UnionType[alt.X, alt.Y, alt.Fill, alt.Size, alt.Stroke]
ChannelsDictType = DictType[str, ChannelType]

ENCODING_CHANNEL_NAMES = (
    "x",
    "y",
    "fill",
    "size",
    "stroke",
    "facet",
)


class Channeled:
    def build_channels(self) -> ChannelsDictType:
        c = self._create_channels()
        c = self._colorize_channels(c)
        c = self._manage_facets(c)
        c = self._manage_legends(c)
        c = self.finalize_channels(c)
        return c

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

    #####################################################################
    # internal helpers
    #####################################################################
    def _create_channels(self) -> ChannelsDictType:
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
        # TK: this should be more of a command-interface validation, than in channel stuff?
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

    def _colorize_channels(self, channelset: ChannelsDictType) -> ChannelsDictType:
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
