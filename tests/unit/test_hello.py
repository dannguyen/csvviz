#!/usr/bin/env python

"""this hsould be in unit/clicky but whatever"""

import pytest
import re
from click.testing import CliRunner
from csvviz import __version__
from csvviz.cli import cli


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')
    pass


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string
    pass


def test_top_cli():
    """Just the overall CLI interface"""
    result = CliRunner().invoke(cli)
    assert result.exit_code == 0
    assert "csvviz (cvz) is a command-line tool" in result.output

    # test help invocation
    helpr = CliRunner().invoke(cli, ["--help"])
    assert helpr.exit_code == 0

    assert re.search(r"--help +Show this message and exit", helpr.output)


def test_top_version():
    """--version flag"""
    result = CliRunner().invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert result.output.strip() == __version__
