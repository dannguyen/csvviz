"""TODO/in progress: ChannelGroup subsumes/simplifies what's in Channeled.py"""

import altair as alt
from altair.utils.schemapi import Undefined as altUndefined
from altair.utils import parse_shorthand as alt_parse_shorthand
import pandas as pd
from typing import (
    Dict as DictType,
    List as ListType,
    Optional as OptionalType,
    Tuple as TupleType,
    Union as UnionType,
)

from csvviz.exceptions import InvalidDataReference
from csvviz.helpers import parse_delimited_str
from csvviz.settings import DEFAULT_COLOR_SCHEME, DEFAULT_LEGEND_ORIENTATION


CHANNELS = {
    "x": alt.X,
    "y": alt.Y,
    "facet": alt.Facet,
    "fill": alt.Fill,
    "stroke": alt.Stroke,
    "size": alt.Size,
    "order": alt.Order,  # bar/area
}


ChannelType = UnionType[tuple(CHANNELS.values())]
ChannelsDictType = DictType[str, ChannelType]


class Helpers:
    def get_data_field(self, channelname: str) -> str:
        """
        given channelname, e.g. 'x', 'y', 'fill', 'stroke'
            return the associated field name
        Note: this method used to be more complicated, but now is trivial
        """
        return self[channelname].field

        # TK/TODO: not sure about the use cases in which this should return
        # `aggregate(fieldname)`...so this stuff below is deprecated and was buggy anyway...
        # NAMEFIELDS = (
        #     "field",
        #     "aggregate",
        # )
        # channel = self[channelname]
        # candidates = (
        #     getattr(channel, NAME)
        #     for NAME in NAMEFIELDS
        #     if getattr(channel, NAME) != altUndefined
        # )
        # return next(candidates)

    @staticmethod
    def configure_legend(kwargs: DictType) -> OptionalType[DictType]:
        config = {}
        if kwargs["no_legend"]:
            config = None
        else:
            config["orient"] = DEFAULT_LEGEND_ORIENTATION
        return config
        # TODO: explicitly set title; figure out how Altair devises the default title

    @staticmethod
    def parse_channel_arg(arg: str) -> TupleType[OptionalType[str]]:
        """
        given an argument like:
            --xvar='id|Product ID' => ('id', 'Product ID')
            --yvar='amount' => return ('amount', 'amount')
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


class ChannelGroup(dict, Helpers):
    """
    Equivalent to:
            cgroup =  {
                "x": alt.X('name'),
                "y": 'amount',
                "fill": alt.Color('amount', scale=alt.Scale(range=['green', 'yellow', 'red']
            )
            alt.Chart(df).mark_bar().encode(**cgroup))

    options: the processed keyword arguments from the click command
    df: the viz's dataframe
    color_channel: either 'fill' or 'stroke'
    """

    def __init__(
        self,
        options: dict,
        df: pd.DataFrame,
        color_channel_name: OptionalType[str] = None,
    ):
        self.options = options  # i.e. "kwargs"
        self.df = df
        self.color_channel_name = color_channel_name

        self.scaffold().colorize().facetize().legendize().limitize()

    def __eq__(self, other):
        """Overrides the default implementation"""
        return {k: self[k] for k in CHANNELS.keys() if self.get(k)}

    # @property
    # def channels(self) -> ChannelsDictType:
    #     return {k: v for k, v in self._channels.items() if v}

    @property
    def color_channel(self) -> OptionalType[UnionType[alt.Fill, alt.Stroke]]:
        if not self.color_channel_name:
            return None
        else:
            return self.get(self.color_channel_name)

    @property
    def column_names(self) -> ListType[str]:
        return self.df.columns

    def scaffold(self) -> "ChannelGroup":
        # at this point, options['colorvar'] is set (via Click interface), but NOT
        #  options['fillvar']/options['strokevar']/etc
        # so we (messily) inject it into a copy of the self.options dict (don't want to alter original tho...)
        # TK: seems like spaghetti but whatever...
        _opts = self.options.copy()
        colarg = _opts.get("colorvar")
        if colarg:
            _opts["%svar" % self.color_channel_name] = colarg

        for cname, Ch in CHANNELS.items():
            karg = _opts.get(f"{cname}var")
            if karg:
                shorthand, title = self.parse_channel_arg(karg)
                chargs = self.parse_shorthand(shorthand, data=self.df)
                if chargs["field"] not in self.column_names:
                    raise InvalidDataReference(
                        f"""'{shorthand}' is either an invalid column name, or invalid Altair shorthand"""
                    )
                if title:
                    chargs["title"] = title
                self[cname] = Ch(**chargs)

        return self

    def colorize(self) -> "ChannelGroup":
        """
        this method operates under the assumption that either/or fill and stroke can be
          colored, i.e. nothing else and NOT both
        """
        if not self.color_channel:
            return self

        config = {"scheme": self.options.get("color_scheme") or DEFAULT_COLOR_SCHEME}
        if self.options.get("color_list"):
            config["range"] = [s.strip() for s in self.options["color_list"].split(",")]
            # color_list` kwarg overrides any color_scheme setting
            config.pop("scheme")

        self.color_channel.scale = alt.Scale(**config)
        return self

    def facetize(self) -> "ChannelGroup":
        # set facets, i.e. grid
        fc = self.get("facet")
        if fc:
            if self.options.get("facetcolumns"):
                fc.columns = self.options["facetcolumns"]

            xo = self.options.get("facetsort")
            # TODO: DRY self.configure_channel_sort(channels["facet"], self.kwargs["facetsort"])
            if xo:
                if xo == "asc":
                    fc.sort = "ascending"
                elif xo == "desc":
                    fc.sort = "descending"
                else:
                    raise ValueError(f"Invalid sort order term: {xo}")

        return self

    def legendize(self) -> "ChannelGroup":
        config = {"orient": DEFAULT_LEGEND_ORIENTATION}
        for cname in ("fill", "size", "stroke"):
            channel = self.get(cname)
            if channel:
                if self.options.get("no_legend"):
                    channel.legend = None
                else:
                    channel.legend = alt.Legend(**config)

        return self

    def limitize(self) -> "ChannelGroup":
        """
        by now, self['x'] and self['y'] are expected to be set
        """
        LIMS = (
            "xlim",
            "ylim",
        )
        for L in LIMS:
            limarg = self.options.get(L)
            lvar = L[0]  # e.g. 'x', 'y'
            if limarg:
                _min, _max = [a.strip() for a in limarg.split(",")]
                self[lvar].scale = alt.Scale(domain=[_min, _max])

        return self
