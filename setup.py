#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()


import csvviz as csvviz_vals



requirements = ['Click>=7.0', ]
setup_requirements = ['pytest-runner', ]
test_requirements = ['pytest>=3', ]

setup(
    name='csvviz',
    version=csvviz_vals.__version__,
    author=csvviz_vals.__author__,
    author_email=csvviz_vals.__author_email__,
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Create visualizations from CSV files and the command line",
    entry_points={
        'console_scripts': [
            'csvviz=csvviz.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='csvviz',
    packages=find_packages(include=['csvviz', 'csvviz.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/dannguyen/csvviz',
    zip_safe=False,
)
