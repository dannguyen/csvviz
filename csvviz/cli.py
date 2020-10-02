import importlib
import json
from pathlib import Path
import re
import sys
from typing import NoReturn as typeNoReturn
import click

from csvviz import __version__
from csvviz.utils.sysio import clout, clerr
from csvviz.cmds.info import command as infocommand


SUBCOMMAND_PATHS = [p for p in Path("csvviz/cmds/").glob("*.py") if p.name != "info.py"]


def _print_version(ctx=None, param=None, value=None) -> typeNoReturn:
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


@click.group()
@click.option(
    "--version",
    callback=_print_version,
    is_eager=True,
    is_flag=True,
    help="Print the version of csvviz",
)
def cli(**kwargs):
    """
    Welcome to csvviz (cvz), a command-line tool for producing visualizations using the Vega-lite spec
    """

    pass


def main():
    def _add_viz_subcommands() -> typeNoReturn:
        for path in SUBCOMMAND_PATHS:
            modname = re.sub(f"/", ".", str(path)).rpartition(".py")[
                0
            ]  # e.g. "csvviz.cmds.bar" or "csvviz.cmds.info"
            klassname = modname.split(".")[-1].capitalize() + "kit"
            mod = importlib.import_module(modname)
            klass = getattr(mod, klassname)

            if getattr(klass, "register_command", None):  # TODO: remove after testing
                cli.add_command(klass.register_command())

    _add_viz_subcommands()
    # manually add info command
    cli.add_command(infocommand)
    cli()


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
