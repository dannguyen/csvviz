from pathlib import Path
from typing import Any as typeAny, Mapping as typeMapping, NoReturn as typeNoReturn
from typing import Dict as typeDict, List as typeList, Tuple as typeTuple, Union as typeUnion
from typing import IO as typeIO

import altair as alt
import pandas as pd


from csvviz.exceptions import *
from csvviz.kits.datakit import Datakit
from csvviz.cli_utils import clout, clerr, preview_chart


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
    def __init__(self, viz_type:str, input_path:typeUnion[typeIO, Path, str]):
        self.viz_type = 'bar'
        self.datakit = Datakit(input_path)
        self.chart = self._init_chart()


    ########### internal methods
    def _init_chart(self) -> alt.Chart:
        mname = get_chart_methodname(self.viz_type)
        foo = getattr(alt.Chart(self.df), mname)
        return foo()

    @property
    def df(self) -> pd.DataFrame:
        return self.datakit.df

    @property
    def column_names(self) -> typeList[str]:
        return list(self.df.columns)


    ##### chart_building helpers

    def output_chart(self) -> typeNoReturn:
        _kwargs = self.kwargs
        # --interactive/--static chart is independent of whether or not we're previewing it,
        #  which is reflected in its JSON representation
        if _kwargs.get('is_interactive'):
            chart = chart.interactive()

        # echo JSON before doing a preview
        if _kwargs.get('to_json'):
            clout(chart.to_json(indent=2))

        if _kwargs['do_preview']:
            preview_chart(chart)
