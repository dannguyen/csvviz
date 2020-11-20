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


DEFAULT_PROPS = {
    "autosize": {
        "contains": "padding",
        "type": "pad",
    },
    "height": None,
    "title": None,
    "width": None,
}

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

        tkc = self.scaffold()
        # given a funky name because _chart_object is not meant to be touched
        # by other classes like Vizkit
        self._chart_object = tkc

    def scaffold(self) -> alt.Chart:
        alt.themes.enable("none")
        c = alt.Chart(data=self.df)

        # set local configs
        # c = getattr(c, self.mark_method_name)(clip=True)
        mark_foo = getattr(c, self.mark_method_name)
        mark_opts = {"clip": True}
        if not self.color_channel and self.options.get("color_list"):
            # user hasn't defined a fill/stroke var, but wants to define a color...
            # TK DRY this up
            xcols = [s.strip() for s in self.options["color_list"].split(",")]
            mark_opts["color"] = xcols[0]
        c = mark_foo(**mark_opts)

        ##### encode channels
        c = c.encode(**self.channels)

        # set global configs
        # TODO: call these "local" configs? and move to own method?
        if self.is_faceted:
            c = c.resolve_axis(x="independent")

        if self.interactive_mode:
            c = c.interactive()
        c = c.properties(**self.init_props())

        return c

    def init_props(self) -> DictType:
        """assumes self.channels has been set, particularly the types of x/y channels"""
        props = {}

        # TK messy messy!
        if self.is_faceted:
            props["height"] = self.defaults["faceted_height"]
            props["width"] = self.defaults["faceted_width"]
        else:
            props["height"] = self.defaults["chart_height"]
            props["width"] = self.defaults["chart_width"]

        for att, default_val in DEFAULT_PROPS.items():
            setval = self.options.get("chart_%s" % att)
            if setval == 0 or setval:
                props[att] = setval
            elif default_val:
                props[att] = default_val
            else:
                pass
                # do nothing, including don't add :att to props

        return props

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
    def color_channel(self):
        """returns OptionalType[UnionType[alt.Fill, alt.Stroke]]"""
        return self.channels.color_channel

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
