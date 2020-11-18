"""
These tests test the effect of vizkit options on its chart object
They do NOT invoke CliRunner i.e. integrated cli output
"""

import pytest

import altair as alt
from pathlib import Path

from csvviz.exceptions import *
import csvviz.settings

# for now, the bar chart seems like a good default viz
from csvviz.vizzes.bar import Barkit as Gkit

INPUT_PATH = "examples/fruits.csv"


def vfoo(options={}, input_file=INPUT_PATH) -> Gkit:
    return Gkit(input_file, options=options)


def cfoo(
    options={},
    input_file=INPUT_PATH,
) -> alt.Chart:
    return vfoo(options, input_file).chart_dict


def test_chart_defaults():
    chart = cfoo()
    assert "title" not in chart
    assert chart["height"] == Gkit.default_chart_height
    assert chart["width"] == Gkit.default_chart_width
    assert chart["autosize"] == {
        "type": "pad",
        "contains": "padding",
    }


@pytest.mark.curious("this should be deprecated/fixed or whatever later TK")
def test_chart_default_config():
    chart = cfoo()
    assert chart["config"]["view"] == {"continuousWidth": 400, "continuousHeight": 300}


##############################################################################################################
# chart style properties
##############################################################################################################
def test_set_title():
    chart = cfoo({"title": "My Title"})
    assert chart["title"] == "My Title"


def test_set_width_height():
    chart = cfoo({"height": 42, "width": 100})
    assert chart["width"] == 100
    assert chart["height"] == 42


def test_set_auto_width_height():
    chart = cfoo({"height": 0})
    assert chart["height"] == 0
    assert chart["width"] == Gkit.default_chart_width

    chart = cfoo({"width": 0})
    assert chart["height"] == Gkit.default_chart_height
    assert chart["width"] == 0


#####################
# legend stuff
#####################
def test_chart_default_legend():
    chart = cfoo({"colorvar": "season"})
    fill = chart["encoding"]["fill"]
    assert fill["legend"]["orient"] == csvviz.settings.DEFAULT_LEGEND_ORIENTATION


@pytest.mark.curious(
    "legend disabling is also tested at the channel_group(options={}) level..."
)
def test_chart_disable_legend():
    """encoding's legend prop is explicitly set to None"""
    chart = cfoo({"colorvar": "season", "no_legend": True})
    fill = chart["encoding"]["fill"]
    assert fill["legend"] is None


##############################################################################################################
# chart style interactivity
##############################################################################################################
def test_is_interactive():
    chart = cfoo({"is_interactive": True})
    sel = list(chart["selection"].keys())[0]
    s = chart["selection"][sel]
    assert isinstance(s, dict)
    assert s["type"] == "interval"
    assert s["bind"] == "scales"
    assert s["encodings"] == ["x", "y"]


# ##############################################################################################################
# # output and preview
# ##############################################################################################################


# def test_interactive_chart():
#     result = CliRunner().invoke(viz, ["--static", *TING_ARGS])
#     cdata = json.loads(result.output)

#     assert "selection" not in cdata


# def test_static_chart():
#     result = CliRunner().invoke(viz, ["--interactive", *TING_ARGS])
#     cdata = json.loads(result.output)

#     assert "selection" in cdata


# ##############################################################################################################
# # --theme
# ##############################################################################################################


# def test_specify_theme():
#     result = CliRunner().invoke(viz, ["--theme", "latimes", *TING_ARGS])
#     cdata = json.loads(result.output)

#     assert "latimes" == cdata["usermeta"]["embedOptions"]["theme"]


# def test_specify_default_theme_has_no_effect():
#     result = CliRunner().invoke(viz, ["--theme", "default", *TING_ARGS])
#     cdata = json.loads(result.output)
#     assert "usermeta" not in cdata
#     # i.e. NOT cdata['usermeta']['embedOptions']['theme'] == 'default'
