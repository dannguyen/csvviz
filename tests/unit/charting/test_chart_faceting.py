"""
These tests test the affect of vizkit facet* options on the
    rest of the vizkit.chart properties

Overlaps with test_channel_group.test_facetize and clicky/test_facet_flags,
    but more unit based

They do NOT invoke CliRunner i.e. integrated cli output
"""

import pytest

import altair as alt
from pathlib import Path

from csvviz.exceptions import *
import csvviz.settings

from csvviz.vizzes.line import Linekit as Gkit

INPUT_PATH = "examples/jobless.csv"
COMMON_OPTIONS = {
    "xvar": "month:O",
    "yvar": "rate",
    "colorvar": "sector",
    "facetvar": "year:O",
}

# def vfoo(options=COMMON_OPTIONS, input_file=INPUT_PATH) -> Gkit:
#     return Gkit(input_file, options=options)


def cfoo(
    options={},
    input_file=INPUT_PATH,
) -> alt.Chart:
    opts = COMMON_OPTIONS.copy()
    opts.update(options)
    return Gkit(input_file, options=opts).chart_dict


def test_chart_and_encoding_defaults():
    c = cfoo()
    assert "title" not in c

    # size defaults aren't affected...for now TK
    assert c["height"] == Gkit.default_faceted_height
    assert c["width"] == Gkit.default_faceted_width
    assert c["autosize"] == {
        "type": "pad",
        "contains": "padding",
    }

    assert c["encoding"]["facet"] == {
        "field": "year",
        "type": "ordinal",
        "columns": csvviz.settings.DEFAULT_FACET_COLUMNS,
        "spacing": csvviz.settings.DEFAULT_FACET_SPACING,
    }


def test_set_facet_columns():
    c = cfoo({"facet_columns": 42})
    assert c["encoding"]["facet"]["columns"] == 42


def test_set_ininite_facet_columns():
    c = cfoo({"facet_columns": 0})
    assert c["encoding"]["facet"]["columns"] is 0


def test_set_faceted_width_and_height():
    """no different in effect than non-faceted chart"""
    chart = cfoo({"height": 42, "width": 100})
    assert chart["width"] == 100
    assert chart["height"] == 42


def test_set_facted_auto_width_height():
    """basically same as effect in non-faceted chart"""
    chart = cfoo({"height": 0})
    assert chart["height"] == 0
    assert chart["width"] == Gkit.default_faceted_width

    chart = cfoo({"width": 0})
    assert chart["height"] == Gkit.default_faceted_height
    assert chart["width"] == 0
