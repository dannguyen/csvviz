#!/usr/bin/env python

"""Tests for `csvviz` package."""

import pytest

from click.testing import CliRunner

from csvviz import csvviz
from csvviz import cli

import re

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

def test_apex_cli():
    """Just the overarching CLI interface"""
    runner = CliRunner()
    result = runner.invoke(cli.apex)
    assert result.exit_code == 0
    assert 'Welcome to csvviz' in result.output
    help_result = runner.invoke(cli.apex, ['--help'])
    assert help_result.exit_code == 0

    assert re.search(r'--help +Show this message and exit', help_result.output)
