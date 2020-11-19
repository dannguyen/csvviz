import json

import altair as alt
import click
import pandas as pd
from csvviz import __version__ as csvviz_version
from csvviz.utils.sysio import clout, clerr

# from typing import Mapping as MappingType, NoReturn as NoReturnType
# from typing import List as ListType, Tuple as TupleType, Union as UnionType
# from typing import IO as IOType


INFO_OPTIONS = {
    "aggregates": "list vega-lite aggregate functions available for Altair shorthand syntax, e.g. `-y 'sum(amount)' ",
    "colors": "list the HTML-valid color names, e.g. 'firebrick', 'hotpink'",
    "colorschemes": "list the vega supported color scales, e.g. 'tableau10', 'purples'",
    # TKD:  "themes": "list the Altair themes, e.g. 'latimes', 'ggplot2', 'fivethirtyeight'",
    "timeunits": "list the timeunits available to Vega and available Altair shorthand syntax, e.g. `-y 'year(birthday)' `",
    "typecodes": "list datatypes and their shorthand syntax, e.g. `-x 'birthday:O'`",
    "versions": "list the versions of csvviz and main dependencies",
}


def load_schema():
    return alt.vegalite.core.load_schema()


@click.command(
    name="info",
    epilog="Topics:\n" + "\n".join([f"\n  {k}: {v}" for k, v in INFO_OPTIONS.items()]),
)
@click.argument(
    "infotype", type=click.Choice(INFO_OPTIONS.keys(), case_sensitive=False)
)
@click.option(
    "to_json",
    "--json/--no-json",
    "-j /",
    default=False,
    help="Output to stdout the Vega JSON representation",
)
def command(infotype, **kwargs):
    """
    Get more information about options and features, including lists of supported values.

    Usage:

        csvinfo [TOPIC]
    """

    schema = load_schema()

    ## from alt.Core
    if infotype == "aggregates":
        values = alt.utils.core.AGGREGATES
    elif infotype == "timeunits":
        values = alt.utils.core.TIMEUNITS
    elif infotype == "typecodes":
        values = alt.utils.core.INV_TYPECODE_MAP

    ## from the schema
    elif infotype == "colors":
        values = sorted(schema["definitions"]["ColorName"]["enum"])

    elif infotype == "colorschemes":
        cats = [
            s["$ref"].split("/")[-1]
            for s in schema["definitions"]["ColorScheme"]["anyOf"]
        ]
        values = tuple(
            (c, val) for c in sorted(cats) for val in schema["definitions"][c]["enum"]
        )

    # TKD
    # elif infotype == "themes":
    #     values = sorted(AVAILABLE_THEMES)  # TODO refactor

    elif infotype == "versions":
        # this should be a refactored constant
        values = {
            "csvviz": csvviz_version,
            "altair": alt.__version__,
            "pandas": pd.__version__,
            "vegalite-schema": alt.vegalite.SCHEMA_VERSION,
            "vegalite-schema-url": alt.vegalite.SCHEMA_URL,
            "vega": alt.vegalite.VEGA_VERSION,
            "vega-embed": alt.vegalite.VEGAEMBED_VERSION,
        }
        # values = [f'{k}: {v}' for k, v in _versions.items()]

    if kwargs.get("to_json"):
        clout(json.dumps(values, indent=2))
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


"""

Color names:
https://altair-viz.github.io/user_guide/generated/core/altair.ColorName.html
"""
