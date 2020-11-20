#!/usr/bin/env python
import pytest
from click.testing import CliRunner

import json
from pathlib import Path

from csvviz.exceptions import *
from csvviz.settings import *

from csvviz.vizzes.heatmap import Heatmapkit

heatmap = Heatmapkit.register_command()

INPUT_PATH = "examples/hot.csv"

COMMON_ARGS = [
    INPUT_PATH,
    "--json",
    "--no-preview",
]


def test_heatmapkit():
    kit = Heatmapkit(
        input_file=INPUT_PATH,
        options={
            "xvar": "state",
            "yvar": "item",
            "fillvar": "sold",
        },
    )

    assert kit.viz_commandname == "heatmap"
    assert kit.viz_name == "heatmap"
    assert kit.mark_name == "rect"
    assert kit.color_channel_name == "fill"

    # test its chart representation
    d = kit.chart_dict()
    assert d["mark"]["type"] == "rect"
    assert all(
        c in d["encoding"]
        for c in (
            "x",
            "y",
            "fill",
        )
    )


def test_heatmap_cli_defaults():
    opts = [
        "-x",
        "state",
        "-y",
        "item",
        "-c",
        "sold",
    ]

    c = CliRunner().invoke(heatmap, [*opts, *COMMON_ARGS])

    jdata = json.loads(c.output)

    assert jdata["mark"]["type"] == "rect"

    datavals = list(jdata["datasets"].values())[0]
    assert datavals[0] == {"item": "apples", "sold": 80, "state": "CA"}

    fill = jdata["encoding"]["fill"]
    assert fill["field"] == "sold"
    assert fill["type"] == "quantitative"
    # as opposed to DEFAULT_COLOR_SCHEMES["heatmap"]
    assert fill["scale"]["scheme"] == DEFAULT_COLOR_SCHEMES["ramp"]
