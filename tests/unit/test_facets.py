import pytest
from click.testing import CliRunner

import click
import json
from pathlib import Path

from csvviz.exceptions import *
from csvviz.settings import *


from csvviz.vizzes.bar import Barkit

viz = Barkit.register_command()


DEFAULT_ARGS = [
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
    cdata = json.loads(CliRunner().invoke(viz, DEFAULT_ARGS).output)
    facet = cdata["encoding"]["facet"]
    assert facet["field"] == "company"
    assert facet["type"] == "nominal"
    assert facet.get("columns") is None  # == DEFAULT_FACET_COLUMNS
    assert facet.get("sort") is None
    assert cdata["resolve"]["axis"] == {"x": "independent"}


def test_facet_column_count():
    x = CliRunner().invoke(viz, ["--gc", "5", *DEFAULT_ARGS])
    jdata = json.loads(x.output)
    assert jdata["encoding"]["facet"]["columns"] == 5

    x = CliRunner().invoke(viz, ["--grid-columns", "1", *DEFAULT_ARGS])
    jdata = json.loads(x.output)
    assert jdata["encoding"]["facet"]["columns"] == 1


def test_facet_column_sort():
    x = CliRunner().invoke(viz, ["--gs", "desc", *DEFAULT_ARGS])
    jdata = json.loads(x.output)
    assert jdata["encoding"]["facet"]["sort"] == "descending"

    x = CliRunner().invoke(viz, ["--grid-sort", "asc", *DEFAULT_ARGS])
    jdata = json.loads(x.output)
    assert jdata["encoding"]["facet"]["sort"] == "ascending"
