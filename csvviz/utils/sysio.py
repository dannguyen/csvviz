import json
import sys
from typing import Any as AnyType, Mapping as MappingType, NoReturn as NoReturnType

import click
from csvviz import __version__
from csvviz.settings import *


def clout(*args, use_stderr: bool = False) -> NoReturnType:
    """top-level method that is used to output to stdout"""
    output = [
        json.dumps(a, indent=2) if isinstance(a, MappingType) else str(a) for a in args
    ]
    click.echo(" ".join(output), err=use_stderr)


def clerr(*args) -> NoReturnType:
    """top-level method that is used to output to stderr"""
    clout(*args, use_stderr=True)


def clexit(code: int, message: AnyType = None):
    """this function exists because I don't understand Click's wrapping of error handling"""
    if message:
        clerr(message)
    sys.exit(code)
