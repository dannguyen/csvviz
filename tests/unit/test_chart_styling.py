import pytest
from click.testing import CliRunner

import click
import json
from pathlib import Path

from csvviz.exceptions import *
from csvviz.settings import *

# for now, the bar chart seems like a good default viz
from csvviz.cmds.bar import Barkit

viz = Barkit.register_command()

OUTPUT_ARGS = ["--json", "--no-preview", "examples/tings.csv"]


def test_defaults():
    result = CliRunner().invoke(viz, [*OUTPUT_ARGS])
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
    result = CliRunner().invoke(viz, ["-t", "My Title", *OUTPUT_ARGS])
    cdata = json.loads(result.output)
    assert cdata["title"] == "My Title"


##############################################################################################################
# output and preview
##############################################################################################################


def test_interactive_chart():
    result = CliRunner().invoke(viz, ["--static", *OUTPUT_ARGS])
    cdata = json.loads(result.output)

    assert "selection" not in cdata


def test_static_chart():
    result = CliRunner().invoke(viz, ["--interactive", *OUTPUT_ARGS])
    cdata = json.loads(result.output)

    assert "selection" in cdata


##############################################################################################################
# --theme
##############################################################################################################


def test_specify_theme():
    result = CliRunner().invoke(viz, ["--theme", "latimes", *OUTPUT_ARGS])
    cdata = json.loads(result.output)

    assert "latimes" == cdata["usermeta"]["embedOptions"]["theme"]


def test_specify_default_theme_has_no_effect():
    result = CliRunner().invoke(viz, ["--theme", "default", *OUTPUT_ARGS])
    cdata = json.loads(result.output)
    assert "usermeta" not in cdata
    # i.e. NOT cdata['usermeta']['embedOptions']['theme'] == 'default'
