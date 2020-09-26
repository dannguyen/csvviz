# TODOS

## JUST DONE 

- [x] fixed how `--sort` and `--hide-legend` works
    - [x] need to rethink how legend default title works; can't depend on encoding.fill.field, as it may sometimes be encoding.fill.aggregate or whatever
        - [ ] need to test

## ON DECK

- axis-range
    - [X] `--xlim/--ylim`: https://altair-viz.github.io/user_guide/customization.html?highlight=axis#adjusting-axis-limits



- hist.py
    - https://altair-viz.github.io/gallery/simple_histogram.html
    - https://altair-viz.github.io/gallery/histogram_responsive.html
    - [x] skeleton
    - [ ] test
    - figure out how to specify bin size and intervals and counts



- kill Datakit, move dataframe stuff into Vizkit
    - what's the point of specific row/column selection? End-user isn't using csvviz to do that
    - Vizkit.data == Vizkit.df


- Figure out a way to re-use/simplify command boilerplate, as simple as it already is

- `scatter`:
    - [X] legend for `size` appears and do we want that?
    - [X] copy `bar` template with half-finished Vizkit
    - [X] need to actually subclass Vizkit, to do custom implementation of set_channels

- csvviz.info:
    - alt.core.TIMEUNITS
    - WINDOW_AGGREGATES
    - AGGREGATES
    - INV_TYPECODE_MAP

- chart-wide attributes:
    - width
    - height (combine into a dimensions flag)

- tooltips: https://altair-viz.github.io/gallery/scatter_tooltips.html

- Handling datetimes: https://altair-viz.github.io/user_guide/times_and_dates.html
    ```py
    # https://altair-viz.github.io/user_guide/times_and_dates.html#altair-and-pandas-datetimes
    # using temporal unit
    alt.Chart(temps).mark_line().encode(
        x='date:T',
        y='temp:Q'
    )

    # using ordinal time units

    alt.Chart(temps).mark_rect().encode(
        alt.X('hoursminutes(date):O', title='hour of day'),
        alt.Y('monthdate(date):O', title='date'),
        alt.Color('temp:Q', title='temperature (F)')
    )
    ```


- opacity option, for use in scatterplots



## Not on deck

- geo: mark_geoshape: https://altair-viz.github.io/gallery/choropleth.html
    - let user specify geoshape file, separate from input_file. Or provide keyword choices, e.g. 'us:states', 'world:countries'
    - should maps have more than one kind of markup? https://altair-viz.github.io/gallery/airport_connections.html
    - allow user to specify background layer: https://altair-viz.github.io/gallery/london_tube.html
        - `--bg-stroke=2,color --bg-fill=color`
    - but how to do labels??

- Adopt Altair mini-syntax: seems like using Altair's mini-syntax is the way to go?
    - [X] maybe kill Datakit.resolve_column for validation, and just pass things straight into Altair and propogate its 'not a column errors'?
    - [?] what are the scenarios when passing invalid column names into alt.X, alt.Y, alt.Fill, etc?

    - https://altair-viz.github.io/user_guide/encoding.html#encoding-shorthands
    - write a quick helpme for csvviz usecases
        - `Vizkit.column_to_channel('sum(amount)')`


- [ ] static data point labels: 
    - https://altair-viz.github.io/gallery/scatter_with_labels.html
    - https://altair-viz.github.io/gallery/bar_chart_with_labels.html


- [ ] `-g/--group` for grouped bar charts



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



- JSON output
    - should include a 'csvviz' object with meta info, including:
        - csvviz version
        - input_path filename if applicable
        - full command as a string
        - `reify` the Python Altair code, so that users can eval/copy-paste it for further 


- `--sort`: for sorting marks by the x-axis:
    - https://vega.github.io/vega-lite/docs/sort.html#sort-field
    - https://altair-viz.github.io/user_guide/encoding.html?highlight=sort%20marks
    - [x] basic implementation
    - [x] make sure horizontal bar sorts as expected
    - [x] test, including robust error handling when invalid column name is passed in
    - [ ? ] naming/syntax
        - should it have a better name, like `--order`, or something?
            - can't use `-o/--order` because `-o` should be for `--output`
            - ggplot2 has a `reorder()` function that is applied to a given channel: https://www.r-graph-gallery.com/267-reorder-a-variable-in-ggplot2.html
        - is `--sort-x` unnecessarily specific, e.g. user will only want to sort by x/independent variable, except in situation of `fill` and stacked charts...
            - or should it have a mini-syntax, e.g. `--sort 'x:-amount'`

- Vizkit class
    - [x] init
    - [x] build_chart
    - [x] refactor bar.py using Vizkit class 
    - [NA] _init_command and @self.command
        - no need for now to wrap click.Command into Vizkit
    - [NA] learn metaprogramming to delegate datakit->vizkit stuff

- [NA] how to independently invoke and manage Click commands
    - https://stackoverflow.com/questions/40091347/call-another-click-command-from-a-click-command



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




## All done

- [X] Look in Altair source to find when column name/shorthand is validated
    - fix: found altair.utils.parse_shorthand(meta:dict, data:pd.DataFrame), and am using it in Vizkit


- csvviz.cmds.bar: Work on bar subcommand, generalize from there
    - `csvviz bars -x name -y things examples/tings.csv` works!
    - [x] read csv from command-line with pandas
    

    - `-x` and `-y`: 
        - [X] should be optional and default to 0,1 columns respectively
        - [X] should accept integer indexes, not just column names as strings
        - [x] `-f/--fill` to specify variable for stacks/groups

    - `-s/--sort` allow
    - `--colors` allow user to set up a color wheel to pick from 
        - OR let user pass in a list of colors, which will be assigned to corresponding -y series
https://altair-viz.github.io/user_guide/encoding.html#ordering-marks


- `bar`
    - [X] kill the ability to refer to columns by index
    - [X] refactored internal chart building methods, to make it easier to make VizCommand
- Top-level chart config https://altair-viz.github.io/user_guide/configuration.html
    - [X] --title for chart title
        - [?] do we need a mini-syntax for configuring title alignment, size, and font?
        - [x] tested
    - [X] --no-legend
        - [?] do we need a mini-syntax for configuring legend stuff, e.g. title and alignment?
        - [x] tested

- [X] Create `info` subcommand
- `--colors`: https://altair-viz.github.io/user_guide/customization.html?highlight=colors#color-schemes
    - [X] if `--colors` and `--colors-scheme` both exist, then use --colors first, and fall back to `--colors-scheme`
    - [x] create a constant var for schemes, or just default to whatever vega accepts?: https://vega.github.io/vega/docs/schemes/
        - Just fallback to Altair's handling, which is to use 'default', but also to not specify it in the metadata.

- [X] '--json' output option
    - [X] write tests for it
