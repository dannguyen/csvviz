"""Main module."""


"""Console script for csvviz."""


from pathlib import Path
import sys
from typing import Any as typeAny, Mapping as typeMapping, NoReturn as typeNoReturn
from typing import (
    Dict as typeDict,
    List as typeList,
    Tuple as typeTuple,
    Union as typeUnion,
)
from typing import IO as typeIO


import altair as alt
import click
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
    click.echo(" ".join(outobjects), err=False)


def clexit(code: int, message: typeAny = None):
    if message:
        clerr(message)
    sys.exit(code)


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
    click.echo(" ".join(outobjects), err=True)


def print_version(ctx=None, param=None, value=None) -> typeNoReturn:
    """
    https://click.palletsprojects.com/en/3.x/options/#callbacks-and-eager-options
    """
    if not ctx:
        clout(__version__)
    else:
        # this is being used as a callback
        if not value or ctx.resilient_parsing:
            return
        clout(__version__)
        ctx.exit()




r'''


def decor_option_sets(*option_sets):
    def decorate(func):
        for options in reversed(option_sets):
            for opt in reversed(options):
                func = opt(func)
        return func

    return decorate


@click.command()
@decor_option_sets(OPTIONS_COMMON, OPTIONS_OUTPUT)
@click.argument(etc)
def vizname(**kwargs):
    ladeedah


OPTIONS_COMMON = [
    click.option(
        "-s",
        "--service",
        type=click.Choice(["wayback",]),
        default="wayback",
        help="The service, e.g. wayback, permacc",
    ),
]

OPTIONS_OUTPUT = [
    click.option(
        "-j",
        "--json",
        "output_json",
        is_flag=True,
        help="""By default, this subcommand returns a snapshot URL if successful, and nothing if not successful. Set this flag to return
            the full JSON response""",
    ),
    click.option("-q", "--quiet", is_flag=True, help="Same as -v/--verbosity 0"),
    click.option(
        "-v",
        "--verbosity",
        type=click.IntRange(min=0, max=2),
        default=2,
        help="""\b
                Verbosity of log messages:
                  0: Silence (except errors)
                  1: Informational messages logged
                  2: Verbose debug log messages
                  """,
    ),
]






'''
