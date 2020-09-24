from pathlib import Path
from typing import Any as typeAny, Mapping as typeMapping, NoReturn as typeNoReturn
from typing import (
    Dict as typeDict,
    List as typeList,
    Tuple as typeTuple,
    Union as typeUnion,
)
from typing import IO as typeIO

import numpy as np
import pandas as pd


from csvviz.exceptions import *


class Datakit(object):
    def __init__(self, input_path: typeUnion[typeIO, Path, str]):
        self.input_path = input_path
        self._load_data()

    def _load_data(self) -> typeNoReturn:
        self._dataframe = pd.read_csv(self.input_path)
        # TODO:
        # validate that it's a flat table
        #

    @property
    def df(self) -> pd.DataFrame:
        return self._dataframe

    @property
    def column_names(self) -> typeList[str]:
        return list(self.df.columns)

    @property
    def schema(self) -> typeDict[str, np.dtype]:
        return dict(self.df.dtypes)

    # ## data selectors
    # # https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html
    # # https://www.shanelynn.ie/select-pandas-dataframe-rows-and-columns-using-iloc-loc-and-ix/#iloc-selection

    def get_column(self, column_index: typeUnion[str, int]) -> pd.Series:
        """accepts either column_index as int, or as a column_name string"""
        if isinstance(column_index, int):
            return self.df[column_index]
        else:
            return self.df.iloc[:, column_index]

    def get_row(self, row_index: int) -> pd.Series:
        return self.df.iloc[row_index]

    def get_value(
        self, row_index: int, column_index: typeUnion[str, int]
    ) -> typeAny:  # technically it's limited to numpy ty pes
        if not isinstance(column_index, int):
            column_index = self.column_names.index(column_index)

        return self.df.iloc[row_index, column_index]

    def resolve_column(self, colname: typeUnion[str]) -> typeTuple[str, dict]:
        """
        Given a column parameter, e.g. a column name meant to be used as xvar/yvar/fill:
            - 'name'
            - 'amount'
            - 'birthdate:time' # TODO meta syntax

        Return the canonical column name, and the meta configuration stuff (e.g. datatype)

        Note: this method was initially created to handle situation in which user specifies columns by ID
            (i.e. integer). That functionality has been deemed not worth it, so now this method is very
            very trivial (e.g. just returns colnmae)
        """
        meta = {}
        if colname not in self.column_names:
            raise InvalidColumnName(
                f"'{colname}' is not a valid column name for the given dataset"
            )

        return (colname, meta)
