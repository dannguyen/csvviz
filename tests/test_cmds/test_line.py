#!/usr/bin/env python

import pytest
from click.testing import CliRunner

import json
from pathlib import Path

from csvviz.cmds.line import command as line
from csvviz.exceptions import *
from csvviz.settings import *

TONK_ARGS = [
    "examples/tonk.csv",
    "--json",
    "--no-preview",
]

STOCK_ARGS = [
    "examples/stocks.csv",
    "--json",
    "--no-preview",
]


def test_line_defaults():
    """
    MVP, where x is columns[0] and y is columns[1]

    just a catch all sanity test...
    Should resemble what's in tests/fixtures/bar-basic.json
    """
    cdata = json.loads(CliRunner().invoke(line, [*TONK_ARGS]).output)

    assert cdata["mark"]["type"] == "line"

    datavals = list(cdata["datasets"].values())[0]
    assert datavals[0] == {"date": "2000-01-01", "price": 64.56}
    assert datavals[-1] == {"date": "2010-03-01", "price": 128.82}

    # even though date is in YYYY-MM-DD format, Altair doesn't automatically know it's temporal
    assert cdata["encoding"]["x"] == {"field": "date", "type": "nominal"}
    assert cdata["encoding"]["y"] == {"field": "price", "type": "quantitative"}


def test_line_multiseries_defaults():
    cdata = json.loads(
        CliRunner()
        .invoke(line, ["-x", "date", "-y", "price", "-s", "company", *STOCK_ARGS])
        .output
    )
    assert cdata["encoding"]["stroke"] == {"field": "company", "type": "nominal"}
