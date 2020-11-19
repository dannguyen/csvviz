#!/usr/bin/env python

import pytest
from click.testing import CliRunner

import json
from pathlib import Path

from csvviz.exceptions import *
from csvviz.settings import *

from csvviz.vizzes.scatter import Scatterkit

scatter = Scatterkit.register_command()

OUTPUT_ARGS = [
    "--json",
    "--no-preview",
    "examples/vals.csv",
]


def test_scatterkit():
    kit = Scatterkit(
        input_file="examples/vals.csv",
        options={
            "xvar": "mass",
            "yvar": "volume",
            "fillvar": "breed",
            "is_interactive": True,
            "no_preview": True,
            "to_json": True,
        },
    )

    assert kit.viz_commandname == kit.viz_name == "scatter"
    assert kit.mark_name == "point"
    assert kit.color_channel_name == "fill"


def test_scatter_defaults():
    """
    MVP, where x is columns[0] and y is columns[1]
    """
    result = CliRunner().invoke(scatter, [*OUTPUT_ARGS])
    cdata = json.loads(result.output)

    assert cdata["mark"]["type"] == "point"

    datavals = list(cdata["datasets"].values())[0]
    assert datavals[0]["mass"] == 0.1

    assert cdata["encoding"]["x"] == {"field": "mass", "type": "quantitative"}
    assert cdata["encoding"]["y"] == {"field": "volume", "type": "quantitative"}


def test_scatter_bubble():
    """
    just a scatter with -s/--sizevar set
    """
    result = CliRunner().invoke(scatter, ["-s", "velocity", *OUTPUT_ARGS])
    cdata = json.loads(result.output)
    esize = cdata["encoding"]["size"]

    assert esize["field"] == "velocity"
    assert esize["type"] == "quantitative"


def test_scatter_default_legends():
    """
    by default, fill --colorvar and --sizevar will have legends when specified
    """
    result = CliRunner().invoke(
        scatter, ["-c", "breed", "-s", "velocity", *OUTPUT_ARGS]
    )
    cdata = json.loads(result.output)
    assert cdata["encoding"]["fill"]["legend"]["orient"] == DEFAULT_LEGEND_ORIENTATION

    assert "title" not in cdata["encoding"]["fill"]["legend"]  # ["title"] == "breed"
    assert "title" not in cdata["encoding"]["size"]["legend"]  # ["title"] == "velocity"


def test_scatter_fill_size():
    """
    setting fill and size
    """
    result = CliRunner().invoke(
        scatter, ["--colorvar", "breed", "--sizevar", "velocity", *OUTPUT_ARGS]
    )
    cdata = json.loads(result.output)

    assert cdata["encoding"]["fill"]["field"] == "breed"
    assert cdata["encoding"]["fill"]["type"] == "nominal"
    # 'x' is NOT assumed to be nominal by default
    assert cdata["encoding"]["size"]["field"] == "velocity"
    assert cdata["encoding"]["size"]["type"] == "quantitative"


def test_scatter_no_legend_hides_fill_color_and_size():
    """hiding the legend sets fill.legend to None explicitly"""

    result = CliRunner().invoke(
        scatter,
        ["--no-legend", "--colorvar", "breed", "--sizevar", "velocity", *OUTPUT_ARGS],
    )
    cdata = json.loads(result.output)

    assert None is cdata["encoding"]["size"]["legend"]


def test_scatter_colors():
    cdata = json.loads(
        CliRunner()
        .invoke(scatter, ["-c", "breed", "-C", "red,yellow", *OUTPUT_ARGS])
        .output
    )
    e = cdata["encoding"]["fill"]
    assert e["scale"]["range"] == ["red", "yellow"]
