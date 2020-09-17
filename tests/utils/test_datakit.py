import pytest

from csvviz.utils.datakit import Datakit
import pandas as pd

@pytest.fixture
def tdk():
    SRC_PATH = 'examples/tings.csv'
    dk = Datakit(SRC_PATH)
    return dk

def test_datakit_init(tdk):
    assert isinstance(tdk, Datakit)
    assert isinstance(tdk.df, pd.DataFrame)



def test_datakit_properties(tdk):
    assert tdk.column_names == ['name', 'amount']
    assert isinstance(tdk.schema, dict)
    assert list(tdk.schema.keys()) == ['name', 'amount']


@pytest.mark.skip(reason="do it later")
def test_datakit_data_getters(tdk):
    pass


def test_datakit_resolve_column_basics(tdk):
    """this reaffirms that columns are zero-indexed"""
    assert tdk.resolve_column('name')   == (0, 'name')
    assert tdk.resolve_column('amount') == (1, 'amount')
    assert tdk.resolve_column(1)        == (1, 'amount')
    assert tdk.resolve_column('0')      == (0, 'name')


@pytest.mark.skip(reason="do it later")
def test_datakit_resolve_column_errors(tdk):
    with pytest.raises(ValueError) as err:
        tdk.resolve_column(42)
    assert 'TK TK TK' in str(err.value)



