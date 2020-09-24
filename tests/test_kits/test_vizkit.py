import pytest

from csvviz.kits.datakit import Datakit
from csvviz.kits.vizkit import Vizkit, get_chart_methodname

import altair as alt
import pandas as pd

@pytest.fixture
def tvk():
    SRC_PATH = 'examples/tings.csv'
    return Vizkit('bar', input_path=SRC_PATH)

def test_vizkit_init(tvk):
    assert isinstance(tvk, Vizkit)
    assert isinstance(tvk.datakit, Datakit)
    assert isinstance(tvk.chart, alt.Chart)

    assert tvk.chart.mark == 'bar'


def test_vizkit_properties(tvk):
    assert tvk.viz_type == 'bar'

    assert isinstance(tvk.df, pd.DataFrame)
    assert tvk.column_names == ['name', 'amount']



#####################################
# get_chart_methodname
#####################################

def test_get_chart_methodname():
    assert 'mark_bar' == get_chart_methodname('bar')
    assert 'mark_line' == get_chart_methodname('line')
    assert 'mark_point' == get_chart_methodname('scatter')
