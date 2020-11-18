import pytest
from click.testing import CliRunner

import click
import json
from pathlib import Path

from csvviz.exceptions import *
import csvviz.settings


from csvviz.vizzes.bar import Barkit

viz = Barkit.register_command()


COMMON_ARGS = [
    "examples/stocks.csv",
    "-x",
    "date",
    "-y",
    "price",
    "-g",
    "company",
    "--json",
    "--no-preview",
]


def test_facet_defaults():
    cdata = json.loads(CliRunner().invoke(viz, COMMON_ARGS).output)
    facet = cdata["encoding"]["facet"]
    assert facet["field"] == "company"
    assert facet["type"] == "nominal"
    assert cdata["resolve"]["axis"] == {"x": "independent"}

    assert facet.get("columns") == csvviz.settings.DEFAULT_FACET_COLUMNS
    assert facet.get("sort") is None


def test_set_facet_columns():
    x = CliRunner().invoke(viz, ["--grid-columns", "1", *COMMON_ARGS])
    jdata = json.loads(x.output)
    assert jdata["encoding"]["facet"]["columns"] == 1

    x = CliRunner().invoke(viz, ["--gc", "5", *COMMON_ARGS])
    jdata = json.loads(x.output)
    assert jdata["encoding"]["facet"]["columns"] == 5


def test_set_facet_columns_to_zero():
    x = CliRunner().invoke(viz, ["--gc", "0", *COMMON_ARGS])
    jdata = json.loads(x.output)
    assert jdata["encoding"]["facet"]["columns"] == 0


def test_facet_column_sort():
    x = CliRunner().invoke(viz, ["--gs", "desc", *COMMON_ARGS])
    jdata = json.loads(x.output)
    assert jdata["encoding"]["facet"]["sort"] == "descending"

    x = CliRunner().invoke(viz, ["--grid-sort", "asc", *COMMON_ARGS])
    jdata = json.loads(x.output)
    assert jdata["encoding"]["facet"]["sort"] == "ascending"
