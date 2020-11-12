from io import StringIO
from typing import (
    List as ListType,
    Union as UnionType,
)


from csv import reader as csv_reader


def parse_delimited_str(
    txt: str,
    delimiter: str = ",",
    minlength: int = 0,
    escapechar=None,
    **csvreader_kwargs,
) -> ListType[UnionType[str]]:
    """
    minlength: expected minimum number of elements. If csv.reader returns a row
        shorter than minlength, it will pad the row with empty strings ''
    """
    row: ListType
    with StringIO(txt) as src:
        kwargs = csvreader_kwargs.copy()
        kwargs["delimiter"] = delimiter
        kwargs["escapechar"] = escapechar

        data = csv_reader(src, **kwargs)
        row = next(data, [])

    for i in range(len(row), minlength):
        row.append("")

    return row
