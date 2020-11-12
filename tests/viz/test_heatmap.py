#!/usr/bin/env python

import pytest
from click.testing import CliRunner

import json
from pathlib import Path

from csvviz.exceptions import *
from csvviz.settings import *

from csvviz.viz.heatmap import Heatmapkit

heatmap = Heatmapkit.register_command()


HOT_ARGS = [
    "examples/hot.csv",
    "--json",
    "--no-preview",
]


def test_kit():
    kit = Heatmapkit(
        input_file="examples/hot.csv",
        kwargs={
            "xvar": "state",
            "yvar": "item",
            "fillvar": "sold",
            "is_interactive": True,
            "no_preview": True,
            "to_json": True,
        },
    )

    assert kit.viz_commandname == "heatmap"
    assert kit.mark_method == "mark_rect"
    assert kit.color_channeltype == "fill"


def test_heatmap_defaults():
    c = CliRunner().invoke(
        heatmap,
        [
            "-x",
            "state",
            "-y",
            "item",
            "-c",
            "sold",
            *HOT_ARGS,
        ],
    )

    cdata = json.loads(c.output)

    assert cdata["mark"]["type"] == "rect"

    datavals = list(cdata["datasets"].values())[0]
    assert datavals[0] == {"item": "apples", "sold": 80, "state": "CA"}

    # TODO: test fill encoding
