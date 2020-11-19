#!/usr/bin/env python

import pytest
from click.testing import CliRunner

import json
from pathlib import Path

from csvviz.exceptions import *
from csvviz.settings import *

from csvviz.vizzes.hist import Histkit

hist = Histkit.register_command()


OUTPUT_ARGS = [
    "--json",
    "--no-preview",
    "examples/tings.csv",
]


def test_kit():
    kit = Histkit(
        input_file="examples/tings.csv",
        options={
            "xvar": "amount",
            "is_interactive": True,
            "no_preview": True,
            "to_json": True,
        },
    )

    assert kit.viz_commandname == kit.viz_name == "hist"
    assert kit.mark_name == "bar"
    assert kit.color_channel_name == "fill"


def test_hist_defaults():
    """
    MVP, where x is columns[0] and y is columns[1]

    just a catch all sanity test...
    Should resemble what's in tests/fixtures/bar-basic.json
    """
    result = CliRunner().invoke(hist, ["-x", "amount", *OUTPUT_ARGS])
    cdata = json.loads(result.output)

    assert cdata["mark"]["type"] == "bar"

    datavals = list(cdata["datasets"].values())[0]
    assert datavals[0] == {"amount": 20, "name": "Alice"}
    assert datavals[-1] == {"amount": 42, "name": "Ellie"}

    assert cdata["encoding"]["x"] == {
        "bin": True,
        "field": "amount",
        "type": "quantitative",
    }
    assert cdata["encoding"]["y"] == {"aggregate": "count", "type": "quantitative"}


def test_hist_bincount():
    cdata = json.loads(
        CliRunner().invoke(hist, ["-x", "amount", "-n", "42", *OUTPUT_ARGS]).output
    )
    assert cdata["encoding"]["x"]["bin"]["maxbins"] == 42


def test_hist_bin_step_size():
    cdata = json.loads(
        CliRunner().invoke(hist, ["-x", "amount", "-s", "2.567", *OUTPUT_ARGS]).output
    )
    assert cdata["encoding"]["x"]["bin"]["step"] == 2.567


def test_hist_bin_step_size_accepts_int():
    cdata = json.loads(
        CliRunner().invoke(hist, ["-x", "amount", "-s", "1", *OUTPUT_ARGS]).output
    )
    assert cdata["encoding"]["x"]["bin"]["step"] == 1


def test_hist_bin_step_size_overrides_bin_count():
    cdata = json.loads(
        CliRunner()
        .invoke(
            hist, ["-x", "amount", "--bin-size", "3.5", "--bins", "42", *OUTPUT_ARGS]
        )
        .output
    )
    xbin = cdata["encoding"]["x"]["bin"]
    assert xbin["step"] == 3.5
    assert "maxbins" not in xbin


def test_hist_ordinal_bins():
    """if user wants quantitative value in ordinal bins, they must specify it with Altair shorthand"""
    cdata = json.loads(
        CliRunner().invoke(hist, ["-x", "amount:O", *OUTPUT_ARGS]).output
    )
    x = cdata["encoding"]["x"]
    assert x["bin"] is True
    assert x["type"] == "ordinal"


def test_hist_nominal_x_is_counted_like_standard_bar_chart():
    """
    when xvar is a nominal field, csvviz ignores --bin-size/--bins and does a standard bar chart, except with y='count()'

    csvviz hist -x product -n 20 examples/fruits.csv
        is equivalent to:
    csvviz bar -x product -y 'count(product)' examples/fruits.csv
    """
    cdata = json.loads(CliRunner().invoke(hist, ["-x", "name", *OUTPUT_ARGS]).output)
    y = cdata["encoding"]["y"]
    assert y["aggregate"] == "count"
    assert y["field"] == "name"
    assert y["type"] == "nominal"

    # 'bin' is not set at all
    assert "bin" not in cdata["encoding"]["x"]


def test_hist_nominal_x_bin_settings_ignored_but_warning():
    """if any bin settings are set, but x is nominal, a warning is emitted"""
    result = CliRunner(mix_stderr=False).invoke(
        hist, ["-x", "name", "--bins", "5", *OUTPUT_ARGS]
    )
    assert result.exit_code == 0
    assert (
        """Warning: Since 'name' consists of nominal values, csvviz will ignore bin-specific settings, e.g. -n/--bins and -s/--bin-size"""
        in result.stderr
    )
