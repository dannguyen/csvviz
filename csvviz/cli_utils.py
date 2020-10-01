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
from csvviz.settings import *


def clout(*args) -> typeNoReturn:
    """
    top-level method that is used to output to stdout
    """
    outobjects = []
    for obj in args:
        if isinstance(obj, typeMapping):
            obj = json.dumps(obj, indent=2)
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

    # TODO: refactor/decorate this jsons stuff
    outobjects = []
    for obj in args:
        if isinstance(obj, typeMapping):
            obj = json.dumps(obj, indent=2)
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


#########################################
# common Click.command options decorators
#########################################


# TODO: figure out how to use stdin without '-':
# https://stackoverflow.com/questions/56351195/how-to-specify-a-default-value-for-argument-list-processed-by-click
# class FilesDefaultToStdin(click.Argument):
#     def __init__(self, *args, **kwargs):
#         kwargs['nargs'] = -1
#         kwargs['type'] = click.File('r')
#         super().__init__(*args, **kwargs)

#     # def full_process_value(self, ctx, value):
#     #     return super().process_value(ctx, value or ('-', ))


def check_piped_arg(ctx, param, value):
    """
    hack courtesy of: https://github.com/pallets/click/issues/1202
    """
    if value:
        return value
    else:
        if not sys.stdin.isatty():
            return click.get_text_stream("stdin")
        else:
            ctx.fail(
                f"Missing argument: {param.human_readable_name}.\n"
                "Pass in a file path, or explicitly pass in '-' for stdin, "
                "or just pipe into the command."
            )


STANDARD_OPTS = {}

"""common input output/options"""
STANDARD_OPTS["io"] = {
    "input_file": click.argument(
        "input_file", type=click.File("r"), required=False, callback=check_piped_arg
    ),
    "is_interactive": click.option(
        "--interactive/--static",
        "is_interactive",
        default=True,
        help="Produce an interactive (default) or static version of the chart, in HTML+JS",
    ),
    "json": click.option(
        "--json/--no-json",
        "-j /",
        "to_json",
        default=False,
        help="Output to stdout the Vega JSON representation",
    ),
    "no_preview": click.option(
        "--no-preview",
        "--np",
        is_flag=True,
        help="By default, csvviz opens a web browser to show the chart",
    ),
}


STANDARD_OPTS["visual"] = {
    "colors": click.option(
        "--colors",
        "-C",
        type=click.STRING,
        help="A comma-delimited list of colors to use for the relevant marks",
    ),
    "color_scheme": click.option(
        "--color-scheme",
        "-CS",
        type=click.STRING,
        help="The name of a Vega color scheme to use for fill (this is overridden by -C/--colors)",
    ),
    "theme": click.option(
        "--theme",
        type=click.Choice(alt.themes.names(), case_sensitive=False),
        default="default",
        help="choose a built-in theme for chart",
    ),  # TODO: refactor alt.themes.names() to constant
    "title": click.option(
        "--title", "-t", type=click.STRING, help="A title for the chart"
    ),
    "no_legend": click.option(
        "--no-legend", is_flag=True, help="Omits any/all legends"
    ),
}


STANDARD_OPTS["axis"] = {
    "xlim": click.option(
        "--xlim",
        type=click.STRING,
        help="Set the min,max of the x-axis with a comma delimited string, e.g. '-10,50'",
    ),
    "ylim": click.option(
        "--ylim",
        type=click.STRING,
        help="Set the min,max of the y-axis with a comma delimited string, e.g. '-10,50'",
    ),
}


STANDARD_OPTS["facet"] = {
    "facetvar": click.option(
        "--grid",
        "-g",
        "facetvar",
        type=click.STRING,
        help="The name of the column to use as a facet for creating a grid of multiple charts",
    ),
    "facetcolumns": click.option(
        "--grid-columns",
        "-gc",
        "facetcolumns",
        default=0,
        type=click.INT,
        help="Number of columns per grid row. Default is '0' for infinite.",
    ),
    "facetsort": click.option(
        "--grid-sort",
        "-gs",
        "facetsort",
        type=click.Choice(["asc", "desc"], case_sensitive=False),
        help="Sort the grid of charts by its facet variable in ascending or descending order.",
    ),
}


def standard_options_decor(fn, exclude_options=[]):
    for groupkey, opts in STANDARD_OPTS.items():
        for oname, o in opts.items():
            if oname not in exclude_options:
                fn = o(fn)
    return fn
