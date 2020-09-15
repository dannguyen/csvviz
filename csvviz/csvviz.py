"""Main module."""


"""Console script for csvviz."""

import click

from pathlib import Path
from typing import Any as typeAny, Mapping as typeMapping, NoReturn as typeNoReturn
from typing import Dict as typeDict, List as typeList, Tuple as typeTuple, Union as typeUnion
from typing import IO as typeIO




def clout(*args) -> typeNoReturn:
    """
    top-level method that is used to output to stdout
    """
    outobjects = []
    for obj in args:
        if isinstance(obj, typeMapping):
            obj = jsonlib.dumps(obj, indent=2)
        else:
            obj = str(obj)
        outobjects.append(obj)
    click.echo(' '.join(outobjects), err=False)


def clerr(*args) -> typeNoReturn:
    """
    top-level method that is used to output to stderr
    """

    # TODO: refactor/decorate this jsonlibs stuff
    outobjects = []
    for obj in args:
        if isinstance(obj, typeMapping):
            obj = jsonlib.dumps(obj, indent=2)
        else:
            obj = str(obj)
        outobjects.append(obj)
    click.echo(' '.join(outobjects), err=True)



