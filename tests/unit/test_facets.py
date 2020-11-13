import pytest
from click.testing import CliRunner

import click
import json
from pathlib import Path

from csvviz.exceptions import *
from csvviz.settings import *


from csvviz.vizkit.viztypes.bar import Barkit

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
    cdata = json.loads(
        CliRunner()
        .invoke(
            viz,
            [
                "-gc",
                "5",
                *DEFAULT_ARGS,
            ],
        )
        .output
    )
    facet = cdata["encoding"]["facet"]
    assert facet["columns"] == 5


def test_facet_column_sort():
    cdata = json.loads(
        CliRunner()
        .invoke(
            viz,
            [
                "-gs",
                "desc",
                *DEFAULT_ARGS,
            ],
        )
        .output
    )
    facet = cdata["encoding"]["facet"]
    assert facet["sort"] == "descending"
