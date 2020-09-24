from pathlib import Path
from typing import Any as typeAny, Mapping as typeMapping, NoReturn as typeNoReturn
from typing import Dict as typeDict, List as typeList, Tuple as typeTuple, Union as typeUnion
from typing import IO as typeIO

import altair as alt
import pandas as pd


from csvviz.exceptions import *
from csvviz.kits.datakit import Datakit
from csvviz.cli_utils import clout, clerr, preview_chart
from csvviz.settings import *

def get_chart_methodname(viz_type:str) -> alt.Chart:
    """
    convenience method that translates our command names, e.g. bar, dot, line, to
    the equivalent in altair
    """
    vname = viz_type.lower()

    if vname in ('area', 'bar', 'line',):
        m = f'mark_{vname}'
    elif vname == 'scatter':
        m = 'mark_point'
    else:
        raise ValueError(f"{viz_type} is not a recognized viz/chart type")
    return m

class Vizkit(object):
    """
    The interface between Click.command, Altair.Chart, and Pandas.dataframe
    """
    def __init__(self, viz_type:str, input_path:typeUnion[typeIO, Path, str], kwargs):
        self.kwargs = kwargs
        self.datakit = Datakit(input_path)

        # chart-related settings
        self.viz_type = 'bar'
        self.theme = kwargs.get('theme')
        self.channels = self.set_channels()
        self.style_properties = self.set_style()
        self.interactive_mode = self.kwargs.get('is_interactive')

        # the chart itself
        self.chart = self.build_chart()


    def _init_chart(self) -> alt.Chart:
        alt.themes.enable(self.theme)

        mname = get_chart_methodname(self.viz_type)
        chartfoo = getattr(alt.Chart(self.df), mname)
        return chartfoo()

    def build_chart(self) -> alt.Chart:

        chart = self._init_chart()
        chart = chart.encode(**self.channels)
        chart = chart.properties(**self.style_properties)

        if self.interactive_mode:
            chart = chart.interactive()

        return chart
        # implementing this for testing ease...
        # raise Exception('Need to implement build_chart for each viz subclass')


    def output_chart(self, oargs={}) -> typeNoReturn:
        # --interactive/--static chart is independent of whether or not we're previewing it,
        #  which is reflected in its JSON representation
        # echo JSON before doing a preview

        oargs = self.output_kwargs if not oargs else oargs

        if oargs['to_json']:
            clout(self.chart.to_json(indent=2))

        if oargs['do_preview']:
            preview_chart(self.chart)



    def set_channels(self) -> typeDict[str, typeUnion[alt.X, alt.Y, alt.Fill, alt.Size]]:
        """
        TK TODO:
        _declare_channels seems like the better name, though we're using that
        for the more general/basic initializations (maybe it should be _init_channels?)

        This method does the bespoke work to combine channels with legends/colors/etc
        and should be implemented in every subclass
        """
        try:
            channels = self._declare_channels(self.channel_kwargs, self.datakit)
        except InvalidColumnName as err:
            clexit(1, err)

        if self.kwargs.get('horizontal'):
            channels['x'], channels['y'] = (channels['y'], channels['x'])

        if _fill := channels['fill']:
            _fill.scale  = alt.Scale(**self._declare_colors(self.color_kwargs))
            # _fill.legend = alt.Legend(title='mah legend', orient='bottom')
            _legend = self._declare_legend(self.legend_kwargs, colname=_fill.shorthand)
            if _legend is False: # then hide_legend was explicitly specified
                _fill.legend = None
            else:
                _fill.legend = _legend

        try:
            _sort_config = self._declare_sorting(self.kwargs, self.datakit)
        except InvalidColumnName as err:
            clexit(1, err)
        else:
            if _sort_config:
                channels['x'].sort = _sort_config

        return channels


    def set_style(self) -> typeDict:
        return self._declare_styles(self.kwargs)

    @property
    def df(self) -> pd.DataFrame:
        return self.datakit.df

    @property
    def column_names(self) -> typeList[str]:
        return list(self.df.columns)



    #####################################################################
    #  kwargs helpers
    # TODO: refactor later
    @property
    def channel_kwargs(self) -> typeDict:
        _ARGKEYS = ('xvar', 'yvar', 'fillvar',)
        return {k: self.kwargs.get(k) for k in _ARGKEYS}

    @property
    def color_kwargs(self) -> typeDict:
        _ARGKEYS = ('color_scheme', 'colors',)
        return {k: self.kwargs.get(k) for k in _ARGKEYS}

    @property
    def legend_kwargs(self) -> typeDict:
        _ARGKEYS = ('hide_legend', 'TK-orient', 'TK-title',)
        return {k: self.kwargs.get(k) for k in _ARGKEYS}


    @property
    def output_kwargs(self) -> typeDict:
        _ARGKEYS = ('to_json', 'do_preview',)
        return {k: self.kwargs.get(k) for k in _ARGKEYS}

    # Not needed if there are no other interactive-like attributes
    # @property
    # def render_kwargs(self) -> typeDict:
    #     _ARGKEYS = ('is_interactive',)
    #     return {k: self.kwargs.get(k) for k in _ARGKEYS}

    @property
    def sorting_kwargs(self) -> typeDict:
        _ARGKEYS = ('sort_x',)
        return {k: self.kwargs.get(k) for k in _ARGKEYS}

    @property
    def styling_kwargs(self) -> typeDict:
        _ARGKEYS = ('title',)
        return {k: self.kwargs.get(k) for k in _ARGKEYS}



    #####################################################################
    ##### declarations

    @staticmethod
    def _declare_channels(kwargs:typeDict, datakit) -> typeDict:
        config = {}

        # configure x and y channels
        for i, n in enumerate(('x', 'y',)):
            _arg = f'{n}var'
            _v = kwargs[_arg] if kwargs[_arg] else datakit.column_names[i]
            vname, _z = datakit.resolve_column(_v)
            config[n] = getattr(alt, n.capitalize())(vname)

        # configure fill channel
        if _fill := kwargs.get('fillvar'):
            _fill, _z = datakit.resolve_column(_fill)
            config['fill'] = alt.Fill(_fill)

        return config

    @staticmethod
    def _declare_colors(kwargs:typeDict) -> typeDict:
        """
        returns a dict for alt.Scale()
        """
        ## fill color stuff
        config = {'scheme': DEFAULT_COLOR_SCHEME}

        if _cs := kwargs.get('color_scheme'):
            config['scheme'] = _cs
            # TODO: if _cs does not match a valid color scheme, then raise a warning/error

        if _colortxt := kwargs['colors']:
            # don't think this needs to be a formal parser
            config['range'] = _colortxt.strip().split(',')
            # for now, only colors OR color_scheme can be set, not both
            config.pop('scheme', None)

        return config

    @staticmethod
    def _declare_legend(kwargs:typeDict, colname:str) -> typeUnion[typeDict, bool]:
        config = {}
        if kwargs['hide_legend']:
            config = False
        else:
        # TODO: let users configure orientation and title...somehow
            config['title'] = colname if not kwargs.get('TK-column-title') else colname
            if _o := kwargs.get('TK-orientation'):
                config['orient'] = _o
            else:
                config['orient'] = DEFAULT_LEGEND_ORIENTATION

        return config



    @staticmethod
    def _declare_sorting(kwargs:typeDict, datakit:Datakit) -> typeDict:
        config = {}
        if _sortx := kwargs.get('sort_x'):
            _sign, _cname = re.match(r'(-?)(.+)', _sortx).groups()
            colname, _z = datakit.resolve_column(_cname)  # mostly validation

            config['field'] = colname
            config['order'] = 'descending' if _sign == '-' else 'ascending'

        return config


    @staticmethod
    def _declare_styles(kwargs:typeDict) -> typeDict:
        config = {}

        if _title := kwargs.get('title'):
            config['title'] = _title

        return config
