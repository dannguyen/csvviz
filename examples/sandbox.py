#!/usr/bin/env python3
from IPython import embed as IBREAKPOINT

import altair as alt
import altair_viewer as altview
import click
import pandas as pd
from vega_datasets import data as vdata

from csvviz.kits.datakit import Datakit

def av(chart):
     altview.show(chart.interactive())

def main():
    la_input_path = vdata.la_riots.filepath
    ladf = pd.read_csv(la_input_path)
    ladk = Datakit(la_input_path)

    tk = Datakit('examples/tings.csv')
    fk = Datakit('examples/fruits.csv')


    ci = alt.Chart(tk.df).mark_bar()
    chart = ci.encode(
        x=alt.X('name'),
        y='amount',
        fill=alt.Color('amount', scale=alt.Scale(range=['green', 'yellow', 'red'] )))

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
