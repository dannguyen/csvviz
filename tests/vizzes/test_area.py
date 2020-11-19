#!/usr/bin/env python

import pytest
from click.testing import CliRunner

import json
from pathlib import Path

from csvviz.exceptions import *
from csvviz.settings import *

from csvviz.vizzes.area import Areakit

area = Areakit.register_command()

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


def test_kit():
    kit = Areakit(
        input_file="examples/fruits.csv",
        options={
            "xvar": "product",
            "yvar": "revenue",
            "fillvar": "season",
            "is_interactive": True,
            "no_preview": True,
            "to_json": True,
        },
    )

    assert kit.viz_commandname == "area"
    assert kit.viz_name == "area"
    assert kit.color_channel_name == "fill"


def test_area_defaults():
    """
    MVP, where x is columns[0] and y is columns[1]

    just a catch all sanity test...
    Should resemble what's in tests/fixtures/bar-basic.json
    """
    cdata = json.loads(CliRunner().invoke(area, [*TONK_ARGS]).output)

    assert cdata["mark"]["type"] == "area"

    datavals = list(cdata["datasets"].values())[0]
    assert datavals[0] == {"date": "2007-01-01", "price": 37.67}
    assert datavals[-1] == {"date": "2010-03-01", "price": 128.82}

    # even though date is in YYYY-MM-DD format, Altair doesn't automatically know it's temporal
    assert cdata["encoding"]["x"] == {"field": "date", "type": "nominal"}
    assert cdata["encoding"]["y"] == {"field": "price", "type": "quantitative"}


def test_area_multiseries_defaults():
    cdata = json.loads(
        CliRunner()
        .invoke(
            area, ["-x", "date", "-y", "price", "--colorvar", "company", *STOCK_ARGS]
        )
        .output
    )
    e = cdata["encoding"]["fill"]
    assert e["field"] == "company"
    assert e["type"] == "nominal"
    assert "title" not in e["legend"]  # ["title"] == "company"


def test_area_colors():
    cdata = json.loads(
        CliRunner()
        .invoke(
            area,
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
    e = cdata["encoding"]["fill"]
    assert e["scale"]["range"] == ["red", "yellow"]


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
def test_area_normalize():
    """
    y.stack is set to 'normalize'
    y axis is in '%' format
    """
    result = CliRunner().invoke(area, ["-N", "-c", "season", *NORMAL_ARGS])
    cdata = json.loads(result.output)
    y = cdata["encoding"]["y"]
    assert y["stack"] == "normalize"
    assert y["axis"]["format"] == "%"


def test_area_error_when_normalize_but_no_fill_color_stack():
    """
    User shouldn't be allowed to create normalized bars of 1 segment, even though it's technically valid
    """
    result = CliRunner().invoke(area, ["-N", *NORMAL_ARGS])
    assert result.exit_code == 1
    assert (
        "ConflictingArgs: -c/--colorvar needs to be specified when creating a normalized (i.e. stacked) chart"
        in result.output.strip()
    )


#############################################
# color-sort
# (TKD)
#############################################
@pytest.mark.skip(
    reason="TKD: Deprecating all color-sorting until i figure out a more graceful solution"
)
def test_area_fill_sort():
    cdata = json.loads(
        CliRunner()
        .invoke(
            area,
            [
                "-x",
                "date",
                "-y",
                "price",
                "--colorvar",
                "company",
                "--color-sort",
                "asc",
                *STOCK_ARGS,
            ],
        )
        .output
    )
    o = cdata["encoding"]["order"]
    assert o["field"] == "company"
    assert o["sort"] == "ascending"


@pytest.mark.skip(
    reason="TKD: Deprecating all color-sorting until i figure out a more graceful solution"
)
def test_area_fill_sort_desc():
    cdata = json.loads(
        CliRunner()
        .invoke(
            area,
            ["-x", "date", "-y", "price", "-c", "company", "--cs", "desc", *STOCK_ARGS],
        )
        .output
    )
    o = cdata["encoding"]["order"]
    assert o["field"] == "company"
    assert o["sort"] == "descending"


@pytest.mark.skip(
    reason="TKD: Deprecating all color-sorting until i figure out a more graceful solution"
)
def test_area_error_when_fill_sort_but_no_fill():
    result = CliRunner().invoke(
        area, ["-x", "date", "-y", "price", "--cs", "asc", *STOCK_ARGS]
    )
    assert result.exit_code == 1
    assert (
        "ConflictingArgs: --color-sort 'asc' was specified, but no --colorvar value"
        in result.output.strip()
    )
