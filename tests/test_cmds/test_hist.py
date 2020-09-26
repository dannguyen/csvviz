#!/usr/bin/env python

import pytest
from click.testing import CliRunner

import json as jsonlib
from pathlib import Path

from csvviz.cmds.hist import command as hist
from csvviz.exceptions import *
from csvviz.settings import *

OUTPUT_ARGS = [
    "--json",
    "--no-preview",
    "examples/tings.csv",
]


def test_hist_defaults():
    """
    MVP, where x is columns[0] and y is columns[1]

    just a catch all sanity test...
    Should resemble what's in tests/fixtures/bar-basic.json
    """
    result = CliRunner().invoke(hist, ["-x", "amount", *OUTPUT_ARGS])
    cdata = jsonlib.loads(result.output)

    assert cdata["mark"]["type"] == "bar"

    datavals = list(cdata["datasets"].values())[0]
    assert datavals[0] == {"amount": 20, "name": "Alice"}
    assert datavals[-1] == {"amount": 42, "name": "Ellie"}

    assert cdata["encoding"]["x"] == {
        "bin": True,
        "field": "amount",
        "type": "quantitative",
    }
    assert cdata["encoding"]["y"] == {"aggregate": "count", "type": "quantitative"}
