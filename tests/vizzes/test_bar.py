#!/usr/bin/env python

import pytest
from click.testing import CliRunner

import json
from pathlib import Path

from csvviz.exceptions import *
from csvviz.settings import *

from csvviz.vizzes.bar import Barkit

bar = Barkit.register_command()


OUTPUT_ARGS = [
    "--json",
    "--no-preview",
    "examples/tings.csv",
]


def test_kit():
    kit = Barkit(
        input_file="examples/fruits.csv",
        kwargs={
            "xvar": "product",
            "yvar": "revenue",
            "fillvar": "season",
            "is_interactive": True,
            "no_preview": True,
            "to_json": True,
        },
    )

    assert kit.viz_commandname == "bar"
    assert kit.mark_method == "mark_bar"
    assert kit.color_channel_name == "fill"


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


##############################################################################################################
# fill
##############################################################################################################
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
        .invoke(bar, ["--colorvar", "name", "--color-sort", "asc", *OUTPUT_ARGS])
        .output
    )

    o = cdata["encoding"]["order"]
    assert o["field"] == "name"
    assert o["sort"] == "ascending"


def test_bar_fill_sort_desc():
    cdata = json.loads(
        CliRunner().invoke(bar, ["-c", "name", "-cs", "desc", *OUTPUT_ARGS]).output
    )

    o = cdata["encoding"]["order"]
    assert o["field"] == "name"
    assert o["sort"] == "descending"


def test_bar_error_when_fill_sort_but_no_fill():
    result = CliRunner().invoke(bar, ["-cs", "desc", *OUTPUT_ARGS])
    assert result.exit_code == 1
    assert (
        "ConflictingArgs: --color-sort 'desc' was specified, but no --colorvar value"
        in result.output.strip()
    )


def test_bar_error_when_fill_sort_invalid():
    result = CliRunner().invoke(bar, ["-cs", "BOOBOO", *OUTPUT_ARGS])
    assert result.exit_code == 2


@pytest.mark.curious(
    reason="this should be in unit/test_vizkit, as opposed to just Barkit"
)
def test_bar_warn_if_colors_specified_but_no_fill():
    result = CliRunner(mix_stderr=False).invoke(
        bar, ["--color-list", "red,blue", *OUTPUT_ARGS]
    )
    assert result.exit_code == 0
    assert (
        "Warning: --colorvar was not specified, so --color-list and --color-scheme is ignored."
        in result.stderr
    )


##############################################################################################################
# normalize
##############################################################################################################
NORMAL_ARGS = [
    "--json",
    "--no-preview",
    "examples/fruits.csv",
]


@pytest.mark.curious(
    reason="Should this modify default legend title to 'Percentage of'?"
)
def test_bar_normalize():
    """
    y.stack is set to 'normalize'
    y axis is in '%' format
    """
    result = CliRunner().invoke(bar, ["-N", "-c", "season", *NORMAL_ARGS])
    cdata = json.loads(result.output)
    y = cdata["encoding"]["y"]
    assert y["stack"] == "normalize"
    assert y["axis"]["format"] == "%"


def test_bar_error_when_normalize_but_no_fill_color_stack():
    """
    User shouldn't be allowed to create normalized bars of 1 segment, even though it's technically valid
    """
    result = CliRunner().invoke(bar, ["-N", *NORMAL_ARGS])
    assert result.exit_code == 1
    assert (
        "ConflictingArgs: -c/--colorvar needs to be specified when creating a normalized (i.e. stacked) chart"
        in result.output.strip()
    )


##############################################################################################################
# sort-x
##############################################################################################################
def test_bar_sortx_var_default():
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


def test_bar_sortx_var_reverse():
    """column name prefixed with '-' indicated descending sort"""
    result = CliRunner().invoke(bar, ["--x-sort", "-x", *OUTPUT_ARGS])
    cdata = json.loads(result.output)

    assert (
        cdata["encoding"]["x"]["sort"] == "-x"
    )  # {"field": "amount", "order": "descending"}


def test_bar_sortx_var_error_invalid_column():
    """
    If a non-existent column name is passed into the sort field, Altair accepts it and
    includes it in the ['encoding']['x']['sort'] object, with no apparent effect (similar to sorting by none)

    However, we want to stop and notify the user of the error
    """
    result = CliRunner().invoke(bar, ["--x-sort", "-name", *OUTPUT_ARGS])
    assert result.exit_code == 1
    assert (
        "InvalidDataReference: '-name' is not a valid channel to sort by"
        in result.output.strip()
    )


@pytest.mark.skip(reason="Deprecated; --x-sort takes x/y/fill, not column name")
def test_bar_sortx_var_handle_column_name_that_starts_with_hyphen():
    """
    TODO: need to create a fixture dataset with column name '-stuff'
    """
    a_result = CliRunner().invoke(bar, ["-xs", r"\-stuff", *OUTPUT_ARGS])
    a_data = json.loads(a_result.output)
    assert a_data["encoding"]["x"]["sort"] == {"field": "-stuff", "order": "ascending"}

    b_result = CliRunner().invoke(bar, ["-xs", r"--stuff", *OUTPUT_ARGS])
    b_data = json.loads(b_result.output)
    assert b_data["encoding"]["x"]["sort"] == {"field": "-stuff", "order": "descending"}
