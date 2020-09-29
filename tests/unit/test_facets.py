import pytest
from click.testing import CliRunner

import click
import json
from pathlib import Path

from csvviz.exceptions import *
from csvviz.settings import *


from csvviz.cmds.bar import Barkit

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

    assert cdata["resolve"]["axis"] == {"x": "independent"}


def test_facet_columns():
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
