import pytest
from click.testing import CliRunner

import click
import json
from pathlib import Path

from csvviz.exceptions import *
from csvviz.settings import *

# for now, the bar chart seems like a good default viz
from csvviz.vizzes.bar import Barkit

viz = Barkit.register_command()

OUTPUT_ARGS = ["--json", "--no-preview", "examples/tings.csv"]


def test_defaults():
    result = CliRunner().invoke(viz, [*OUTPUT_ARGS])
    assert result.exit_code is 0

    # no usermeta, i.e. default theme is specified
    cdata = json.loads(result.output)

    # clip is always True, whether xlim/ylim is set
    assert cdata["mark"]["clip"] is True


##############################################################################################################
# fill color
##############################################################################################################


def test_basic_color_list():
    """
    -c/--color-list
    """
    colors = "red,deeppink,#999 "
    x = CliRunner().invoke(viz, ["-c", "name", "-C", colors, *OUTPUT_ARGS])
    assert x.exit_code == 0

    jdata = json.loads(x.output)
    scale = jdata["encoding"]["fill"]["scale"]
    assert scale["range"] == ["red", "deeppink", "#999"]

    # any time -C/--color-list is specified, 'scheme' is popped out
    assert "scheme" not in scale


def test_basic_color_scheme():
    """
    -C/--color-scheme
    """
    x = CliRunner().invoke(viz, ["-c", "name", "--CS", "dark2", *OUTPUT_ARGS])
    jdata = json.loads(x.output)

    scale = jdata["encoding"]["fill"]["scale"]
    assert scale["scheme"] == "dark2"


@pytest.mark.curious(
    reason="""
    This may not be a good idea, if the user specifies continuous fill variable, which looks like ****
     when the scale is categorical like category10.

    However, for now, I can't see a reason the user would knowingly specify a non-categorical variable for
    a bar chart fill variable. Thus, this is an opinionated default..."""
)
def test_fill_default_quant_color_scheme():
    """
    by default, a viz chart with fill should have scheme=DEFAULT_COLOR_SCHEMES
    """
    result = CliRunner().invoke(viz, ["--colorvar", "amount", *OUTPUT_ARGS])
    cdata = json.loads(result.output)

    fill = cdata["encoding"]["fill"]
    assert fill["type"] == "quantitative"
    assert fill["scale"]["scheme"] == DEFAULT_COLOR_SCHEMES["ramp"]


@pytest.mark.skip(reason="Not worrying about extra legend functionality until later")
def test_legend_settings():
    """when there is a fill, there is a legend"""
    result = CliRunner().invoke(
        viz,
        ["-c", "name", "--legend", "title=Legend of Titles;orient=left", *OUTPUT_ARGS],
    )
    cdata = json.loads(result.output)
    legend = cdata["encoding"]["fill"]["legend"]

    assert legend["Legend of Titles"] == "name"
    assert legend["orient"] == "left"


##############################################################################################################
# --xlim,--ylim
##############################################################################################################
def test_lims():
    result = CliRunner().invoke(
        viz, ["--xlim", "-10,30", "--ylim", "-40,50", *OUTPUT_ARGS]
    )
    cdata = json.loads(result.output)
    cdata["mark"]["clip"] is True  # this is always true, whether xlim/ylim are set
    cdata["encoding"]["x"]["scale"]["domain"] == [-10, 30]
    cdata["encoding"]["y"]["scale"]["domain"] == [-40, 50]


##############################################################################################################
# specify var titles
##############################################################################################################
def test_var_title_specified():
    result = CliRunner().invoke(
        viz,
        ["-x", "name|Foo", "-y", "amount|Bar", "-c", "sum(amount)|Woah", *OUTPUT_ARGS],
    )
    cdata = json.loads(result.output)
    assert cdata["encoding"]["x"]["field"] == "name"
    assert cdata["encoding"]["x"]["title"] == "Foo"
    assert cdata["encoding"]["y"]["field"] == "amount"
    assert cdata["encoding"]["y"]["title"] == "Bar"
    assert cdata["encoding"]["fill"]["aggregate"] == "sum"
    assert cdata["encoding"]["fill"]["field"] == "amount"
    assert cdata["encoding"]["fill"]["title"] == "Woah"


##############################################################################################################
# warnings
##############################################################################################################
@pytest.mark.curious(reason="This test is repeated somewhere else, oh well")
def test_warn_if_colors_scheme_specified_but_no_colorvar():
    r = CliRunner().invoke(viz, ["--color-scheme", "dark2", *OUTPUT_ARGS])
    assert r.exit_code == 0
    assert (
        "Warning: --colorvar was not specified, so --color-scheme is ignored"
        in r.output
    )


def test_warn_if_invalid_colorscheme_used():
    r = CliRunner().invoke(
        viz, ["--colorvar", "name", "--color-scheme", "booyah", *OUTPUT_ARGS]
    )
    assert r.exit_code == 0
    assert "Warning: Using default color scheme" in r.output
    assert (
        "--color-scheme argument 'booyah' does not seem to be a valid color scheme"
        in r.output
    )


def test_warning_for_missing_colorvar_supercedes_invalid_color_scheme():
    r = CliRunner().invoke(viz, ["--color-scheme", "booyah", *OUTPUT_ARGS])
    assert r.exit_code == 0
    assert "Warning: --colorvar was not specified" in r.output
    assert "Warning: Using default color scheme" not in r.output


##############################################################################################################
# errors
##############################################################################################################


def test_error_when_both_color_list_and_color_scheme_are_set():
    args = [
        "-c",
        "name",
        "-C",
        "red,blue",
        "--CS",
        "tableau10",
    ]

    c = CliRunner().invoke(viz, [*args, *OUTPUT_ARGS])
    assert c.exit_code == 1
    assert (
        "--color-list and --color-scheme cannot both be specified." in c.output.strip()
    )


def test_error_if_user_specifies_columns_as_integers():
    # with pytest.raises(click.UsageError) as err:
    result = CliRunner().invoke(viz, ["-y", "0", *OUTPUT_ARGS])
    assert result.exit_code == 1
    assert (
        "InvalidDataReference: '0' is either an invalid column name, or invalid Altair shorthand"
        in result.output.strip()
    )


@pytest.mark.skip("TKD deprecated --themes for now")
def test_error_if_invalid_theme_specified():
    result = CliRunner().invoke(viz, ["--theme", "NotGood", *OUTPUT_ARGS])
    assert result.exit_code == 2
    assert (
        """Error: Invalid value for '--theme': invalid choice: NotGood"""
        in result.output
    )


@pytest.mark.skip(reason="TODO")
def test_error_if_invalid_color_scheme_specified():
    with pytest.raises(InvalidColorScheme) as err:
        CliRunner().invoke(viz, ["--color-scheme", "not a color scheme", *OUTPUT_ARGS])

    assert (
        f"ERROR: 'dark2' is not a valid color scheme; run `csvviz info colorschemes` to get list of color schemes"
        in str(err.value)
    )


@pytest.mark.curious(
    reason="Maybe it is better to silently fail, then to write a color string validator?"
)
@pytest.mark.skip(reason="TODO; also, pytest.raises doesn't really work here")
def test_error_if_invalid_color_name_value_specified():
    with pytest.raises(Exception) as err:
        CliRunner().invoke(
            viz, ["--color-list", "red,blue,000,#999,asdf", *OUTPUT_ARGS]
        )

    assert f"ERROR: 'asdf'" in str(err.value)
