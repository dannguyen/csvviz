from pathlib import Path

import pandas as pd
import pytest

from csvviz.data import load_csv
from csvviz.exceptions import EmptyDataError, InvalidColumnError
from csvviz.specs import BarSpec, HeatmapSpec, HistSpec, LineSpec

FIXTURES = Path(__file__).parent / "fixtures"


def test_load_csv_from_file():
    spec = BarSpec(input_path=str(FIXTURES / "tings.csv"))
    df = load_csv(spec)
    assert list(df.columns) == ["name", "amount"]
    assert len(df) == 5


def test_xvar_defaults_to_first_column():
    spec = BarSpec(input_path=str(FIXTURES / "tings.csv"))
    load_csv(spec)
    assert spec.xvar == "name"


def test_yvar_defaults_to_second_column():
    spec = BarSpec(input_path=str(FIXTURES / "tings.csv"))
    load_csv(spec)
    assert spec.yvar == "amount"


def test_explicit_xvar_not_overridden():
    spec = LineSpec(input_path=str(FIXTURES / "stocks.csv"), xvar="date")
    load_csv(spec)
    assert spec.xvar == "date"


def test_heatmap_valuevar_defaults_to_third_column():
    spec = HeatmapSpec(input_path=str(FIXTURES / "hot.csv"))
    load_csv(spec)
    assert spec.xvar == "state"
    assert spec.yvar == "item"
    assert spec.valuevar == "sold"


def test_hist_does_not_resolve_yvar():
    spec = HistSpec(input_path=str(FIXTURES / "tings.csv"))
    load_csv(spec)
    assert spec.xvar == "name"
    assert spec.yvar is None


def test_invalid_xvar_raises():
    spec = BarSpec(input_path=str(FIXTURES / "tings.csv"), xvar="nope")
    with pytest.raises(InvalidColumnError) as exc:
        load_csv(spec)
    assert "nope" in str(exc.value)
    assert "name" in str(exc.value)


def test_invalid_colorvar_raises():
    spec = BarSpec(input_path=str(FIXTURES / "tings.csv"), colorvar="bogus")
    with pytest.raises(InvalidColumnError):
        load_csv(spec)


def test_empty_csv_raises(tmp_path):
    p = tmp_path / "empty.csv"
    p.write_text("")
    spec = BarSpec(input_path=str(p))
    with pytest.raises(EmptyDataError):
        load_csv(spec)


def test_single_column_csv_raises_for_bar(tmp_path):
    p = tmp_path / "one.csv"
    p.write_text("only\n1\n2\n")
    spec = BarSpec(input_path=str(p))
    with pytest.raises(EmptyDataError):
        load_csv(spec)
