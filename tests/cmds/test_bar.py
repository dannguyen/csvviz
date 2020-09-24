#!/usr/bin/env python

import pytest
from click.testing import CliRunner

import json as jsonlib
from pathlib import Path

from csvviz.cmds.bar import bar
from csvviz.exceptions import *
from csvviz.settings import *

OUTPUT_ARGS = ['--json', '--no-preview', 'examples/tings.csv',]


def test_bar_defaults():
    """
    MVP, where x is columns[0] and y is columns[1]

    just a catch all sanity test...
    Should resemble what's in tests/fixtures/bar-basic.json
    """
    result = CliRunner().invoke(bar, [*OUTPUT_ARGS])
    cdata = jsonlib.loads(result.output)

    assert cdata['mark'] == 'bar'

    datavals = list(cdata['datasets'].values())[0]
    assert datavals[0] == {'amount': 20, 'name': 'Alice'}
    assert datavals[-1] == {'amount': 42, 'name': 'Ellie'}

    assert cdata['encoding']['x'] == {'field': 'name', 'type': 'nominal'}
    assert cdata['encoding']['y'] == {'field': 'amount', 'type': 'quantitative'}




def test_bar_x_y():
    """
    setting x and y
    """
    result = CliRunner().invoke(bar, ['-x', 'amount', '-y', 'amount', *OUTPUT_ARGS])
    cdata = jsonlib.loads(result.output)

    assert cdata['encoding']['x']['field'] == 'amount'
    assert cdata['encoding']['x']['type'] == 'quantitative'
    # 'x' is NOT assumed to be nominal by default
    assert cdata['encoding']['y']['field'] == 'amount'
    assert cdata['encoding']['y']['type'] == 'quantitative'

def test_bar_horizontal():
    """
    Making a horizontal bar chart in Altair means flipping how x and y are specified.

    csvviz does that for the user, i.e. user shouldn't expect x to be 'name', despite the command line setting
    """
    result = CliRunner().invoke(bar, ['-x', 'name', '-y', 'amount', '-H', *OUTPUT_ARGS])
    cdata = jsonlib.loads(result.output)

    assert cdata['encoding']['x']['field'] == 'amount'
    assert cdata['encoding']['y']['type'] == 'nominal'

def test_bar_fill():
    """
    fill can be varied by the same column as x
    """
    result = CliRunner().invoke(bar, ['-f', 'name', *OUTPUT_ARGS])
    cdata = jsonlib.loads(result.output)

    fill = cdata['encoding']['fill']
    assert fill['field'] == 'name'
    assert fill['type'] == 'nominal'

