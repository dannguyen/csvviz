from pathlib import Path
import sys
from typing import Any as AnyType, Mapping as MappingType, NoReturn as NoReturnType


import click
from csvviz import __version__
from csvviz.settings import *


def _echo(*args, use_stderr) -> NoReturnType:
    outobjects = []
    for obj in args:
        if isinstance(obj, MappingType):
            obj = json.dumps(obj, indent=2)
        else:
            obj = str(obj)
        outobjects.append(obj)
    click.echo(" ".join(outobjects), err=use_stderr)


def clout(*args) -> NoReturnType:
    """
    top-level method that is used to output to stdout
    """
    _echo(*args, use_stderr=False)


def clerr(*args) -> NoReturnType:
    """
    top-level method that is used to output to stderr
    """

    # TODO: refactor/decorate this jsons stuff
    _echo(*args, use_stderr=True)


def clexit(code: int, message: AnyType = None):
    if message:
        clerr(message)
    sys.exit(code)
