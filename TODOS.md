# TODOS



## 0.4.0 – more fundamentals, more refactoring


- [x] normalized bar/area charts
- [X] Name channel vars, which sets axes and legend titles:
    - [X] extend mini-syntax: `-y 'amount|Named Amount'`
- [X] fix setup.py and requirements
    - [x] got tox working
    - [x] bump2version works?
- [x] alias csvviz to cvz
- [x] facet/grid: `-gs/--grid-sort`
- [x] subclass click.Command to have type/category attribute, e.g. to specify 'general/specific' options
    - [x] subclass helpformatter to print subsections of general/specific options, as well as categories of options 

- chart-wide properties: https://altair-viz.github.io/user_guide/configuration.html#config-view
    - chart-fill `-BGC/--background-color`
    - width/height; `-CW/-CH`
    - --no-grid; `--no-grid`
- axis properties
    - https://altair-viz.github.io/gallery/us_population_over_time_facet.html
    - y-axis number format `--yf/--y-format`
    - https://vega.github.io/vega-lite/docs/config.html#format
    - https://github.com/d3/d3-format#locale_format
    - subcommand `info number_formats`



## 0.5.0 – better bespoke visuals and labels


Check out R-guides:
- hist: https://www.r-graph-gallery.com/histogram.html
- density: https://www.r-graph-gallery.com/density-plot.html
- heatmap https://www.r-graph-gallery.com/heatmap.html


- make a density chart? 
    - https://www.r-graph-gallery.com/density-plot.html
    - https://altair-viz.github.io/user_guide/transform/density.html
- make stream chart? https://altair-viz.github.io/gallery/streamgraph.html
- heatmap? https://altair-viz.github.io/gallery/simple_heatmap.html
- 
- [ ] allow sorting by array of values: https://vega.github.io/vega-lite/docs/sort.html#sort-array


- More chartwide options
    - `-op/--opacity` mark opacity option, for use in scatterplots
    - bar width: https://altair-viz.github.io/user_guide/customization.html#adjusting-the-width-of-bar-marks


- custom visuals
    - conditional highlighting: 
        - https://altair-viz.github.io/gallery/bar_chart_with_highlighted_bar.html
        - bar chart negative values: https://altair-viz.github.io/gallery/bar_chart_with_negatives.html

- [ ] static data point labels: 
    - https://altair-viz.github.io/gallery/scatter_with_labels.html
    - https://altair-viz.github.io/gallery/bar_chart_with_labels.html
- [ ] tooltips
    - https://altair-viz.github.io/gallery/scatter_tooltips.html
    - by default, show all channel values
    - have `--no-tooltips` option

- better bin transforms
    - https://altair-viz.github.io/user_guide/transform/bin.html
    - use pandas.cut and qcut: https://pbpython.com/pandas-qcut-cut.html
    - allow manual definition of bin `steps` for fun: https://vega.github.io/vega-lite/docs/bin.html
    - limit use of bins to:
        - x-axis for all charts (except hist)
        - color/fill for choropleth and heatmaps
    

## 0.6.0 – better input/output

- read csv:
    - option to specify typecast for columns, e.g. prevent fips from being returned as integers

- output bundle to dir:
    - storing data files as JSON to a specific dir: https://altair-viz.github.io/user_guide/data_transformers.html#storing-json-data-in-a-separate-directory
    - https://github.com/altair-viz/altair_saver/issues/62
- output vega or vega-lite
    - https://altair-viz.github.io/user_guide/importing.html#importing-vega-vega-lite-versions
- output png
    - use altair_saver: https://github.com/altair-viz/altair_saver#usage
    - https://vega.github.io/vega-lite/usage/compile.html
    - https://stackoverflow.com/questions/42742991/how-setup-py-install-npm-module

- allow read from non CSV paths
    - [ ] make a tocsv/read subcommand?
    - [ ] url
        - Vega has it built into its spec, but maybe just use pandas.read_csv()? https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html
    - [ ] excel; infer from path https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_excel.html
    - [ ] json: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_json.html

- `csvviz view`: reads vega/vega-lite json
- `csvviz save`: reads vega/vega-lite json, produces bundle/output

## 0.7.0 – the geo edition

- `csvviz geo`:
    - datawrapper gives 3 choices: choropleth, symbol map, locator map: https://app.datawrapper.de/create/map
    - mark_geoshape: https://altair-viz.github.io/gallery/choropleth.html
    - arguments:
        - input_file is expected to be a geoshape file
        - `-s/--shape 'counties'` or `-f/--feature 'counties'`?
    - let user specify related data file and a join column, e.g. `--data unemployment.csv --lookup 'FIPS'`
    - should maps have more than one kind of markup? https://altair-viz.github.io/gallery/airport_connections.html
    - allow user to specify background layer: https://altair-viz.github.io/gallery/london_tube.html
        - `--bg-stroke=2,color --bg-fill=color`
    - but how to do labels??

- get state-by-state electoral map over the years

- csvviz inspect
    - show number of columns by rows
    - for every column, show: name, datatype, cardinality, most_common_val, number of nils, mean, median, min, max


## 0.8.0 – the utilities edition

- make csvviz_datasets package
    - congress
    - electoral_vote
    - stop-and-frisk
    - babynames

- make csvviz_geo package
    - sources:
        - https://github.com/topojson/us-atlas
        - https://www2.census.gov/geo/tiger/GENZ2017/shp/
    - naming_scheme:   
    - examples
        - world
            - countries
                - 2020
                - 1900
        - usa
            - counties
                - 2020
                - 2010
            - states
                - 2020
                - 2000
                - ny
                    - census_tracts
            - congressional_districts
                - 116
                - 115
                - 114
            - places


## 0.9 – the wrangler edition

- `cvz wrangle` for pre-processing data
    - https://pandas.pydata.org/Pandas_Cheat_Sheet.pdf
    - select:
        - https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html
        - https://pandas.pydata.org/docs/getting_started/intro_tutorials/03_subset_data.html#how-do-i-select-specific-columns-from-a-dataframe
    - sort: `sort_values('amount', ascending=False)`
    - grep: `filter` https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.filter.html
    - query/where: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.query.html
    - drop-na: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.dropna.html
    - fill-na: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.fillna.html
    - qcut
    - cut
    - join/merge
    - pivot
    - groupby: https://pandas.pydata.org/docs/getting_started/intro_tutorials/06_calculate_statistics.html#aggregating-statistics-grouped-by-category
        
## 0.9.5 - the documentation edition

- clean up command info/options text
- write Readthedocs


-----------------------------------------------------------------------------


## Not on deck

- csvviz.info:
    - alt.core.TIMEUNITS
    - WINDOW_AGGREGATES
    - AGGREGATES
    - INV_TYPECODE_MAP



- Housekeeping
    - Get some data files to store locally

- JSON output
    - should include a 'csvviz' object with meta info, including:
        - csvviz version
        - input_path filename if applicable
        - full command as a string
        - `reify` the Python Altair code, so that users can eval/copy-paste it for further 



-----------------------------------------------------------------------------



## Appendix 

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


-----------------------------------------------------------------------------


### All done

- [X] Look in Altair source to find when column name/shorthand is validated
    - fix: found altair.utils.parse_shorthand(meta:dict, data:pd.DataFrame), and am using it in Vizkit


- csvviz.viz.bar: Work on bar subcommand, generalize from there
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


- [x] Figure out a way to re-use/simplify command boilerplate, as simple as it already is


- axis-range
    - [X] `--xlim/--ylim`: https://altair-viz.github.io/user_guide/customization.html?highlight=axis#adjusting-axis-limits


- `scatter`:
    - [X] legend for `size` appears and do we want that?
    - [X] copy `bar` template with half-finished Vizkit
    - [X] need to actually subclass Vizkit, to do custom implementation of set_channels


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


- [X] kill Datakit
    - [x] removed reference/usage in Vizkit; Datakit is now unused except in tests
    - [?] move dataframe functions into Vizkit

- line chart
    - https://altair-viz.github.io/gallery/simple_line_chart.html
    - [X] skeleton and basic tests
    - `-s/--stroke` conflicts with `--sort/-s`; change `--sort` to `-S`?




- Vizkit class
    - [x] init
    - [x] build_chart
    - [x] refactor bar.py using Vizkit class 
    - [NA] _init_command and @self.command
        - no need for now to wrap click.Command into Vizkit
    - [NA] learn metaprogramming to delegate datakit->vizkit stuff

- [NA] how to independently invoke and manage Click commands
    - https://stackoverflow.com/questions/40091347/call-another-click-command-from-a-click-command





## 0.3.0

- [x] better option documentation
- [X] test color settings for area/line/scatter

- hist.py
    - https://altair-viz.github.io/gallery/simple_histogram.html
    - https://altair-viz.github.io/gallery/histogram_responsive.html
    - [x] skeleton
    - [x] test
    - [x] figure out how to specify bin size and intervals and counts

- [x?] write io tests, make sure stdin works (mostly done?)

- add faceting
https://stackoverflow.com/questions/61840072/show-x-and-y-labels-in-each-facet-subplot-in-altair
    - Maybe call it `-g/--grid`? That makes grouped bar charts easier to reason with.
    - [X] basic skeleton and test; made `Vizkit._manage_axis()` for now
    - [X] `-gc/--grid-columns`
    - [?] how about independent axis

- [x] change `-f/--fill`, `-s/--stroke` to `-c/--colorvar`, so handles line.stroke and bar/area/scatter.fill. 'color' is also easier for user.

- area chart
    - [x] skeleton and basic tests
    - [x] sorting the color (fill) `-cs/--color-sort`
        - [x] basic test
        - [x] added to bar charts
        - [x] maybe change '+/-' signage to 'asc/desc'
        - [ ] DRY it: should be a general function handled by Vizkit
        - [ ] Should automatically set the legend
        - [NA] practically speaking, `--fill-sort '-'` has the same effect as not setting anything


- [x]  `--hide-legend` now hides all legends

- `-xs/--x-sort`: for sorting marks by the x-axis:
    - https://vega.github.io/vega-lite/docs/sort.html#sort-field
    - https://altair-viz.github.io/user_guide/encoding.html?highlight=sort%20marks
    - [x] basic implementation
    - [x] make sure horizontal bar sorts as expected
    - [x] test, including robust error handling when invalid column name is passed in

