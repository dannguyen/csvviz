# TODOS



## The state of things (2020-11-20): v0.4.9


- Rethink adding barkit and columnkit, on the basis that histkit is ALWAYS vertical columns: https://ggplot2.tidyverse.org/reference/geom_histogram.html
    - and if user doesn't want that, provide special option to histkit

Check out ggplot2 doc pages:
- each geom page has self-contained examples
    - Get those right, worry about gallery in future release
- geoms:
    - area: https://ggplot2.tidyverse.org/reference/geom_ribbon.html
    - bar: https://ggplot2.tidyverse.org/reference/geom_bar.html
    - columns: https://ggplot2.tidyverse.org/reference/geom_bar.html
    - line: https://ggplot2.tidyverse.org/reference/geom_path.html
    - histogram: https://ggplot2.tidyverse.org/reference/geom_histogram.html
    - rect/heatmap: https://ggplot2.tidyverse.org/reference/geom_tile.html
    - scatter: https://ggplot2.tidyverse.org/reference/geom_point.html
        - jitter: https://ggplot2.tidyverse.org/reference/geom_jitter.html
    - density: https://ggplot2.tidyverse.org/reference/geom_density.html
        - `Computes and draws kernel density estimate, which is a smoothed version of the histogram. This is a useful alternative to the histogram for continuous data that comes from an underlying smooth distribution.`

- mostly done with 0.5.0 -- put version number at '0.4.9'
- think about doing documentation
    - get an idea of what's easy to explain and what seems extraneous
    - find another gallery site to pattern off of
        - altair gallery: https://altair-viz.github.io/gallery/
        - https://www.r-graph-gallery.com/
        - https://vega.github.io/vega-lite/examples/
        - http://www.cookbook-r.com/Graphs/
    - Gallery: make a spreadsheet of all chart types and variations
        - https://docs.google.com/spreadsheets/d/1X8hn71T5jHNeMXLc03LOeak-uVTu4tSr-ZnfVcCXeJ8/edit#gid=0
- grid vs facet
    - should probably call option `-f/--facetvar` to maintain consistency with docs and common understanding
    - also, 'grid' implies being able to specify a regular grid, e.g. '4x8'...but we only give user option to specify `--grid-columns`

## 0.5.0 – better bespoke visuals and labels

##### overall
- [x] kill --theme for now
- [x] set altair theme to None

##### color_list and color_scheme

- [x] allow color_list to set mark.color even if --colorvar left unspecified
        - https://vega.github.io/vega/docs/config/#mark


##### Vizkit.chart stuff should be a class?
- [?] cut out commented and deprecated code
- [x] commit and push refactoring work for tonight
- [x] Dataful should be a class
- [x] similar to channelgroup
- [x] name is Chart for now... ChartSpec, or Viz?
- refactoring Vizkit.init   
    - [no why?] do not let Viz class touch `colorvar` or Vizkit.color_channel_name
    - [NO] maybe Viz should handle channels/ChannelGroup, and Vizkit shouldn't at all?
        - but then Viz would have to know about Vizkit.color_channel_name
    - [x] rename viz_info/iz_epilog to help_info and help_epilog
    - [x] is_faceted and interactive_mode are now Chart properties and are removed from Vizkit
- testing
    - [x] all prior tests run, including integration
    - [x] held up at vizzes/test_*, with vizkit.mark_name and vizkit.chart.mark_name breaking on test_line.py

##### facet/grid stuff

- Example calls:
        ```sh
        # simple
        cvz bar examples/jobless.csv -x year:O -y thousands -g sector  --json
        # complex
        cvz line examples/real/unemployment.csv \
            -x month:O -y rate -c sector -g year:O --json
        ```
- [ ] kill `--grid-sort` for now?

- In general
    - [x] `-g` should be `--gridvar` not `--grid` (but clicky stores it in facetvar)
    - [x] `--grid-columns=0` creates a chart with unlimited facets
    - if `-g/--gridvar`, calculate unique grid variables and set grid columns accordingly
    - set facet['spacing'] to DEFAULT_FACET_SPACING https://vega.github.io/vega-lite/docs/facet.html#config
    - [x] Vizkit should have is_faceted property, which is derived from self.channels
    - SHOULD I RENAME --grid to --facet?
        - note that what we call `--grid` to the calling user is internally referred to as `facet`
        - Vega refers to as a "wrapped facet" chart, i.e. with "facet encoding": https://vega.github.io/vega-lite/docs/facet.html#facet-encoding
        - Further note: Vega also has a "grid facet" chart which is something slightly different: https://vega.github.io/vega-lite/docs/facet.html#grid-facet-with-row-and-column-encoding
            - should we change up names?
                - if we use `-f/--facetvar`, this means we can't use `-f` for other stuff, like `--format`...
            - ggplot2 context
                - ggplot2 calls it a `facet_grid`: https://ggplot2.tidyverse.org/reference/facet_grid.html
                - extra confusing: ggplot2 says a `facet_wrap` is when "you have only one variable with many levels"???
                    - i.e vega's facet_row/facet_column: http://zevross.com/blog/2019/04/02/easy-multi-panel-plots-in-r-using-facet_wrap-and-facet_grid-from-ggplot2/#useful-arguments-for-facet_wrap-and-facet_grid

- How to deal with sizing for grid charts
    - https://vega.github.io/vega-lite/docs/size.html#width-and-height-of-multi-view-displays
    - use chart_grid_default_height/width? Or none at all?
    - [x] allow `--width/--height` to have effect
        - [x] defines width/height of each facet
    




##### chart width/height, i.e. init_props
- https://vega.github.io/vega-lite/docs/size.html#specifying-fixed-width-and-height
- [x] chart-wide with `-W` and `-H`
- [x] vizkit now has class vars default_chart_width and default_chart_height
- autosize is by default set in chart spec
- write tests 
    - [x] create tests/unit/charting
    - [x] to confirm the default h/w and autosize



chart config
- https://altair-viz.github.io/user_guide/customization.html#global-config
- separate it from chart styling
- what to do with config.continuouswidth?

- hist
    - [x] test is_horizontal (changed flipxy)
- make streamgraph 
    - https://altair-viz.github.io/gallery/streamgraph.html
    - https://www.r-graph-gallery.com/154-basic-interactive-streamgraph-2.html
    - get better sample data (vega?)
        - [x] examples/real/unemployment.csv
    - barebones implementation
        - [x] `csvviz stream -x 'yearmonth(date)' -y 'thousands' -c 'sector'  --json examples/jobless.csv`
    - [x] basic tests


- heatmap 
    - [x] barebones implementation
    - default color scale is categorical and terrible
        - this is fixed with `--color-scheme` but a sane default should be used:
            ``` 
            cvz area -x 'yearmonth(date)' -y 'sum(thousands)' -c sector \
                examples/real/unemployment.csv --title 'Unemployment'
            ```
    - [NO] by default, third column should be passed into -c?
    - [DEFER] enable sorting x-axis (and y-axis?)
    - [x] use heatmap to try out sizing options, since default heatmap is tiny!
    - [ ] write tests

    - notes:
        - https://altair-viz.github.io/gallery/simple_heatmap.html 
            - (note 5,000 row limit) https://altair-viz.github.io/gallery/weather_heatmap.html 
            - pretty bespoke: https://altair-viz.github.io/gallery/layered_heatmap_text.html
            - (broken URL) https://altair-viz.github.io/gallery/binned_heatmap.html
        - https://www.data-to-viz.com/graph/heatmap.html
        - https://www.r-graph-gallery.com/heatmap.html
            - Most basic heatmap: https://www.r-graph-gallery.com/215-the-heatmap-function.html


- [X] deprecate (TKD) color-sort for area/bar/stream
    - when there *is* encoding
        - `--color-sort=asc` arranges the marks in an order *opposite* of how they're sorted in the legend, which is not optimal
    - [x] remove for now; produced JSON should have no `order` encoding
    - [x] write tests to confirm this: **test_bar.py:test_no_order_for_now**



## 0.5.2 -- more bespokeness 

##### make bar and column separate charts

- [ ] kill `--HZ/--horizontal`?
- ggplot2 has a geom_hist, and it only allows for column charts

- density
    - https://altair-viz.github.io/user_guide/transform/density.html
    - https://www.r-graph-gallery.com/density-plot.html


- smarter default color schemes
    - [x] should depend on `color_channel` being quantitative vs categorical
    - for categorical color_channel type, use tableau10 when fewer than 10 categories, and tableau20 otherwise
        - https://vega.github.io/vega/docs/schemes/
        - [ ] write separate test suite
        - [ ] if color_channel has `.aggregate`, do pandas group count


- [ ] make Columnkit?
    - but then how to handle Histkit? Other than to make it always a column kit?


- More chartwide options
    - `-op/--opacity` mark opacity option, for use in scatterplots
    - bar width: https://altair-viz.github.io/user_guide/customization.html#adjusting-the-width-of-bar-marks

- sorting
    - [ ] allow sorting by array of values: https://vega.github.io/vega-lite/docs/sort.html#sort-array

- More sizing features
    - https://vega.github.io/vega-lite/docs/spec.html#single
    - [ ] should I use step sizing? https://vega.github.io/vega-lite/docs/facet.html#resolve
    - [ ] should i create new click option where user sets total width and height, and futz width/height to fit?


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
    


## 0.5.5 

##### channelgroup limits

- [ ] allow user to do: `--xlim ',120' and --ylim '20,' `
- [ ] what happens when `--xlim [0,50]` but xvar is non-quant?
- [ ] add tests and warnings


- axis properties
    - [ ] `--no-grid`
    - https://altair-viz.github.io/gallery/us_population_over_time_facet.html
    - y-axis number format `--yf/--y-format`
    - https://vega.github.io/vega-lite/docs/config.html#format
    - https://github.com/d3/d3-format#locale_format
    - subcommand `info number_formats`


    - padding:
        https://vega.github.io/vega-lite/docs/spec.html#top-level

    - https://altair-viz.github.io/user_guide/configuration.html#config-view
    - https://altair-viz.github.io/user_guide/generated/toplevel/altair.Chart.html?highlight=configure#altair.Chart
    - chart-fill `-BGC/--background-color`



## 0.5.9 layered charts with highlights and rules

- https://altair-viz.github.io/gallery/bar_chart_with_highlighted_segment.html


## 0.6.0 – better input/output

- read csv:
    - option to specify typecast for columns, e.g. prevent fips from being returned as integers
- read json:
    - serialized pandas output
    - can detect from stdin
    - need flags to force json/csv? `--input-format=json/--input-json`

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
    - outputs JSON by default
    - reify pandas sequence
        - https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.pipe.html
    
        - https://towardsdatascience.com/using-pandas-pipe-function-to-improve-code-readability-96d66abfaf8
        - https://towardsdatascience.com/the-unreasonable-effectiveness-of-method-chaining-in-pandas-15c2109e3c69
            - https://tomaugspurger.github.io/method-chaining.html
    - https://pandas.pydata.org/Pandas_Cheat_Sheet.pdf

    - edit/calculate: these functions should accept a list of columns and do in-place replacement
        - drop-na: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.dropna.html
        - fill-na: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.fillna.html
        - date transforms
        - round: https://pandas.pydata.org/pandas-docs/version/0.22.0/generated/pandas.DataFrame.round.html
        - floor/ceil: https://stackoverflow.com/questions/27592456/floor-or-ceiling-of-a-pandas-series-in-python
        - replace: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.replace.html
        - astype

    - transform: (creates new columns) 
        - concat cols
        - cut: https://towardsdatascience.com/data-handling-using-pandas-cleaning-and-processing-3aa657dc9418
            - `--bin 'col_name_to_bin|new_col_name '[bins]0,5,10,20'`
            - `--bin-cat 'col_name_to_bin|new_col_name' '[bins]0,5,10,20' '[cats]awful,average,good,great'`
            - `bin-q`: qcut

    - aggregates
        - groupby: https://pandas.pydata.org/docs/getting_started/intro_tutorials/06_calculate_statistics.html#aggregating-statistics-grouped-by-category

    - reshape
        - rename columns 'org_name_1,org_name2' 'new_name_1,new_name_2'
        - select:
            - https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html
            - https://pandas.pydata.org/docs/getting_started/intro_tutorials/03_subset_data.html#how-do-i-select-specific-columns-from-a-dataframe
        - sort: `sort_values('amount', ascending=False)`
        - join/merge ??
        - pivot
        - filtering
            - grep: `filter` https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.filter.html
            - query/where: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.query.html

        
## 0.9.5 - the documentation edition

- clean up command info/options text
- write Readthedocs

## 0.99 release (usable beta)

## 1.0 release

- revisions to CLI api


##### colorvar should override config, not mark
- https://altair-viz.github.io/user_guide/customization.html#encoding
- However, it's probably better to do color range at the encoding level, in case we want to layer charts...

## 2.0 

- add option to do seaborn viz


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


## Refactoring 2020-11-17

ChannelGroup addition color stuff:
- [x] should validate colorscheme name
- [x] kill `-C` `-CS` and other dumb arg shortcuts [just made them more consistent]

(2020-11-16 and prior has been moved to Old section)


## Update 2020-11-11

Been many weeks since I looked at this code base. After some struggling, was able to come up with a reliable bar chart command:

    $  cvz bar examples/stocks.csv -x date:N -y price:Q -c company --json

Scatter chart:

    $ cvz scatter -x date:T examples/tonk.csv --json


### Jumping in

- Moved a bunch of 0.4.0 stuff to 0.5.5 -- basically everything that wasn't already done, and seemed like over-customization stuff, like `--no-grid`
- moving on to 0.5.0 with new chart types
- working on heatmap: basic implementation so far (2020-11-11)
- time for a code refactor? vizkit.py is just a mess to me
    - add more type hinting
    - use more OOP stuff like @property


### 2020-11-16: refactor

More general vizkit stuff:
- [x] refactor create_channels._set_default_xyvar_args
- [x] ancillary mixins have been moved to interfaces.py for now
- [x] Vizkit.kwargs should be renamed to Vizkit.options


ChannelGroup phase 1:
- implementation
    - [x] Channeled's basic implementation
- [x] for every vizzes' click option, '--colorvar' should go to 'colorvar', not 'fillvar/strokevar'. Because channelgroup should use its channel_color_name to resolve what color should be.
- [x] same for `--colorsort`
- [x] basic tests
- [x] integration/replaced Channeled
- [x] parse_channel_arg/parse_shorthand can be removed from interfaces.ArgFace
- [x] what to do with Channeled.configure_channel_sort?
    - was un-DRYed for now
- [x] what to do with Channeled.resolve_channel_name? 
    - moved to ChannelGroup.get_data_field

### 2020-11-13: refactor

- [x] vizkit.py  is now vizkit/init
- [x] vizkit channel stuff is now in vizkit/channeled, as a temp refactor

### 2020-11-12: refactor

Refamiliarizing myself with code:
- in vizkit.py, fix/clean up "manage"/"create"/"configure" naming convention
- figure out configure_legend
- "finalize" methods need their own mixin?

### moar refactor

- [ ] make warnings.append be a method/property
- color stuff
    - [X] for each vizkit.clicky, `--color` should just go to `colorvar`, not `fillvar`, `strokevar`
    - [?] in vizkit, remove fill/stroke from ENCODED list
    - [?] vizkit.create_channel should initiate fill/stroke based on colorvar
    - [ ] write test for get_color warning...
- vizkit
    - [x] channels-related methods not meant to be subclassed should in own mixin
        - break up create_channels into more submethods
    - [?] clean up channels code, it's too big
    - [x] organize properties
    
### first refactor phase

- [x] Vizkit.validate_options, to be implemented by each class
- color stuff
    - [x] vizkit.set_channel_colorscale now is vizkit.colorize_channels
    - [x] --colors should be --color-list
    - [x] write test for vizkit.color_channel_name
