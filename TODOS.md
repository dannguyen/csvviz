# TODOS


JUST DONE: `csvviz bars -x name -y things examples/tings.csv` works!

- csvviz.cli.charters.bars.py: Work on bar subcommand, generalize from there
    - [x] read csv from command-line with pandas
    - `-x` and `-y`: 
        - [ ] should be optional and default to 0,1 respectively
        - [ ] should accept integer indexes, not just column names as strings
        - [ ] `-y` should take in multiple arguments as multiple series
        - [ ] do we need a mini-syntax for column_name,data_type(ordinal, continuous, etc)
    - `--colors` allow user to set up a color wheel to pick from 
        - OR let user pass in a list of colors, which will be assigned to corresponding -y series


- Overall design
    - subclass click.command
    - Datakit class
        - has common utils, like pandas stuff: read path/stdin, parsing options
        - write basic tests for current properties and methods

- Housekeeping
    - Get some data files to store locally

- Future thinking
    - Do some charts/apps require multiple CSVs? Or should we expect data to always be wrangled to single CSV?
        - leaning towards yes to single table only
    - setup.extras for selenium, etc. to do PNG rendering
