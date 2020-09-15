import importlib
import json as jsonlib
from pathlib import Path
import re
import sys
from typing import Any as typeAny, Mapping as typeMapping, NoReturn as typeNoReturn
from typing import Dict as typeDict, List as typeList, Tuple as typeTuple, Union as typeUnion
from typing import IO as typeIO

import click
from csvviz.cli.helpers import clout, clerr

@click.group()
def top(args=None):
    """Console script for csvviz."""
    pass

@top.command()
@click.argument('foo', nargs=1)
@click.argument('bar', nargs=-1)
def foo(foo, bar):
    """
    this is just for foo!
    """
    clerr("foo goes to:", "stderr")
    clerr(foo)

    clout("bar goes to:", "stdout")
    clout(bar)


def main():
    def _add_subcommands(maincommand) -> typeNoReturn:
        for path in Path('csvviz/cli/charters').glob('*.py'):
            pmod_name = re.sub(f'/', '.',  str(path)).rpartition('.py')[0]
            pmod = importlib.import_module(pmod_name)
            pcommand = pmod.__command__

            maincommand.add_command(pcommand)
    _add_subcommands(top)
    top()


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
