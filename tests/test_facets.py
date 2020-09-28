import pytest
from click.testing import CliRunner

import click
import json as json
from pathlib import Path

from csvviz.cmds.bar import command as viz

from csvviz.exceptions import *
from csvviz.settings import *

DEFAULT_ARGS = [
    "-x",
    "date",
    "-y",
    "price",
    "-F",
    "company",
    "--json",
    "--no-preview",
    "examples/stocks.csv",
]


def test_facet_defaults():

    cdata = json.loads(CliRunner().invoke(viz, DEFAULT_ARGS).output)
    assert cdata["encoding"]["facet"] == {
        "field": "company",
        "type": "nominal",
        "columns": DEFAULT_FACET_COLUMNS,
    }
    assert cdata["resolve"]["axis"] == {"x": "independent"}
