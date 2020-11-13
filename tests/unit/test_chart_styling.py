import pytest
from click.testing import CliRunner

import click
import json
from pathlib import Path

from csvviz.exceptions import *
from csvviz.settings import *

# for now, the bar chart seems like a good default viz
from csvviz.vizkit.viztypes.bar import Barkit

viz = Barkit.register_command()

MI_ARGS = ["--json", "--no-preview", "examples/mix.csv"]
TING_ARGS = ["--json", "--no-preview", "examples/tings.csv"]


def test_defaults():
    result = CliRunner().invoke(viz, [*TING_ARGS])
    assert result.exit_code is 0

    # no usermeta, i.e. default theme is specified
    cdata = json.loads(result.output)

    # i.e. NOT cdata['usermeta']['embedOptions']['theme'] == 'default'
    assert "usermeta" not in cdata

    # charts have no titles by default
    assert "title" not in cdata

    # default rendering is interactive mode, which means 'selection' will exist
    assert "selection" in cdata


##############################################################################################################
# chart properties
##############################################################################################################
def test_title():
    result = CliRunner().invoke(viz, ["-t", "My Title", *TING_ARGS])
    cdata = json.loads(result.output)
    assert cdata["title"] == "My Title"


##############################################################################################################
# output and preview
##############################################################################################################


def test_interactive_chart():
    result = CliRunner().invoke(viz, ["--static", *TING_ARGS])
    cdata = json.loads(result.output)

    assert "selection" not in cdata


def test_static_chart():
    result = CliRunner().invoke(viz, ["--interactive", *TING_ARGS])
    cdata = json.loads(result.output)

    assert "selection" in cdata


##############################################################################################################
# --theme
##############################################################################################################


def test_specify_theme():
    result = CliRunner().invoke(viz, ["--theme", "latimes", *TING_ARGS])
    cdata = json.loads(result.output)

    assert "latimes" == cdata["usermeta"]["embedOptions"]["theme"]


def test_specify_default_theme_has_no_effect():
    result = CliRunner().invoke(viz, ["--theme", "default", *TING_ARGS])
    cdata = json.loads(result.output)
    assert "usermeta" not in cdata
    # i.e. NOT cdata['usermeta']['embedOptions']['theme'] == 'default'


##############################################################################################################
# -W/--width and -H/--height
##############################################################################################################
def test_chart_dim_defaults():
    cdata = json.loads(CliRunner().invoke(viz, MI_ARGS).output)
    assert all(d not in cdata for d in ("width", "height"))
    # assert cdata["width"] == DEFAULT_CHART_WIDTH
    # assert cdata["height"] == DEFAULT_CHART_HEIGHT


def test_chart_width_set():
    cdata = json.loads(CliRunner().invoke(viz, ["-W", "345", *MI_ARGS]).output)
    assert cdata["width"] == 345
    assert "height" not in cdata


# def test_width_defaults_nominal_is_discrete():
#     """
#     when x/y is nominal, config.view.discreteWidth and discreteHeight are used
#     """
#     cdata = json.loads(CliRunner().invoke(viz, [
#         "-x", "id:N", "-y", "handle:N", *MI_ARGS]).output)
#     view = cdata['config']['view']
#     assert view['discreteWidth'] == DEFAULT_CHART_WIDTH
#     assert view['discreteHeight'] == DEFAULT_CHART_HEIGHT
#     assert 'continuousWidth' not in view
#     assert 'continuousHeight' not in view
