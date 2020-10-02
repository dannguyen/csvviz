from collections import defaultdict
from contextlib import contextmanager
from pathlib import Path
import sys
from typing import Any as typeAny, Mapping as typeMapping, NoReturn as typeNoReturn
from typing import (
    Dict as typeDict,
    List as typeList,
    Tuple as typeTuple,
    Union as typeUnion,
)
from typing import IO as typeIO

import altair as alt
import click

from csvviz import __version__
from csvviz.settings import *



def _echo(*args, use_stderr) -> typeNoReturn:
    outobjects = []
    for obj in args:
        if isinstance(obj, typeMapping):
            obj = json.dumps(obj, indent=2)
        else:
            obj = str(obj)
        outobjects.append(obj)
    click.echo(" ".join(outobjects), err=use_stderr)

def clout(*args) -> typeNoReturn:
    """
    top-level method that is used to output to stdout
    """
    _echo(*args, use_stderr=False)

def clerr(*args) -> typeNoReturn:
    """
    top-level method that is used to output to stderr
    """

    # TODO: refactor/decorate this jsons stuff
    _echo(*args, use_stderr=True)


def clexit(code: int, message: typeAny = None):
    if message:
        clerr(message)
    sys.exit(code)

def print_version(ctx=None, param=None, value=None) -> typeNoReturn:
    """
    https://click.palletsprojects.com/en/3.x/options/#callbacks-and-eager-options
    """
    if not ctx:
        clout(__version__)
    else:
        # this is being used as a callback
        if not value or ctx.resilient_parsing:
            return
        clout(__version__)
        ctx.exit()




#########################################
# common Click.command options decorators
#########################################

# TODO: This stuff should be located next to Vizkit stuff, not floating in general cli-utils space
class VizHelpFormatter(click.formatting.HelpFormatter):
    def write_lined_heading(self, heading):
        """Writes a heading into the buffer, sans trailing colon"""
        top_sep = "".join("─" for i in range(self.width))
        #       bottom_sep = ''.join('–' for i in range(len(heading)))
        bottom_sep = "".join("─" for i in range(self.width))

        self.write(f"{'':>{self.current_indent}}{top_sep}\n")
        self.write(f"{'':>{self.current_indent}}{heading}\n")
        self.write(f"{'':>{self.current_indent}}{bottom_sep}\n")

    @contextmanager
    def option_section(self, name):
        """Helpful context manager that writes a paragraph, a heading,
        and the indents.

        :param name: the section name that is written as heading.
        """
        self.write_paragraph()
        self.write_lined_heading(name)
        self.indent()
        try:
            yield
        finally:
            self.dedent()

    @contextmanager
    def category_section(self, name):
        sep = "".join("─" for i in range(len(name)))
        self.write_paragraph()
        self.write(f"{'':>{self.current_indent}}{name}\n")
        self.write(f"{'':>{self.current_indent}}{sep}\n")
        self.indent()
        try:
            yield
        finally:
            self.dedent()


class VizContext(click.Context):
    # formatter_class = VizHelpFormatter  # this will only have an effect for Click 8.0

    def make_formatter(self):
        """
        On Click < 8.0, :attr`formatter_class` isn't yet available, so we have to
        override the function body of make_formatter(), i.e.

        return self.formatter_class(
            width=self.terminal_width, max_width=self.max_content_width
        )
        """
        return VizHelpFormatter(
            width=self.terminal_width, max_width=self.max_content_width
        )


class VizCommand(click.Command):
    def format_options(self, ctx, formatter):
        """Writes all the options into the formatter if they exist."""
        common_opts = defaultdict(list)
        specific_opts = []
        for param in self.get_params(ctx):
            rv = param.get_help_record(ctx)
            if rv is not None:
                if isinstance(param, VizGeneralOption):
                    cat = param.category
                    common_opts[cat].append(rv)
                else:
                    specific_opts.append(rv)

        if specific_opts:
            with formatter.option_section(f"Options specific to `{self.name}` command"):
                formatter.write_dl(specific_opts)

        if common_opts:
            with formatter.option_section(f"Common options"):
                for category, opts in common_opts.items():
                    with formatter.category_section(category):
                        formatter.write_dl(opts)

    # context_class = VizContext
    def make_context(self, info_name, args, parent=None, **extra):
        """
        On Click < 8.0, :attr`context_class` isn't yet available, so we have to
        override the function body of make_context(), i.e.


        """
        for key, value in self.context_settings.items():
            if key not in extra:
                extra[key] = value

        ctx = VizContext(self, info_name=info_name, parent=parent, **extra)

        with ctx.scope(cleanup=False):
            self.parse_args(ctx, args)
        return ctx


def viz_general_argument(*args, **kwargs):
    kwargs["cls"] = VizGeneralArgument
    return click.argument(*args, **kwargs)


def viz_general_option(*args, **kwargs):
    kwargs["cls"] = VizGeneralOption
    return click.option(*args, **kwargs)


class VizGeneralArgument(click.Argument):
    # TODO: figure out how to use stdin without '-':
    # https://stackoverflow.com/questions/56351195/how-to-specify-a-default-value-for-argument-list-processed-by-click
    # class FilesDefaultToStdin(click.Argument):
    #     def __init__(self, *args, **kwargs):
    #         kwargs['nargs'] = -1
    #         kwargs['type'] = click.File('r')
    #         super().__init__(*args, **kwargs)

    #     # def full_process_value(self, ctx, value):
    #     #     return super().process_value(ctx, value or ('-', ))
    @staticmethod
    def check_piped_arg(ctx, param, value):
        """
        hack courtesy of: https://github.com/pallets/click/issues/1202
        """
        if value:
            return value
        else:
            if not sys.stdin.isatty():
                return click.get_text_stream("stdin")
            else:
                ctx.fail(
                    f"Missing argument: {param.human_readable_name}.\n"
                    "Pass in a file path, or explicitly pass in '-' for stdin, "
                    "or just pipe into the command."
                )


class VizGeneralOption(click.Option):
    def __init__(self, *args, **kwargs):
        self.category = kwargs.pop("category")
        super().__init__(*args, **kwargs)


GENERAL_OPTS = {}


GENERAL_OPTS["facet"] = {
    "facetvar": viz_general_option(
        "--grid",
        "-g",
        "facetvar",
        category="Grid (i.e. faceted/trellis)",
        type=click.STRING,
        help="The name of the column to use as a facet for creating a grid of multiple charts",
    ),
    "facetcolumns": viz_general_option(
        "--grid-columns",
        "-gc",
        "facetcolumns",
        category="Grid (i.e. faceted/trellis)",
        default=0,
        type=click.INT,
        help="Number of columns per grid row. Default is '0' for infinite.",
    ),
    "facetsort": viz_general_option(
        "--grid-sort",
        "-gs",
        "facetsort",
        category="Grid (i.e. faceted/trellis)",
        type=click.Choice(["asc", "desc"], case_sensitive=False),
        help="Sort the grid of charts by its facet variable in ascending or descending order.",
    ),
}

GENERAL_OPTS["visual"] = {
    "colors": viz_general_option(
        "--colors",
        "-C",
        category="Chart visual styles and properties",
        type=click.STRING,
        help="A comma-delimited list of colors to use for the relevant marks",
    ),
    "color_scheme": viz_general_option(
        "--color-scheme",
        "-CS",
        category="Chart visual styles and properties",
        type=click.STRING,
        help="The name of a Vega color scheme to use for fill (this is overridden by -C/--colors)",
    ),
    "no_legend": viz_general_option(
        "--no-legend",
        category="Chart visual styles and properties",
        is_flag=True,
        help="Omits any/all legends",
    ),
    "theme": viz_general_option(
        "--theme",
        category="Chart visual styles and properties",
        type=click.Choice(alt.themes.names(), case_sensitive=False),
        default="default",
        help="choose a built-in theme for chart",
    ),  # TODO: refactor alt.themes.names() to constant
    "title": viz_general_option(
        "--title",
        "-t",
        category="Chart visual styles and properties",
        type=click.STRING,
        help="A title for the chart",
    ),
}


GENERAL_OPTS["axis"] = {
    "xlim": viz_general_option(
        "--xlim",
        category="Axis",
        type=click.STRING,
        help="Set the min,max of the x-axis with a comma delimited string, e.g. '-10,50'",
    ),
    "ylim": viz_general_option(
        "--ylim",
        category="Axis",
        type=click.STRING,
        help="Set the min,max of the y-axis with a comma delimited string, e.g. '-10,50'",
    ),
}


"""common input output/options"""
GENERAL_OPTS["io"] = {
    "input_file": viz_general_argument(
        "input_file",
        type=click.File("r"),
        required=False,
        callback=VizGeneralArgument.check_piped_arg,
    ),
    "is_interactive": viz_general_option(
        "--interactive/--static",
        "is_interactive",
        category="Output and presentation",
        default=True,
        help="Produce an interactive (default) or static version of the chart, in HTML+JS",
    ),
    "json": viz_general_option(
        "--json/--no-json",
        "-j /",
        "to_json",
        category="Output and presentation",
        default=False,
        help="Output to stdout the Vega JSON representation",
    ),
    "no_preview": viz_general_option(
        "--no-preview",
        "--np",
        category="Output and presentation",
        is_flag=True,
        help="By default, csvviz opens a web browser to show the chart",
    ),
}


def general_options_decor(fn, exclude_options=[]):
    for groupkey, opts in GENERAL_OPTS.items():
        for oname, o in opts.items():
            if oname not in exclude_options:
                fn = o(fn)
    return fn
