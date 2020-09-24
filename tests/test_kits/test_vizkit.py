import pytest

from csvviz.kits.datakit import Datakit
from csvviz.kits.vizkit import Vizkit, get_chart_methodname

import altair as alt
import pandas as pd

@pytest.fixture
def tvk():
    SRC_PATH = 'examples/tings.csv'
    return Vizkit('bar', input_path=SRC_PATH,
        kwargs={'xvar': 'name', 'yvar': 'amount', 'fillvar': 'name',
            'is_interactive': True,  'do_preview': False,  'to_json': True})

def test_vizkit_basic_init(tvk):
    assert isinstance(tvk, Vizkit)
    assert isinstance(tvk.datakit, Datakit)
    assert isinstance(tvk.chart, alt.Chart)
    assert tvk.chart.mark == 'bar'



def test_vizkit_kwarg_properties(tvk):
    """
    these internal helpers copy from self.kwargs
    """

#    import pdb; pdb.set_trace()
    assert tvk.channel_kwargs['xvar'] == 'name'
    assert tvk.channel_kwargs['yvar'] == 'amount'
    assert tvk.channel_kwargs['fillvar'] == 'name'

    assert tvk.output_kwargs['to_json'] is True
    assert tvk.output_kwargs['do_preview'] is False

    # duh:
    assert tvk.color_kwargs['colors'] is None
    assert tvk.color_kwargs['color_scheme'] is None



@pytest.mark.skip(reason='TODO')
def test_vizkit_declarations(tvk):
    pass
    # assert isinstance(tvk.declare_channels['x'], alt.X)
    # assert isinstance(tvk.declare_channels['fill'], alt.Fill)

    # assert tvk.declare_legend['orient'] == DEFAULT_LEGEND_ORIENTATION
    # assert tvk.declare_legend['title'] == 'name'
    # assert tvk.declare_output['to_json'] is True


def test_vizkit_properties(tvk):
    assert tvk.viz_type == 'bar'

    assert isinstance(tvk.df, pd.DataFrame)
    assert tvk.column_names == ['name', 'amount']


###################################################################################
# chart building
###################################################################################
def test_vizkit_chart_basic(tvk):
    chart = tvk.chart
    vega = chart.to_dict()
    assert 'selection' in vega # because of is_interactive

    # import pdb; pdb.set_trace()
    assert vega['mark'] == 'bar'
    assert vega['encoding']['y']['field'] == 'amount'
    assert vega['encoding']['fill']['field'] == 'name'
    assert vega['encoding']['fill']['legend']['title'] == 'name'

def test_vizkit_output_basic(tvk, capsys):
    tvk.output_chart()
    outs = capsys.readouterr().out
    assert '{' == outs.splitlines()[0]
    assert '"amount": 20' in outs
    assert '"mark": "bar"' in outs
    assert '"$schema"' in outs


#####################################
# get_chart_methodname
#####################################
def test_get_chart_methodname():
    assert 'mark_bar' == get_chart_methodname('bar')
    assert 'mark_line' == get_chart_methodname('line')
    assert 'mark_point' == get_chart_methodname('scatter')
