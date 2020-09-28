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
    out = CliRunner().invoke(viz, DEFAULT_ARGS).output
    cdata = json.loads(out)
    assert cdata["encoding"]["facet"] == {
        "field": "company",
        "type": "nominal",
        "columns": DEFAULT_FACET_COLUMNS,
    }
    assert cdata["resolve"]["axis"] == {"x": "independent"}
