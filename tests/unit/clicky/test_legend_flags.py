"""
TK: no reason why most of these tests can't be refactored to be CLI independent
    and then moved to unit/charting
"""
import pytest
from click.testing import CliRunner

import click
import json
from pathlib import Path

from csvviz.vizzes.scatter import Scatterkit

viz = Scatterkit.register_command()

from csvviz.exceptions import *
from csvviz.settings import *

DEFAULT_ARGS = [
    "--json",
    "--no-preview",
    "examples/vals.csv",
]


##############################################################################################################
# legend
##############################################################################################################
def test_legend_default():
    """when there is a fill --colorvar, there is a legend"""
    result = CliRunner().invoke(viz, ["-c", "breed", *DEFAULT_ARGS])
    cdata = json.loads(result.output)
    legend = cdata["encoding"]["fill"]["legend"]

    assert "title" not in legend  # let Vega automatically infer this
    assert legend["orient"] == DEFAULT_LEGEND_ORIENTATION


def test_no_legend_flag():
    """hiding the legend sets fill.legend to None explicitly"""

    result = CliRunner().invoke(
        viz,
        ["--colorvar", "breed", "--sizevar", "velocity", "--no-legend", *DEFAULT_ARGS],
    )
    cdata = json.loads(result.output)

    assert None is cdata["encoding"]["fill"]["legend"]
    assert None is cdata["encoding"]["size"]["legend"]


@pytest.mark.skip(
    reason="Not needed; Vega automatically infers legend title when it is not explicitly set"
)
def test_legend_with_aggregate_title():
    result = CliRunner().invoke(viz, ["-c", "sum(velocity)", *DEFAULT_ARGS])
    cdata = json.loads(result.output)
    legend = cdata["encoding"]["fill"]["legend"]

    assert legend["title"] == "sum"


@pytest.mark.skip(
    reason="Not needed; Vega automatically infers legend title when it is not explicitly set"
)
def test_legend_with_specified_var_titles():
    result = CliRunner().invoke(
        viz,
        ["--colorvar", "breed|Foo", "--sizevar", "sum(velocity)|Bar", *DEFAULT_ARGS],
    )
    cdata = json.loads(result.output)

    assert "Foo" == cdata["encoding"]["fill"]["legend"].get("title")
    assert "Bar" == cdata["encoding"]["size"]["legend"].get("title")
