import altair as alt
from altair.utils import parse_shorthand as alt_parse_shorthand
import pandas as pd
from typing import (
    Dict as DictType,
    List as ListType,
    Optional as OptionalType,
    Tuple as TupleType,
    Union as UnionType,
)

from csvviz import altUndefined
from csvviz.exceptions import InvalidDataReference
from csvviz.helpers import parse_delimited_str
from csvviz.settings import (
    DEFAULT_COLOR_SCHEMES,
    DEFAULT_LEGEND_ORIENTATION,
    DEFAULT_FACET_COLUMNS,
    DEFAULT_FACET_SPACING,
)

from csvviz.vizkit.dataful import Dataful


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

    @staticmethod
    def get_default_color_scheme(datatype: str) -> str:
        if datatype in (
            "quantitative",
            "temporal",
        ):
            ds = DEFAULT_COLOR_SCHEMES["ramp"]
        elif datatype == "ordinal":
            ds = DEFAULT_COLOR_SCHEMES["ordinal"]
        else:
            ds = DEFAULT_COLOR_SCHEMES["category"]
        return ds


class ChannelGroup(dict, Dataful, Helpers):
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
        data: pd.DataFrame,
        color_channel_name: OptionalType[str] = None,
    ):
        self.options = options  # i.e. "kwargs"
        self._dataframe = data
        self.color_channel_name = color_channel_name

        self.scaffold().colorize().facetize().legendize().limitize()

    def __eq__(self, other):
        """Overrides the default implementation"""
        return {k: self[k] for k in CHANNELS.keys() if self.get(k)}

    def scaffold(self) -> "ChannelGroup":
        # at this point, options['colorvar'] is set (via Click interface), but NOT
        #  options['fillvar']/options['strokevar']/etc
        # so we (messily) inject it into a copy of the self.options dict (don't want to alter original tho...)
        # TK: seems like spaghetti but whatever...
        _opts = self.options.copy()
        colarg = _opts.get("colorvar")
        if colarg:
            _opts["%svar" % self.color_channel_name] = colarg

        for cname, Channel in CHANNELS.items():
            k = _opts.get(f"{cname}var")
            if k:
                shorthand, title = self.parse_channel_arg(k)
                chargs = self.parse_shorthand(shorthand, data=self.df)
                if chargs["field"] not in self.column_names:
                    raise InvalidDataReference(
                        f"""'{shorthand}' is either an invalid column name, or invalid Altair shorthand"""
                    )
                if title:
                    chargs["title"] = title
                self[cname] = Channel(**chargs)

        return self

    def colorize(self) -> "ChannelGroup":
        """
        this method operates under the assumption that either/or fill and stroke can be
          colored, i.e. nothing else and NOT both
        """
        if not self.color_channel:
            return self

        config = {}
        if self.options.get("color_scheme"):
            config["scheme"] = self.options["color_scheme"]
        else:
            config["scheme"] = self.get_default_color_scheme(self.color_channel.type)

        if self.options.get("color_list"):
            colornames = [s.strip() for s in self.options["color_list"].split(",")]
            if len(colornames) > 1:
                config["range"] = colornames
            else:
                # if the color variable is quantitative, it will display nothing unless
                # the color list has at least 2 things...
                # this amounts to a silent failure tho....TKTK
                config["range"] = [colornames[0], colornames[0]]
            # color_list` kwarg overrides any color_scheme setting
            # TKD: Note: Vizkit validation prevents color_scheme and color_list from being set
            # but unit testing purposes, we need to do this pop:
            config.pop("scheme", None)

        self.color_channel.scale = alt.Scale(**config)
        return self

    def facetize(self) -> "ChannelGroup":
        """set facets, i.e. grid"""
        fc = self.facet_channel
        if fc:
            fc.spacing = DEFAULT_FACET_SPACING

            colcount = self.options.get("facet_columns")
            if colcount == 0 or colcount:
                fc.columns = colcount
            else:
                fc.columns = DEFAULT_FACET_COLUMNS

            # TODO: DRY self.configure_channel_sort(channels["facet"], self.kwargs["facet_sort"])
            xo = self.options.get("facet_sort")
            if xo:
                if xo == "asc":
                    fc.sort = "ascending"
                elif xo == "desc":
                    fc.sort = "descending"
                else:
                    raise ValueError(f"Invalid sort order term: {xo}")

        return self

    def legendize(self) -> "ChannelGroup":
        """
        Vega doesn't seem to have a legend-disabling config at the global/local level,
        so we have to do it at the encoding level

        https://altair-viz.github.io/user_guide/generated/toplevel/altair.Chart.html#altair.Chart.configure_legend
        """
        config = {"orient": DEFAULT_LEGEND_ORIENTATION}
        for cname in ("fill", "size", "stroke"):
            channel = self.get(cname)
            if channel:
                if self.options.get("no_legend"):
                    channel.legend = None
                else:
                    channel.legend = alt.Legend(**config)
        # TODO: explicitly set title; figure out how Altair devises the default title
        return self

    def limitize(self) -> "ChannelGroup":
        """
        by now, self['x'] and self['y'] are expected to be set

        Note that because options['xlim/ylim'] is a comma-delimited str, like '-10,40'
        the channel.scale will be set to alt.Scale(domain=["-10", "40"])...and Vega figures it out?
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

    @property
    def color_channel(self) -> OptionalType[UnionType[alt.Fill, alt.Stroke]]:
        if not self.color_channel_name:
            # this is an edge case, as every known viz type has at least the default
            # :color_channel_name (i.e. 'fill')
            return None
        return self.get(self.color_channel_name)

    @property
    def facet_channel(self) -> alt.Facet:
        return self.get("facet")
