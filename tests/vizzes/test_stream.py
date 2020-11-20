#!/usr/bin/env python
import pytest

from click.testing import CliRunner
import json
from pathlib import Path

from csvviz.exceptions import *
from csvviz.settings import *
from csvviz.vizzes.stream import Streamkit

stream = Streamkit.register_command()

INPUT_PATH = "examples/stream.csv"
COMMON_ARGS = [
    INPUT_PATH,
    "--json",
    "--no-preview",
]


def test_streamkit():
    kit = Streamkit(
        input_file=INPUT_PATH,
        options={
            "xvar": "marker",
            "yvar": "pints",
            "fillvar": "region",
        },
    )

    assert kit.viz_commandname == kit.viz_name == "stream"
    assert kit.mark_name == "area"
    assert kit.color_channel_name == "fill"

    # test its chart representation
    d = kit.chart_dict()
    assert d["mark"]["type"] == "area"
    assert all(
        c in d["encoding"]
        for c in (
            "x",
            "y",
            "fill",
        )
    )

    y = d["encoding"]["y"]
    assert y["axis"] is None
    assert y["stack"] == "center"


def test_streamkit_cli_defaults():
    opts = [
        ## by default x,y are set to columns 0,1
        # "-x",
        # "marker",
        # "-y",
        # "pints",
        "-c",
        "region",
    ]

    c = CliRunner().invoke(stream, [*opts, *COMMON_ARGS])
    jdata = json.loads(c.output)

    assert jdata["mark"]["type"] == "area"
    fill = jdata["encoding"]["fill"]
    assert fill["field"] == "region"
    assert fill["type"] == "nominal"
    assert fill["scale"]["scheme"] == DEFAULT_COLOR_SCHEMES["category"]
