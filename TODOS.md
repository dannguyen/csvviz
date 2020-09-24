# TODOS


## JUST DONE 

- [X] Create `info` subcommand
- `--colors`: https://altair-viz.github.io/user_guide/customization.html?highlight=colors#color-schemes
    - [X] if `--colors` and `--colors-scheme` both exist, then use --colors first, and fall back to `--colors-scheme`
    - [x] create a constant var for schemes, or just default to whatever vega accepts?: https://vega.github.io/vega/docs/schemes/
        - Just fallback to Altair's handling, which is to use 'default', but also to not specify it in the metadata.

- [X] '--json' output option
    - [X] write tests for it
    
## On deck

- Come up with syntax for labeling, e.g. chart title, x-title, y-title
- kill the ability to refer to columns by index


## Not on deck

- csvviz.cli.charters.bars.py: Work on bar subcommand, generalize from there
    - `csvviz bars -x name -y things examples/tings.csv` works!
    - [x] read csv from command-line with pandas
    

    - `-x` and `-y`: 
        - [X] should be optional and default to 0,1 respectively
        - [X] should accept integer indexes, not just column names as strings
        - [x] `-f/--fill` to specify variable for stacks/groups
        - [later] `-g/--group` to s
        - [ ] do we need a mini-syntax for column_name,data_type(ordinal, continuous, etc): https://altair-viz.github.io/user_guide/encoding.html#encoding-shorthands
            - Maybe use brackets to specify that a field should be Altair shorthand, e.g.
                `csvviz bar tings.csv -x name -y '@mean(amount):Q'  `

    - `-s/--sort` allow
    - `--colors` allow user to set up a color wheel to pick from 
        - OR let user pass in a list of colors, which will be assigned to corresponding -y series
https://altair-viz.github.io/user_guide/encoding.html#ordering-marks

- Encoding channel options
    - Which options should be parsed/allowed? https://altair-viz.github.io/user_guide/encoding.html#encoding-channel-options
    - Maybe just stick to what shorthand allows? https://altair-viz.github.io/user_guide/encoding.html#encoding-shorthands
        - aggregate
        - data type
        - 


- Overall design
    - subclass click.command
    - Datakit class
        - has common utils, like pandas stuff: read path/stdin, parsing options
        - write basic tests for current properties and methods
        - need custom errors for out of index issues?
- Housekeeping
    - Get some data files to store locally

- Future thinking
    - Do some charts/apps require multiple CSVs? Or should we expect data to always be wrangled to single CSV?
        - leaning towards yes to single table only
    - setup.extras for selenium, etc. to do PNG rendering
    - Should csvviz treat columns as 0-based or, like csvkit and xsv, 1-based?



## Stuff to read

- line charts
    - multiseries: https://altair-viz.github.io/gallery/multi_series_line.html
        - use `color=` to set series


### Alternate viz libs

- a close implementation of ggplot2: https://github.com/has2k1/plotnine


#### seaborn

- still extremely popular, and sits atop matplotlib: https://github.com/mwaskom/seaborn
    - https://seaborn.pydata.org/tutorial.html
    - great support for small-multiples: https://seaborn.pydata.org/tutorial/function_overview.html#combining-multiple-views-on-the-data


chart examples

- line chart: https://seaborn.pydata.org/examples/errorband_lineplots.html
- scatter: https://seaborn.pydata.org/examples/different_scatter_variables.html
- bar: https://seaborn.pydata.org/generated/seaborn.barplot.html
