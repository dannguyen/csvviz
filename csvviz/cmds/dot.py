import click
from csvviz.cli_utils import clout, clerr


@click.command()
def dot(**kwargs):
    """just a stub"""
    clout("Nothing to see here")


__command__ = dot
