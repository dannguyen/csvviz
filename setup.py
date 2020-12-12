#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()


import csvviz as csvviz_vals


install_requirements = [
    "altair>=4.1",
    "altair-viewer>=0.3.0",
    "Click>=7.0",
    "pandas>=0.18",

]
setup_requirements = [
    "pytest-runner",
]
test_requirements = [
    "coverage>=5",
    "pytest>=5",
]

setup(
    name="csvviz",
    version=csvviz_vals.__version__,
    author=csvviz_vals.__author__,
    author_email=csvviz_vals.__author_email__,
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Framework :: Pytest",
        "Framework :: tox",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Utilities",
    ],
    description="Create visualizations from CSV files and the command line",
    entry_points={
        "console_scripts": [
            "csvviz=csvviz.cli:main",
            "cvz=csvviz.cli:main",

        ],
    },
    extras_require={
        "dev": [
            "black",
            "bump2version",
            "tox>=3.14",
            "twine>=3",
        ],
        "docs": [
            "sphinx",
            "sphinx_rtd_theme",
            "sphinx-autobuild",
            "vega_datasets",
            "watchdog",
        ],
        "tests": test_requirements,
    },
    install_requires=install_requirements,
    license="MIT license",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="csvviz",
    packages=find_packages(include=["csvviz", "csvviz.*"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    # tests_require=test_requirements,
    url="https://github.com/dannguyen/csvviz",
    zip_safe=False,
)
