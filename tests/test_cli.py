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


def test_bar_simple_writes_png(tmp_path):
    runner = CliRunner()
    out = tmp_path / "out.png"
    result = runner.invoke(
        cli,
        ["bar", "--no-show", "-o", str(out), str(FIXTURES / "tings.csv")],
    )
    assert result.exit_code == 0, result.output
    assert out.exists() and out.stat().st_size > 0


def test_bar_invalid_column_exits_1(tmp_path):
    runner = CliRunner()
    out = tmp_path / "out.png"
    result = runner.invoke(
        cli,
        ["bar", "-x", "nope", "--no-show", "-o", str(out), str(FIXTURES / "tings.csv")],
    )
    assert result.exit_code == 1
    assert "nope" in result.output


def test_line_multi_series_writes_png(tmp_path):
    runner = CliRunner()
    out = tmp_path / "out.png"
    result = runner.invoke(
        cli,
        [
            "line",
            "-x",
            "date",
            "-y",
            "price",
            "-c",
            "company",
            "--no-show",
            "-o",
            str(out),
            str(FIXTURES / "stocks.csv"),
        ],
    )
    assert result.exit_code == 0, result.output
    assert out.exists()


def test_scatter_writes_png(tmp_path):
    p = tmp_path / "sc.csv"
    p.write_text("x,y\n1,2\n3,4\n5,6\n")
    out = tmp_path / "out.png"
    runner = CliRunner()
    result = runner.invoke(cli, ["scatter", "--no-show", "-o", str(out), str(p)])
    assert result.exit_code == 0, result.output
    assert out.exists()


def test_hist_writes_png(tmp_path):
    runner = CliRunner()
    out = tmp_path / "out.png"
    result = runner.invoke(
        cli,
        ["hist", "-x", "amount", "--no-show", "-o", str(out), str(FIXTURES / "tings.csv")],
    )
    assert result.exit_code == 0, result.output
    assert out.exists()


def test_area_writes_png(tmp_path):
    runner = CliRunner()
    out = tmp_path / "out.png"
    result = runner.invoke(
        cli,
        [
            "area",
            "-x",
            "date",
            "-y",
            "price",
            "--no-show",
            "-o",
            str(out),
            str(FIXTURES / "stocks.csv"),
        ],
    )
    assert result.exit_code == 0, result.output
    assert out.exists()


def test_heatmap_writes_png(tmp_path):
    runner = CliRunner()
    out = tmp_path / "out.png"
    result = runner.invoke(cli, ["heatmap", "--no-show", "-o", str(out), str(FIXTURES / "hot.csv")])
    assert result.exit_code == 0, result.output
    assert out.exists()


def test_conflict_normalized_without_colorvar_exits_1(tmp_path):
    runner = CliRunner()
    out = tmp_path / "out.png"
    result = runner.invoke(
        cli,
        ["bar", "--normalized", "--no-show", "-o", str(out), str(FIXTURES / "tings.csv")],
    )
    assert result.exit_code == 1
    assert "colorvar" in result.output or "-c" in result.output


def test_xlim_bad_value_gives_usage_error(tmp_path):
    runner = CliRunner()
    out = tmp_path / "out.png"
    result = runner.invoke(
        cli,
        ["bar", "--xlim", "a,b", "--no-show", "-o", str(out), str(FIXTURES / "tings.csv")],
    )
    # Click usage errors exit with code 2 (not 1, not "unexpected failure")
    assert result.exit_code == 2
    assert "unexpected failure" not in result.output
