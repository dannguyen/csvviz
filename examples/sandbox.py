#!/usr/bin/env python3
from IPython import embed as IBREAKPOINT

import altair as alt
import altair_viewer as altview

import pandas as pd
from vega_datasets import data as vdata

from csvviz.utils.datakit import Datakit

def main():
    input_path = vegadata.la_riots.filepath
    df = pd.read_csv(input_path)
    dk = Datakit(input_path)


    fdk = Datakit('examples/fruits.csv')



    print('Breakpoint time!')
    IBREAKPOINT()


if __name__ == '__main__':
    main()



