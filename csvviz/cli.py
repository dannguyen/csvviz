import click
import importlib
import json
from pathlib import Path
import re
import sys
from typing import NoReturn as NoReturnType

from csvviz import __version__
from csvviz.utils.sysio import clout, clerr
from csvviz.info import command as infocommand


SUBCOMMAND_PATHS = [
    p for p in Path("csvviz/vizzes").glob("*.py") if p.name != "info.py"
]


def _print_version(ctx=None, param=None, value=None) -> NoReturnType:
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
    """csvviz (cvz) is a command-line tool for producing visualizations using the Vega-lite spec"""
    pass

# manual hack for now
from csvviz.vizzes import area, bar, heatmap, hist, line, scatter, stream

def main():
    ## this doesn't work for release, for some reason
    # def _add_viz_subcommands() -> NoReturnType:
    #     for path in SUBCOMMAND_PATHS:
    #         modname = re.sub(f"/", ".", str(path)).rpartition(".py")[
    #             0
    #         ]  # e.g. "csvviz.viz.bar" or "csvviz.viz.info"
    #         klassname = modname.split(".")[-1].capitalize() + "kit"
    #         klass = getattr(importlib.import_module(modname), klassname)

    #         if getattr(klass, "register_command", None):  # TODO: remove after testing
    #             cli.add_command(klass.register_command())

    # _add_viz_subcommands()
    # manually add info command
    cli.add_command(infocommand)
    cli.add_command(area.Areakit.register_command())
    cli.add_command(bar.Barkit.register_command())
    cli.add_command(heatmap.Heatmapkit.register_command())
    cli.add_command(hist.Histkit.register_command())
    cli.add_command(line.Linekit.register_command())
    cli.add_command(scatter.Scatterkit.register_command())
    cli.add_command(stream.Streamkit.register_command())
    cli()

if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
