#!/usr/bin/env python

import pytest
from click.testing import CliRunner

import json
from pathlib import Path

from csvviz.exceptions import *
from csvviz.settings import *

from csvviz.viz.line import Linekit

line = Linekit.register_command()

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
    cdata = json.loads(CliRunner().invoke(line, TONK_ARGS).output)

    assert cdata["mark"]["type"] == "line"

    datavals = list(cdata["datasets"].values())[0]
    assert datavals[0] == {"date": "2007-01-01", "price": 37.67}
    assert datavals[-1] == {"date": "2010-03-01", "price": 128.82}

    # even though date is in YYYY-MM-DD format, Altair doesn't automatically know it's temporal
    assert cdata["encoding"]["x"] == {"field": "date", "type": "nominal"}
    assert cdata["encoding"]["y"] == {"field": "price", "type": "quantitative"}


def test_line_multiseries_defaults():
    cdata = json.loads(
        CliRunner()
        .invoke(line, ["-x", "date", "-y", "price", "-c", "company", *STOCK_ARGS])
        .output
    )
    e = cdata["encoding"]["stroke"]
    assert e["field"] == "company"
    assert e["type"] == "nominal"
    assert "title" not in e["legend"]  # ["title"] == "company"


def test_line_colors():
    cdata = json.loads(
        CliRunner()
        .invoke(
            line,
            [
                "-x",
                "date",
                "-y",
                "price",
                "-c",
                "company",
                "-C",
                "red,yellow",
                *STOCK_ARGS,
            ],
        )
        .output
    )
    e = cdata["encoding"]["stroke"]
    assert e["scale"]["range"] == ["red", "yellow"]
