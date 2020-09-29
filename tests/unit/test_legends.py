import pytest
from click.testing import CliRunner

import click
import json
from pathlib import Path

from csvviz.cmds.scatter import Scatterkit

viz = Scatterkit.register_command()

from csvviz.exceptions import *
from csvviz.settings import *

DEFAULT_ARGS = [
    "-x",
    "mass",
    "-y",
    "volume",
    "--json",
    "--no-preview",
    "examples/vals.csv",
]


##############################################################################################################
# legend
##############################################################################################################
def test_legend_default():
    """when there is a fill --color, there is a legend"""
    result = CliRunner().invoke(viz, ["-c", "breed", *DEFAULT_ARGS])
    cdata = json.loads(result.output)
    legend = cdata["encoding"]["fill"]["legend"]

    assert legend["title"] == "breed"
    assert legend["orient"] == DEFAULT_LEGEND_ORIENTATION


def test_no_legend():
    """hiding the legend sets fill.legend to None explicitly"""

    result = CliRunner().invoke(
        viz, ["--color", "breed", "--size", "velocity", "--no-legend", *DEFAULT_ARGS]
    )
    cdata = json.loads(result.output)

    assert None is cdata["encoding"]["fill"]["legend"]
    assert None is cdata["encoding"]["size"]["legend"]
