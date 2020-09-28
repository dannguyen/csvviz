#!/usr/bin/env python

import pytest
from click.testing import CliRunner

import json
from pathlib import Path

from csvviz.exceptions import *
from csvviz.settings import *

from csvviz.cmds.bar import Barkit

bar = Barkit.register_command()


OUTPUT_ARGS = [
    "--json",
    "--no-preview",
    "examples/tings.csv",
]


def test_bar_defaults():
    """
    MVP, where x is columns[0] and y is columns[1]

    just a catch all sanity test...
    Should resemble what's in tests/fixtures/bar-basic.json
    """
    result = CliRunner().invoke(bar, OUTPUT_ARGS)
    cdata = json.loads(result.output)

    assert cdata["mark"]["type"] == "bar"

    datavals = list(cdata["datasets"].values())[0]
    assert datavals[0] == {"amount": 20, "name": "Alice"}
    assert datavals[-1] == {"amount": 42, "name": "Ellie"}

    assert cdata["encoding"]["x"] == {"field": "name", "type": "nominal"}
    assert cdata["encoding"]["y"] == {"field": "amount", "type": "quantitative"}


def test_bar_x_y():
    """
    setting x and y
    """
    result = CliRunner().invoke(bar, ["-x", "amount", "-y", "amount", *OUTPUT_ARGS])
    cdata = json.loads(result.output)

    assert cdata["encoding"]["x"]["field"] == "amount"
    assert cdata["encoding"]["x"]["type"] == "quantitative"
    # 'x' is NOT assumed to be nominal by default
    assert cdata["encoding"]["y"]["field"] == "amount"
    assert cdata["encoding"]["y"]["type"] == "quantitative"


def test_bar_horizontal():
    """
    Making a horizontal bar chart in Altair means flipping how x and y are specified.

    csvviz does that for the user, i.e. user shouldn't expect x to be 'name', despite the command line setting
    """
    result = CliRunner().invoke(bar, ["-x", "name", "-y", "amount", "-H", *OUTPUT_ARGS])
    cdata = json.loads(result.output)

    assert cdata["encoding"]["x"]["field"] == "amount"
    assert cdata["encoding"]["y"]["type"] == "nominal"


def test_bar_fill():
    """
    fill can be varied by the same column as x
    """
    result = CliRunner().invoke(bar, ["-c", "name", *OUTPUT_ARGS])
    cdata = json.loads(result.output)

    fill = cdata["encoding"]["fill"]
    assert fill["field"] == "name"
    assert fill["type"] == "nominal"


def test_bar_fill_sort():
    cdata = json.loads(
        CliRunner()
        .invoke(bar, ["--color", "name", "--color-sort", "+", *OUTPUT_ARGS])
        .output
    )

    o = cdata["encoding"]["order"]
    assert o["field"] == "name"
    assert o["sort"] == "ascending"

    cdata = json.loads(
        CliRunner().invoke(bar, ["-c", "name", "-cs", "-", *OUTPUT_ARGS]).output
    )

    o = cdata["encoding"]["order"]
    assert o["field"] == "name"
    assert o["sort"] == "descending"


def test_error_when_fill_sort_but_no_fill():
    result = CliRunner().invoke(bar, ["-cs", "-", *OUTPUT_ARGS])
    assert result.exit_code == 1
    assert (
        "MissingDataReference: --color-sort '-' was specified, but no --color value"
        in result.output.strip()
    )


##############################################################################################################
# sort-x
##############################################################################################################
def test_sortx_var_default():
    """default sort is ascending"""
    result = CliRunner().invoke(
        bar, ["-x", "name", "-y", "amount", "-xs", "y", *OUTPUT_ARGS]
    )
    cdata = json.loads(result.output)

    assert (
        cdata["encoding"]["x"]["sort"] == "y"
    )  # {"field": "amount", "order": "ascending"}

    # data ordering is unchanged
    dataset = cdata["datasets"][cdata["data"]["name"]]
    assert dataset[0]["name"] == "Alice"
    assert dataset[-1]["name"] == "Ellie"


def test_sortx_var_reverse():
    """column name prefixed with '-' indicated descending sort"""
    result = CliRunner().invoke(bar, ["--x-sort", "-x", *OUTPUT_ARGS])
    cdata = json.loads(result.output)

    assert (
        cdata["encoding"]["x"]["sort"] == "-x"
    )  # {"field": "amount", "order": "descending"}


def test_sortx_var_error_invalid_column():
    """
    If a non-existent column name is passed into the sort field, Altair accepts it and
    includes it in the ['encoding']['x']['sort'] object, with no apparent effect (similar to sorting by none)

    However, we want to stop and notify the user of the error
    """
    result = CliRunner().invoke(bar, ["--x-sort", "-name", *OUTPUT_ARGS])
    assert result.exit_code == 1
    assert (
        "InvalidDataReference: 'name' is not a valid channel to sort by"
        in result.output.strip()
    )


@pytest.mark.skip(reason="seems like a major edge case, but worth keeping in mind")
def test_sortx_var_handle_column_name_that_starts_with_hyphen():
    """
    TODO: need to create a fixture dataset with column name '-stuff'
    """
    a_result = CliRunner().invoke(bar, ["-xs", r"\-stuff", *OUTPUT_ARGS])
    a_data = json.loads(a_result.output)
    assert a_data["encoding"]["x"]["sort"] == {"field": "-stuff", "order": "ascending"}

    b_result = CliRunner().invoke(bar, ["-xs", r"--stuff", *OUTPUT_ARGS])
    b_data = json.loads(b_result.output)
    assert b_data["encoding"]["x"]["sort"] == {"field": "-stuff", "order": "descending"}
