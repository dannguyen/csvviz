#!/usr/bin/env python3
"""
just a scratchpad for quickly interactively testing things out

testing out top-level config
"""

from IPython import embed as IBREAKPOINT

import altair as alt
from altair.utils import parse_shorthand as pshort
import altair_viewer as altview
import click
import numpy as np
import pandas as pd
from vega_datasets import data as vdata


def av(chart):
    print(chart.to_json())
    altview.show(chart)

def main():
    df = pd.read_csv('examples/fruits.csv')

    alt.themes.enable('none')
    color_range = {
        "category": ["red", "green"],
    }

    cline = alt.Chart(df).mark_bar().encode(x='product', y="revenue", fill="region")
    qline = alt.Chart(df).mark_bar().encode(x='product', y="revenue", fill="revenue:Q")

    print('Breakpoint time!')
    IBREAKPOINT()


if __name__ == '__main__':
    main()






# #!/usr/bin/env python3
# """
# just a scratchpad for quickly interactively testing things out
# """

# from IPython import embed as IBREAKPOINT

# import altair as alt
# from altair.utils import parse_shorthand as pshort
# import altair_viewer as altview
# import click
# import numpy as np
# import pandas as pd
# from vega_datasets import data as vdata


# def av(chart):
#     print(chart.to_json())
#     altview.show(chart)

# def main():
#     la_input_path = vdata.la_riots.filepath
#     ladf = pd.read_csv(la_input_path)

#     tkdf = pd.read_csv('examples/tings.csv')

#     tkart = alt.Chart(tkdf).mark_bar().encode(
#         x=alt.X('name'),
#         y='amount',
#         fill=alt.Color('amount', scale=alt.Scale(range=['green', 'yellow', 'red'] )))



#     ## try cars stuff
#     cdf = vdata.cars()
#     c = alt.Chart(cdf).mark_bar()
#     ci = c.encode(
#         x=alt.X('Horsepower:Q', bin=True),
#         y='count()',
#     )


#     # heat map stuff
#     # this makes such a tiny chart!
#     hots = pd.read_csv('examples/hot.csv')
#     hc = alt.Chart(hots).mark_rect().encode(
#         x='state',
#         y='item',
#         color='sold',
#     )



#     print('Breakpoint time!')
#     IBREAKPOINT()


# if __name__ == '__main__':
#     main()




# def foo():

#     srcpath = 'examples/real/congress.csv'
#     cdf = pd.read_csv(srcpath)
#     ci = alt.Chart(cdf).mark_bar()
#     cj = ci.encode(
#             x=alt.X('gender'),
#             y='count()',
#         )

#     ck = ci.encode(
#             x=alt.X('year(birthday):T', bin=True),
#             y='count()',
#         )
#     av(ck)
