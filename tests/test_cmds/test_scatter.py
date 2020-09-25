#!/usr/bin/env python

import pytest
from click.testing import CliRunner

import json as jsonlib
from pathlib import Path

from csvviz.cmds.scatter import command as scatter
from csvviz.exceptions import *
from csvviz.settings import *

OUTPUT_ARGS = [
    "--json",
    "--no-preview",
    "examples/vals.csv",
]


def test_scatter_defaults():
    """
    MVP, where x is columns[0] and y is columns[1]
    """
    result = CliRunner().invoke(scatter, [*OUTPUT_ARGS])
    cdata = jsonlib.loads(result.output)

    assert cdata["mark"] == "point"

    datavals = list(cdata["datasets"].values())[0]
    assert datavals[0]["mass"] == 0.1

    assert cdata["encoding"]["x"] == {"field": "mass", "type": "quantitative"}
    assert cdata["encoding"]["y"] == {"field": "volume", "type": "quantitative"}


def test_scatter_fill_size():
    """
    setting fill and size
    """
    result = CliRunner().invoke(
        scatter, ["--fill", "breed", "--size", "velocity", *OUTPUT_ARGS]
    )
    cdata = jsonlib.loads(result.output)

    assert cdata["encoding"]["fill"]["field"] == "breed"
    assert cdata["encoding"]["fill"]["type"] == "nominal"
    # 'x' is NOT assumed to be nominal by default
    assert cdata["encoding"]["size"]["field"] == "velocity"
    assert cdata["encoding"]["size"]["type"] == "quantitative"


def test_no_legend_hides_fill_and_size():
    """hiding the legend sets fill.legend to None explicitly"""

    result = CliRunner().invoke(
        scatter, ["--no-legend", "--fill", "breed", "--size", "velocity", *OUTPUT_ARGS]
    )
    cdata = jsonlib.loads(result.output)

    assert None is cdata["encoding"]["size"]["legend"]
