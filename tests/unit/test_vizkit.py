import pytest
from io import StringIO
import altair as alt
import pandas as pd

from csvviz.vizkit import Vizkit, VizkitCommandMixin
from csvviz.viz.scatter import Scatterkit


@pytest.fixture
def tvk():
    SRC_PATH = "examples/tings.csv"
    return Vizkit(
        input_file=SRC_PATH,
        kwargs={
            "xvar": "name",
            "yvar": "amount",
            "fillvar": "name",
            "is_interactive": True,
            "no_preview": True,
            "to_json": True,
        },
    )


@pytest.fixture
def dotvk():
    SRC_PATH = "examples/vals.csv"
    return Scatterkit(
        input_file=SRC_PATH,
        kwargs={
            "xvar": "mass",
            "yvar": "volume",
            "fillvar": "breed",
            "is_interactive": True,
            "no_preview": True,
            "to_json": True,
        },
    )


def test_vizkit_basic_init(tvk):
    assert isinstance(tvk, Vizkit)
    assert isinstance(tvk.chart, alt.Chart)


def test_vizkit_properties(tvk, dotvk):
    assert tvk.viz_commandname == "abstract"
    assert tvk.mark_type == "mark_bar"
    assert isinstance(tvk.df, pd.DataFrame)
    assert tvk.column_names == ["name", "amount"]

    assert dotvk.name == "scatter"
    assert dotvk.mark_type == "mark_point"


def test_vizkit_unneeded_properties_to_deprecate(tvk):
    assert tvk.name == "abstract"  # maybe viz_commandname isn't needed?


def test_vizkit_kwarg_properties(tvk):
    """
    these internal helpers copy from self.kwargs
    """

    #    import pdb; pdb.set_trace()
    assert tvk.channel_kwargs["xvar"] == "name"
    assert tvk.channel_kwargs["yvar"] == "amount"
    assert tvk.channel_kwargs["fillvar"] == "name"

    assert tvk.output_kwargs["to_json"] is True
    assert tvk.output_kwargs["no_preview"] is True

    # duh:
    assert tvk.color_kwargs["colors"] is None
    assert tvk.color_kwargs["color_scheme"] is None


@pytest.mark.skip(reason="TODO")
def test_vizkit_declarations(tvk):
    pass
    # assert isinstance(tvk.finalize_channels['x'], alt.X)
    # assert isinstance(tvk.finalize_channels['fill'], alt.Fill)

    # assert tvk.declare_legend['orient'] == DEFAULT_LEGEND_ORIENTATION
    # assert tvk.declare_legend['title'] == 'name'
    # assert tvk.declare_output['to_json'] is True


###################################################################################
# chart building
###################################################################################
def test_vizkit_chart_basic(tvk):
    chart = tvk.chart
    vega = chart.to_dict()
    assert "selection" in vega  # because of is_interactive

    # import pdb; pdb.set_trace()
    assert vega["mark"]["type"] == "bar"
    assert vega["mark"]["clip"] is True

    assert vega["encoding"]["y"]["field"] == "amount"
    assert vega["encoding"]["fill"]["field"] == "name"


def test_vizkit_output_basic(tvk, capsys):
    tvk.output_chart()
    outs = capsys.readouterr().out
    assert "{" == outs.splitlines()[0]
    assert '"amount": 20' in outs
    assert '"type": "bar"' in outs
    assert '"$schema"' in outs


#####################################
# get_chart_methodname
#####################################
def test_lookup_mark_method():
    foo = VizkitCommandMixin.lookup_mark_method
    assert "mark_area" == foo("area")
    assert "mark_bar" == foo("bar")
    assert "mark_bar" == foo("hist")
    assert "mark_line" == foo("line")
    assert "mark_point" == foo("scatter")


##### parse_var_str
def test_parse_var_str_default_name():
    foo = VizkitCommandMixin.parse_var_str
    assert foo("id") == ("id", None)
    assert foo("id|") == ("id", None)
    assert foo("sum(thing)|") == ("sum(thing)", None)


def test_parse_var_str_specified_name():
    foo = VizkitCommandMixin.parse_var_str
    assert foo("id|Foo") == ("id", "Foo")
    assert foo("sum(thing)|Bar") == ("sum(thing)", "Bar")


def test_parse_var_str_edge_case():
    data = StringIO("id,Hello|World\nfoo,42\n")
    s = Vizkit(
        input_file=data,
        kwargs={
            "xvar": "id",
            "yvar": '"Hello|World"|"hey|world"',
        },
    )
    assert s.channels["y"]["field"] == "Hello|World"
    assert s.channels["y"]["title"] == "hey|world"
