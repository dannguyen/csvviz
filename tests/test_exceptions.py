import pytest

from csvviz.exceptions import (
    CsvvizError,
    InvalidColumnError,
    ConflictingFlagsError,
    EmptyDataError,
    OutputError,
)


def test_all_errors_subclass_csvviz_error():
    for cls in (
        InvalidColumnError,
        ConflictingFlagsError,
        EmptyDataError,
        OutputError,
    ):
        assert issubclass(cls, CsvvizError)


def test_csvviz_error_is_exception():
    assert issubclass(CsvvizError, Exception)


def test_invalid_column_error_carries_message():
    err = InvalidColumnError("column 'foo' not found")
    assert "foo" in str(err)
