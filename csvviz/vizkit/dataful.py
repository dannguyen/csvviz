"""basically a wrapper around pandas.DataFrame"""

import pandas as pd
from typing import (
    # Dict as DictType,
    List as ListType,
    # NoReturn as NoReturnType,
    # Optional as OptionalType,
    # Tuple as TupleType,
    # Union as UnionType,
)


class Dataful:
    def __init__(self, data):
        """this is basically an abstract class"""
        self._dataframe = data

    @property
    def df(self) -> pd.DataFrame:
        return self._dataframe

    @property
    def column_names(self) -> ListType[str]:
        return list(self.df.columns)
