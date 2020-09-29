#!/usr/bin/env python3
from IPython import embed as IBREAKPOINT

import altair as alt
from altair.utils import parse_shorthand as pshort
import altair_viewer as altview
import click
import pandas as pd
from vega_datasets import data as vdata


def av(chart):
    print(chart.to_json())
    altview.show(chart)

def main():
    la_input_path = vdata.la_riots.filepath
    ladf = pd.read_csv(la_input_path)

    tkdf = pd.read_csv('examples/tings.csv')

    tkart = alt.Chart(tkdf).mark_bar().encode(
        x=alt.X('name'),
        y='amount',
        fill=alt.Color('amount', scale=alt.Scale(range=['green', 'yellow', 'red'] )))



    ## try cars stuff
    cdf = vdata.cars()
    c = alt.Chart(cdf).mark_bar()
    ci = c.encode(
        x=alt.X('Horsepower:Q', bin=True),
        y='count()',
    )



    print('Breakpoint time!')
    IBREAKPOINT()


if __name__ == '__main__':
    main()




def foo():

    srcpath = 'examples/real/congress.csv'
    cdf = pd.read_csv(srcpath)
    ci = alt.Chart(cdf).mark_bar()
    cj = ci.encode(
            x=alt.X('gender'),
            y='count()',
        )

    ck = ci.encode(
            x=alt.X('year(birthday):T', bin=True),
            y='count()',
        )
    av(ck)
