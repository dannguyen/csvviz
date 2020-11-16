"""TODO/in progress: ChannelGroup subsumes/simplifies what's in Channeled.py"""

import altair as alt
from altair.utils import parse_shorthand as alt_parse_shorthand
import pandas as pd
from typing import (
    Dict as DictType,
    Optional as OptionalType,
    Tuple as TupleType,
    Union as UnionType,
)

from csvviz.helpers import parse_delimited_str


CHANNELS = {
    "x": alt.X,
    "y": alt.Y,
    "fill": alt.Fill,
    "stroke": alt.Stroke,
    "size": alt.Size,
}


ChannelType = UnionType[alt.X, alt.Y, alt.Fill, alt.Size, alt.Stroke]
ChannelsDictType = DictType[str, ChannelType]


class ChannelGroup:
    """
    A dict of alt.Channels,
    e.g.
        cgroup =  {
            "x": alt.X('name'),
            "y": 'amount',
            "fill": alt.Color('amount', scale=alt.Scale(range=['green', 'yellow', 'red']
        )
        alt.Chart(df).mark_bar().encode(**cgroup))

    kwargs are the processed keyword arguments from the click command
    """

    def __init__(self, df: pd.DataFrame, kwargs):
        self.df = df
        self.kwargs = kwargs
        self._channels = self.create()

    @property
    def channels(self) -> ChannelsDictType:
        return {k: v for k, v in self._channels.items() if v}

    def create(self) -> ChannelsDictType:
        cx = {}
        for cname, channel in CHANNELS.items():
            karg = self.kwargs.get(f"{cname}var")
            if karg:
                shorthand, title = self.parse_channel_arg(karg)
                chargs = self.parse_shorthand(shorthand, data=self.df)
                if title:
                    chargs["title"] = title
                cx[cname] = channel(**chargs)

        return cx

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
