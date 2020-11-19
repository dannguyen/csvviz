import altair as alt
import pandas as pd
from typing import (
    Any as AnyType,
    Callable as CallableType,
    Dict as DictType,
    List as ListType,
    NoReturn as NoReturnType,
    Optional as OptionalType,
    # Tuple as TupleType,
    # Union as UnionType,
)


from csvviz.vizkit.channel_group import ChannelGroup
from csvviz.vizkit.dataful import Dataful

# from csvviz import altUndefined
# from csvviz.exceptions import InvalidDataReference


VIZ_MARK_NAME_LOOKUP = {
    "abstract": "bar",  # for testing purposes
    "area": "area",
    "bar": "bar",
    "heatmap": "rect",
    "hist": "bar",
    "line": "line",
    "scatter": "point",
    "stream": "area",
}


class Chart(Dataful):
    def __init__(
        self,
        viz_name: str,
        data: pd.DataFrame,
        channels: ChannelGroup,
        defaults: DictType,
        options: DictType = {},
        # styles:DictType = {},
        # config:DictType = {},
        # is_interactive:bool = True
    ):
        """
        A class that abstracts the actual chart building

        - also doesn't care about the channel making, though it does do the channel encoding

        Note: `options` is still just a sloppy grabbag from the command-line arg parser, consider
            refactoring Chart to prevent leaky abstraction
        """

        self.viz_name = viz_name
        self.options = options
        self.defaults = defaults
        self._dataframe = data
        self._channels = channels
        # self._init_styles = styles
        # self._init_config = config  # chart wide stuff, like width, height, title
        # self.is_interactive = is_interactive

        tkc = self.scaffold()
        # given a funky name because _chart_object is not meant to be touched
        # by other classes like Vizkit
        self._chart_object = tkc

    def scaffold(self) -> alt.Chart:
        c = alt.Chart(data=self.df)
        c = getattr(c, self.mark_method_name)(clip=True)
        c = c.encode(**self.channels)

        if self.is_faceted:
            c = c.resolve_axis(x="independent")

        if self.interactive_mode:
            c = c.interactive()

        c = c.properties(**self.init_styles())

        return c

    def init_styles(self) -> DictType:
        """assumes self.channels has been set, particularly the types of x/y channels"""
        # TK rename this...
        styles = {}

        # TODO: refactor this
        styles["autosize"] = {"type": "pad", "contains": "padding"}

        STYLE_ATTRS = {
            "height": self.defaults["chart_height"],
            "width": self.defaults["chart_width"],
            "title": None,
        }

        # TK messy messy!
        if self.is_faceted:
            STYLE_ATTRS["height"] = self.defaults["faceted_height"]
            STYLE_ATTRS["width"] = self.defaults["faceted_width"]

        for att, default_val in STYLE_ATTRS.items():
            setval = self.options.get(att)
            if setval == 0 or setval:
                styles[att] = setval
            elif default_val:
                styles[att] = default_val
            else:
                pass
                # do nothing, including don't add :att to styles

        return styles

    def get_prop(self, propname: str) -> AnyType:
        """used by Vizkit to talk to the raw chart properties without having to do vizkit.raw_chart.prop"""
        return getattr(self._chart_object, propname)

    def set_props(self, props: dict) -> NoReturnType:
        """
        basically used by Vizkit.finalize_chart()
        TODO: test this and mutability and sanctity of _chart_object
        """
        c = self._chart_object.properties(**props)
        self._chart_object = c
        return

    def to_dict(self, **kwargs) -> dict:
        """
        Convert the chart to a dictionary suitable for JSON export
        File:   altair/vegalite/v4/api.py
        """
        return self.raw_chart.to_dict(**kwargs)

    def to_json(self, **kwargs) -> str:
        """
        The JSON specification of the chart object.
        altair/utils/schemapi.py
        """
        kwargs["indent"] = kwargs.get("indent") or 2
        kwargs["sort_keys"] = (
            False if kwargs.get("sort_keys") is None else kwargs["sort_keys"]
        )
        kwargs["validate"] = (
            True if kwargs.get("validate") is None else kwargs["validate"]
        )

        return self.raw_chart.to_json(**kwargs)

    @property
    def channels(self) -> ChannelGroup:
        return self._channels

    @property
    def is_faceted(self) -> bool:
        """should throw error if accessed before self.channels is set"""
        c = self.channels.get("facet")
        return isinstance(c, alt.Facet)

    @property
    def interactive_mode(self) -> bool:
        return self.options.get("is_interactive") == True

    @property
    def mark_name(self) -> str:
        return self.lookup_mark_name(self.viz_name)

    @property
    def mark_method_name(self) -> str:
        """e.g. 'mark_rect', 'mark_line'"""
        return "mark_%s" % self.mark_name

    @property
    def raw_chart(self) -> alt.Chart:
        return self._chart_object

    @staticmethod
    def lookup_mark_name(cmdname) -> str:
        """this only exists for testing conveniences; no reason not to fold it into Chart.mark_name"""
        name = cmdname.lower()
        m = VIZ_MARK_NAME_LOOKUP.get(name)
        if not m:
            raise ValueError(f"{name} is not a recognized viz/chart type")
        else:
            return m


# def lookup_mark_method(viz_commandname: str) -> str:
#     """
#     convenience method that translates our command names, e.g. bar, dot, line, to
#     the equivalent in altair
#     """
#     m = VIZ_MARK_NAME_LOOKUP.get(viz_commandname.lower())
#     if not m:
#         raise ValueError(f"{viz_commandname} is not a recognized viz/chart type")
#     else:
#         return "mark_%s" % m

# @property
# def mark_method_foo(self) -> CallableType:
#     return getattr(alt.Chart(self.df), self.mark_method_name)


# def stylize_chart(self, chart: alt.Chart) -> alt.Chart:
#     styleprops = self.init_styles()
#     styleprops = self.finalize_styles(styleprops)

#     chart = chart.properties(**styleprops)

#     return chart

# def init_styles(self) -> DictType:
#     """assumes self.channels has been set, particularly the types of x/y channels"""
#     styles = {}

#     # TODO: refactor this
#     styles["autosize"] = {"type": "pad", "contains": "padding"}

#     STYLE_ATTRS = {
#         "height": self.default_chart_height,
#         "width": self.default_chart_width,
#         "title": None,
#     }

#     # TK messy messy!
#     if self.is_faceted:
#         STYLE_ATTRS["height"] = self.default_faceted_height
#         STYLE_ATTRS["width"] = self.default_faceted_width

#     for att, default_val in STYLE_ATTRS.items():
#         setval = self.options.get(att)
#         if setval == 0 or setval:
#             styles[att] = setval
#         elif default_val:
#             styles[att] = default_val
#         else:
#             pass
#             # do nothing, including don't add :att to styles

#     return styles
