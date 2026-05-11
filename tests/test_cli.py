from pathlib import Path

from click.testing import CliRunner

from csvviz import __version__
from csvviz.cli import cli

FIXTURES = Path(__file__).parent / "fixtures"


def test_version_flag():
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_help_lists_subcommands():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    for cmd in ("bar", "line", "scatter", "hist", "area", "heatmap"):
        assert cmd in result.output
