#!/usr/bin/env python3
import pandas as pd
from typing import List as ListType

# from IPython import embed as IBREAKPOINT

"""
2020-11-12 note: this is just rando code for a rando feature that should probably be thrown away
"""


class Shape:
    @staticmethod
    def query(
        df: pd.DataFrame, expr: str, inplace: bool = True, **kwargs
    ) -> pd.DataFrame:
        return df.query(expr)

    @staticmethod
    def sort(
        df: pd.DataFrame, cols: ListType[str], ascendings: ListType[bool] = [], **kwargs
    ) -> pd.DataFrame:
        if not ascendings:
            ascendings = list(True for c in cols)
        return df.sort_values(by=cols, ascending=ascendings)


class Edit:
    @staticmethod
    def replace(
        df: pd.DataFrame, to_replace: str, replacement: str, **kwargs
    ) -> pd.DataFrame:
        return df.replace(to_replace=to_replace, value=replacement, regex=True)


class Foo(Edit, Shape):
    pass


def foo(df, inplace: bool = True, **kwargs) -> pd.DataFrame:
    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.pipe.html

    def bar(funcname):
        return getattr(Foo, funcname)

    return (
        df.pipe(bar("query"), **kwargs)
        .pipe(bar("replace"), **kwargs)
        .pipe(bar("sort"), **kwargs)
    )


def main():
    df = pd.read_csv("examples/tings.csv")
    xf = foo(
        df, expr="amount > 20", cols=["name"], to_replace="[A-Z]", replacement="42"
    )
    print(xf.to_csv(index=False))
    # IBREAKPOINT()


if __name__ == "__main__":
    main()
