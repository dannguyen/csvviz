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


#########################################
# common Click.command options decorators
#########################################


def input_file_decor(fn):
    decorator = click.argument("input_file", type=click.File("r"))
    fn = decorator(fn)
    return fn


def output_options_decor(fn):
    """common input output/options"""
    for decorator in reversed(
        (
            click.option(
                "--json/--no-json",
                "-j /",
                "to_json",
                default=False,
                help="Output to stdout the Vega JSON representation",
            ),
            click.option(
                "--no-preview",
                "--np",
                is_flag=True,
                help="By default, csvviz opens a web browser to show the chart",
            ),
            click.option(
                "--interactive/--static",
                "is_interactive",
                default=True,
                help="Produce an interactive (default) or static version of the chart, in HTML+JS",
            ),
        )
    ):
        fn = decorator(fn)
    return fn


def visual_options_decor(fn):
    """common visual options"""
    for decorator in (
        click.option(
            "-c",
            "--colors",
            type=click.STRING,
            help="A comma-delimited list of colors to use for the relevant marks",
        ),
        click.option(
            "-C",
            "--color-scheme",
            type=click.STRING,
            help="The name of a Vega color scheme to use for fill (this is overridden by -c/--colors)",
        ),
        click.option(
            "--theme",
            type=click.Choice(alt.themes.names(), case_sensitive=False),
            default="default",
            help="choose a built-in theme for chart",
        ),  # TODO: refactor alt.themes.names() to constant
        click.option("--title", "-t", type=click.STRING, help="A title for the chart"),
        click.option("--no-legend", is_flag=True, help="Omits the legend"),
    ):
        fn = decorator(fn)
    return fn


def axis_options_decor(fn):
    fn = click.option(
        "--xlim",
        type=click.STRING,
        help="Set the min,max of the x-axis with a comma delimited string, e.g. '-10,50'",
    )(fn)
    fn = click.option(
        "--ylim",
        type=click.STRING,
        help="Set the min,max of the y-axis with a comma delimited string, e.g. '-10,50'",
    )(fn)

    return fn


def facet_options_decor(fn):
    return click.option(
        "--facet", "-F", "facetvar", type=click.STRING, help="The var to facet by TKTK"
    )(fn)


def standard_options_decor(fn):
    fn = input_file_decor(fn)
    fn = output_options_decor(fn)
    fn = visual_options_decor(fn)
    fn = axis_options_decor(fn)
    fn = facet_options_decor(fn)
    return fn
