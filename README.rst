======
csvviz
======


.. .. image:: https://img.shields.io/pypi/v/csvviz.svg
..         :target: https://pypi.python.org/pypi/csvviz

.. .. image:: https://img.shields.io/travis/dannguyen/csvviz.svg
..         :target: https://travis-ci.com/dannguyen/csvviz

.. .. image:: https://readthedocs.org/projects/csvviz/badge/?version=latest
..         :target: https://csvviz.readthedocs.io/en/latest/?badge=latest
..         :alt: Documentation Status


Create visualizations from CSV files and the command line


Current status
--------------

Pretty usable::

    $ csvviz bar -x name -y amount examples/tings.csv

    $ csvviz line -x date -y price -c company examples/stocks.csv



But undocumented so far, other than running ``$ csvviz --help``


.. * Documentation: https://csvviz.readthedocs.io.


Features
--------

* Can do the standard chart types
* Produces validated Vega-lite JSON output that can be reused
* Free software: MIT license


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage



Dev instructions
----------------

To install on your own machine for development::

    $ make install

Note: setup.py/requirements.txt is not correctly set up yet...


(note to self) To publish on pypi::

    $ make release
