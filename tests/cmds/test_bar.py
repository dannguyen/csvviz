#!/usr/bin/env python

import pytest
from click.testing import CliRunner

import json as jsonlib
from pathlib import Path

from csvviz import csvviz
from csvviz.cmds.bar import bar

OUTPUT_ARGS = ['--json', '--no-preview']


def test_bar_basic():
    """
    just a catch all sanity test...
    Should resemble what's in tests/fixtures/bar-basic.json
    """
    result = CliRunner().invoke(bar, ['examples/tings.csv'] + OUTPUT_ARGS)
    assert result.exit_code == 0

    cdata = jsonlib.loads(result.output)

    assert cdata['mark'] == 'bar'

    datavals = list(cdata['datasets'].values())[0]
    assert datavals[0] == {'amount': 20, 'name': 'Alice'}
    assert datavals[-1] == {'amount': 42, 'name': 'Ellie'}

    assert cdata['encoding']['x'] == {'field': 'name', 'type': 'nominal'}
    assert cdata['encoding']['y'] == {'field': 'amount', 'type': 'quantitative'}



def test_bar_basic_fill():
    """
    fill can be varied by the same column as x
    """
    result = CliRunner().invoke(bar, ['-f', 'name', 'examples/tings.csv'] + OUTPUT_ARGS)
    cdata = jsonlib.loads(result.output)

    assert cdata['encoding']['fill'] ==  {
      "field": "name",
      "type": "nominal"
    }
