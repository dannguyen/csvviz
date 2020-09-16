from functools import reduce
import json as jsonlib


import altair as alt
import click
import pandas as pd
from csvviz.csvviz import clout, clerr, __version__ as csvviz_version

# from typing import Mapping as typeMapping, NoReturn as typeNoReturn
# from typing import List as typeList, Tuple as typeTuple, Union as typeUnion
# from typing import IO as typeIO


INFO_OPTIONS = {
        'colors': "list the HTML-valid color names, e.g. 'firebrick', 'hotpink'",

        'colorschemes':"list the vega supported color scales, e.g. 'tableau10', 'purples'",

        'themes': "list the Altair themes, e.g. 'latimes', 'ggplot2', 'fivethirtyeight'",

        'versions':       "list the versions of csvviz and main dependencies",

}


def load_schema():
    return alt.vegalite.core.load_schema()


@click.command()
@click.argument('infotype', type=click.Choice(INFO_OPTIONS.keys(), case_sensitive=False))
@click.option('to_json', '--json/--no-json', '-j /', default=False, help='Output to stdout the Vega JSON representation')
def info(infotype, **kwargs):
    """
    Get more information about options and features, including lists of supported values:

        'colors': "list the HTML-valid color names, e.g. 'firebrick', 'hotpink'",

        'colorschemes':"list the vega supported color scales, e.g. 'tableau10', 'purples'",

        'themes': "list the Altair themes, e.g. 'latimes', 'ggplot2', 'fivethirtyeight'",

        'versions':       "list the versions of csvviz and main dependencies",

    """

    schema = load_schema()
    if infotype == 'colors':
        values = sorted(schema['definitions']['ColorName']['enum'])

    elif infotype == 'colorschemes':
        cats = [s['$ref'].split('/')[-1] for s in schema['definitions']['ColorScheme']['anyOf']]
        values = tuple((c, val) for c in sorted(cats) for val in schema['definitions'][c]['enum'])

    elif infotype == 'themes':
        values = sorted(alt.themes.names()) # TODO refactor

    elif infotype == 'versions':
        # this should be a refactored constant
        values = {
            'csvviz': csvviz_version,
            'altair': alt.__version__,
            'pandas': pd.__version__,
            'vegalite-schema': alt.vegalite.SCHEMA_VERSION,
            'vegalite-schema-url': alt.vegalite.SCHEMA_URL,
            'vega': alt.vegalite.VEGA_VERSION,
            'vega-embed': alt.vegalite.VEGAEMBED_VERSION,
        }
        # values = [f'{k}: {v}' for k, v in _versions.items()]


    if kwargs.get('to_json'):
        clout(jsonlib.dumps(values, indent=2))
    else:
        if isinstance(values, dict):
            max_key_length = max(len(k) for k in values.keys())
            for k, v in values.items():
                clout(f"{k.ljust(max_key_length)}\t{v}")
        elif isinstance(values, tuple):
            max_key_length = max(len(cat) for cat, val in values)
            for cat, val in values:
                clout(f"{val.ljust(max_key_length)}\t[{cat}]")
        else:
            for v in values:
                clout(v)


__command__ = info


"""

Color names:
https://altair-viz.github.io/user_guide/generated/core/altair.ColorName.html
"""
