=======
History
=======


0.4.0-alpha (ongoing)
---------------------
- Can specify var titles with pipe-delimited syntax, e.g. ``-x 'fieldname|The field name'``

0.3.1 (2020-09-30)
------------------

- Removed (non-existent) Python 3.5 compat, fixed 3.6 & 3.7 compat
- Normalized area and bar charts with ``-N/--normalize``
- removed '-alpha' tag


0.3.0-alpha (2020-09-28)
------------------------

New chart types
^^^^^^^^^^^^^^^

- area
- hist (like bar charts, but for frequency count only)
- line
- scatter, which can act as bubble chart if ``--sizevar`` param is set


Grid (i.e. trellis/small multiples)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For any chart type, use ``-g/--grid`` to specify variable to map chart multiples


0.2.1-alpha (2020-09-23)
------------------------


General
^^^^^^^
- Fixed total breakage


0.2.0-alpha (2020-09-23)
------------------------

General
^^^^^^^

- ``csvviz --version`` prints out version
- viz options
    - --theme to set chart theme
    - --json to output Vegalite chart specification in JSON
    - --no-preview to not preview chart in browser (useful for testing)
    - --interactive/--static to show an interactive chart or not (default is 'static')

cli.info
^^^^^^^^

- a command for general help and listing
- Show list of colors, colorschemes, themes, etc


cli.bar
^^^^^^^

- arguments and options
    - x,y options accept integers (as strings)
    - --fill/-s
    - -H/--horizontal for horizontal bars (vertical columns is default)

- --colors/-c to set colors
- --color-scheme/-C to specify a color scheme




0.1.1-alpha (2020-09-15 16:30)
------------------------------

cli.bar
^^^^^^^

- Minimally functional: ``$ csvviz bars -x name -y things examples/tings.csv``



0.1.0-alpha (2020-09-15)
------------------------

First release on PyPI. Just a cookiecutter-pypackage skeleton stub.


