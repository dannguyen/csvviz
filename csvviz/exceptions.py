class CsvvizError(Exception):
    """Base class for all csvviz user-facing errors."""


class InvalidColumnError(CsvvizError):
    """A referenced column is not in the CSV."""


class ConflictingFlagsError(CsvvizError):
    """Flags combine in a way that doesn't make sense."""


class EmptyDataError(CsvvizError):
    """The input CSV is empty or has too few columns for the chart type."""


class OutputError(CsvvizError):
    """The output path or format is invalid."""
