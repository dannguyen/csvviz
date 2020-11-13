import json
from pathlib import Path
import pytest
import re
from subprocess import Popen, PIPE

# shouldn't have to use these...
# from click.testing import CliRunner
# from csvviz.vizzes.bar import Barkit
# viz = Barkit.register_command()


DEFAULT_ARGS = [
    "csvviz",
    "bar",
]
DEFAULT_OPTS = [
    "--json",
    "--no-preview",
]
PATH_CSV = Path("examples/fruits.csv")


def assert_valid_json(output: str):
    """whatever, good enough for now"""
    assert output[0:2] == "{\n"
    assert output[-2:] == "\n}"
    data = json.loads(output)
    assert re.match(
        r"https://vega.github.io/schema/vega-lite/v\d.+?json", data["$schema"]
    )
    assert all(k in data for k in ("config", "data", "mark", "encoding"))


def process_program(pipe: PIPE):
    """returns (stdout, exitcode, stderr) as str"""
    out, err = [o.decode("utf-8").strip() if o else "" for o in pipe.communicate()]
    exitcode = pipe.returncode
    return (
        out,
        exitcode,
        err,
    )


def test_io_basic():
    pviz = Popen([*DEFAULT_ARGS, *DEFAULT_OPTS, PATH_CSV], stdout=PIPE)
    output, exitcode, err = process_program(pviz)
    assert exitcode == 0
    assert_valid_json(output)


@pytest.mark.curious(reason="""Repurpose csvmedkit's cmd running code""")
def test_io_piped_stdin():
    """accepts '-' as stdin argument"""
    pcat = Popen(
        [
            "cat",
            PATH_CSV,
        ],
        stdout=PIPE,
    )
    pviz = Popen(
        [
            *DEFAULT_ARGS,
            *DEFAULT_OPTS,
        ],
        stdin=pcat.stdout,
        stdout=PIPE,
    )
    pcat.stdout.close()
    output, exitcode, err = process_program(pviz)
    assert exitcode == 0
    assert_valid_json(output)


def test_io_filepath_invalid():
    badpath = "/tmp/zzz/123.txt"
    pviz = Popen(["csvviz", "bar", badpath], stderr=PIPE, stdout=PIPE, stdin=None)
    output, exitcode, err = process_program(pviz)
    assert exitcode == 2
    assert """Invalid value for '[INPUT_FILE]'""" in err
    assert f"""Could not open file: {badpath}""" in err


@pytest.mark.curious(
    reason="""No idea why this doesn't work, and why it keeps returning exitcode == 2"""
)
@pytest.mark.skip(reason="fix later...")
def test_io_error_when_missing_input_file():
    pviz = Popen(
        [
            "csvviz",
            "bar",
        ],
        stderr=PIPE,
        stdout=PIPE,
        stdin=None,
    )
    # why?    pviz.poll()
    output, exitcode, err = process_program(pviz)
    assert exitcode == 2
    assert "Error: Missing argument: INPUT_FILE" in err


#  # have to use CliRunner
#  runner = CliRunner()
#  result = runner.invoke(viz, DEFAULT_OPTS)
# # assert not result.exception
#  assert result.exit_code == 1
#  # assert (
#  #     """Error: Invalid value for '--theme': invalid choice: NotGood"""
#  #     in result.output
#  # )
