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
}


ChannelType = UnionType[tuple(CHANNELS.values())]
ChannelsDictType = DictType[str, ChannelType]


class ChannelGroup(dict):
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
        self, options: dict, df: pd.DataFrame, color_channel: OptionalType[str] = None
    ):
        self.options = options  # i.e. "kwargs"
        self.df = df
        self.color_channel_str = color_channel

        self.create().colorize().facetize().legendize()

    def __eq__(self, other):
        """Overrides the default implementation"""
        return {k: self[k] for k in CHANNELS.keys() if self.get(k)}

    # @property
    # def channels(self) -> ChannelsDictType:
    #     return {k: v for k, v in self._channels.items() if v}

    @property
    def color_channel(self) -> OptionalType[UnionType[alt.Fill, alt.Stroke]]:
        if not self.color_channel_str:
            return None
        else:
            return self.get(self.color_channel_str)

    @property
    def column_names(self) -> ListType[str]:
        return self.df.columns

    def create(self) -> "ChannelGroup":
        for cname, channel in CHANNELS.items():
            karg = self.options.get(f"{cname}var")
            if karg:
                shorthand, title = self.parse_channel_arg(karg)
                chargs = self.parse_shorthand(shorthand, data=self.df)
                if chargs["field"] not in self.column_names:
                    raise InvalidDataReference(
                        f"""'{shorthand}' is either an invalid column name, or invalid Altair shorthand"""
                    )
                if title:
                    chargs["title"] = title
                self[cname] = channel(**chargs)

        return self

    def colorize(self) -> "ChannelGroup":
        """
        this method operates under the assumption that either/or fill and stroke can be colored. Nothing else
        and NOT both
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
    def parse_channel_arg(arg: str) -> TupleType[OptionalType[str]]:
        """
        given an argument like:
            --xvar='id|Product ID'
                return ('id', 'Product ID')
            --yvar='amount'
                return ('amount', 'amount')
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
