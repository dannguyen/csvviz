"""Main module."""


"""Console script for csvviz."""

import click

from pathlib import Path
from typing import Any as typeAny, Mapping as typeMapping, NoReturn as typeNoReturn
from typing import Dict as typeDict, List as typeList, Tuple as typeTuple, Union as typeUnion
from typing import IO as typeIO


from csvviz import __version__


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



def print_version(ctx=None, param=None, value=None) -> typeNoReturn:
    """
    https://click.palletsprojects.com/en/3.x/options/#callbacks-and-eager-options
    """
    if not ctx:
        clout(csvviz_version)
    else:
        # this is being used as a callback
        if not value or ctx.resilient_parsing:
            return
        clout(csvviz_version)
        ctx.exit()
