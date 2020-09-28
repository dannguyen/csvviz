import importlib
import json as jsonlib
from pathlib import Path
import re
import sys
from typing import Any as typeAny, Mapping as typeMapping, NoReturn as typeNoReturn
from typing import (
    Dict as typeDict,
    List as typeList,
    Tuple as typeTuple,
    Union as typeUnion,
)
from typing import IO as typeIO

import click

# from csvviz import __version__ as csvviz_version
from csvviz.cli_utils import clout, clerr, print_version


SUBCOMMAND_PATHS = Path("csvviz/cmds/").glob("*.py")


# def _callback_print_version(ctx, param, value) -> typeNoReturn:
#     """
#     https://click.palletsprojects.com/en/3.x/options/#callbacks-and-eager-options
#     """
#     if not value or ctx.resilient_parsing:
#         return
#     clout(csvviz_version)
#     ctx.exit()


@click.group()
@click.option(
    "--version",
    callback=print_version,
    is_eager=True,
    is_flag=True,
    help="Print the version of csvviz",
)
def apex(**kwargs):
    """Welcome to csvviz"""

    pass


@apex.command()
@click.argument("foo", nargs=1)
@click.argument("bar", nargs=-1)
def foo(foo, bar):
    """
    this is just for foo!
    """
    clerr("foo goes to:", "stderr")
    clerr(foo)

    clout("bar goes to:", "stdout")
    clout(bar)


def main():
    def _add_subcommands() -> typeNoReturn:
        for path in SUBCOMMAND_PATHS:
            modname = re.sub(f"/", ".", str(path)).rpartition(".py")[0] # e.g. "csvviz.cmds.bar" or "csvviz.cmds.info"
            klassname = modname.split('.')[-1].capitalize() + 'kit' # e.g. "Barkit" or "Infokit"
            mod = importlib.import_module(modname)
            klass = getattr(mod, klassname)

            if getattr(klass, 'get_command', None): # TODO: remove after testing
                apex.add_command(klass.get_command())

    _add_subcommands()
    apex()


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
