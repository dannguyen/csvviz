#!/usr/bin/env python3
from IPython import embed as IBREAKPOINT
import pandas as pd
from vega_datasets import data as vegadata

from csvviz.csvviz import Datakit

def main():
    input_path = vegadata.la_riots.filepath
    df = pd.read_csv(input_path)

    dk = Datakit(input_path)

    print('Breakpoint time!')
    IBREAKPOINT()


if __name__ == '__main__':
    main()



