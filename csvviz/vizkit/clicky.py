import click
from collections import defaultdict
from contextlib import contextmanager
import sys

from csvviz.settings import *

#########################################
# common Click.command options decorators
#########################################


class Clicky(click.Command):
    def format_options(self, ctx, formatter):
        """Writes all the options into the formatter if they exist."""
        common_opts = defaultdict(list)
        specific_opts = []
        for param in self.get_params(ctx):
            rv = param.get_help_record(ctx)
            if rv is not None:
                if isinstance(param, GenOption):
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

    def make_context(self, info_name, args, parent=None, **extra):
        """
        On Click < 8.0, :attr`context_class` isn't yet available, so we have to
        override the function body of make_context()...
        """
        for key, value in self.context_settings.items():
            if key not in extra:
                extra[key] = value

        ctx = MyCliContext(self, info_name=info_name, parent=parent, **extra)

        with ctx.scope(cleanup=False):
            self.parse_args(ctx, args)
        return ctx


class GenArgument(click.Argument):
    """not much different from regular click.Argument, for now"""

    @classmethod
    def foo(klass, *args, **kwargs):
        kwargs["cls"] = klass
        return click.argument(*args, **kwargs)

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

    # TODO: figure out how to use stdin without '-':
    # https://stackoverflow.com/questions/56351195/how-to-specify-a-default-value-for-argument-list-processed-by-click
    # class FilesDefaultToStdin(click.Argument):
    #     def __init__(self, *args, **kwargs):
    #         kwargs['nargs'] = -1
    #         kwargs['type'] = click.File('r')
    #         super().__init__(*args, **kwargs)

    #     # def full_process_value(self, ctx, value):
    #     #     return super().process_value(ctx, value or ('-', ))


class GenOption(click.Option):
    """supports a "category" keyword"""

    def __init__(self, *args, **kwargs):
        self.category = kwargs.pop("category")
        super().__init__(*args, **kwargs)

    @classmethod
    def foo(klass, *args, **kwargs):
        kwargs["cls"] = klass
        return click.option(*args, **kwargs)


GENERAL_OPTS = {}
GENERAL_OPTS["facet"] = {
    "facetvar": GenOption.foo(
        "--gridvar",
        "-g",
        "facetvar",
        category="Grid (i.e. faceted/trellis)",
        type=click.STRING,
        help="The name of the column to use as a facet for creating a grid of multiple charts",
    ),
    "facet_columns": GenOption.foo(
        "--grid-columns",
        "--gc",
        "facet_columns",
        category="Grid (i.e. faceted/trellis)",
        type=click.INT,
        help="Number of columns per grid row. Default is '0' for infinite.",
    ),
    "facet_sort": GenOption.foo(
        "--grid-sort",
        "--gs",
        "facet_sort",
        category="Grid (i.e. faceted/trellis)",
        type=click.Choice(["asc", "desc"], case_sensitive=False),
        help="Sort the grid of charts by its facet variable in ascending or descending order.",
    ),
}

GENERAL_OPTS["visual"] = {
    "color_list": GenOption.foo(
        "--color-list",
        "-C",
        category="Chart visual styles and properties",
        type=click.STRING,
        help="A comma-delimited list of colors to use for the relevant marks, e.g. 'deeppink,#555'",
    ),
    "color_scheme": GenOption.foo(
        "--color-scheme",
        "--CS",
        category="Chart visual styles and properties",
        type=click.STRING,
        help="The name of a Vega color scheme to use for fill (this is overridden by -C/--color-list)",
    ),
    "chart_height": GenOption.foo(
        "--height",
        "-H",
        "chart_height",
        category="Chart visual styles and properties",
        type=click.INT,
        help="The height in pixels for the chart",
    ),
    "no_legend": GenOption.foo(
        "--no-legend",
        category="Chart visual styles and properties",
        is_flag=True,
        help="Omits any/all legends",
    ),
    # TKD
    # "theme": GenOption.foo(
    #     "--theme",
    #     category="Chart visual styles and properties",
    #     type=click.Choice(AVAILABLE_THEMES, case_sensitive=False),
    #     default="default",
    #     help="Choose a built-in theme for chart",
    # ),
    "chart_title": GenOption.foo(
        "--title",
        "-T",
        "chart_title",
        category="Chart visual styles and properties",
        type=click.STRING,
        help="A title for the chart",
    ),
    "chart_width": GenOption.foo(
        "--width",
        "-W",
        "chart_width",
        category="Chart visual styles and properties",
        type=click.INT,
        help="The width in pixels for the chart",
    ),
}


GENERAL_OPTS["axis"] = {
    "xlim": GenOption.foo(
        "--xlim",
        category="Axis",
        type=click.STRING,
        help="Set the min,max of the x-axis with a comma delimited string, e.g. '-10,50'",
    ),
    "ylim": GenOption.foo(
        "--ylim",
        category="Axis",
        type=click.STRING,
        help="Set the min,max of the y-axis with a comma delimited string, e.g. '-10,50'",
    ),
}


"""common input output/options"""
GENERAL_OPTS["io"] = {
    "input_file": GenArgument.foo(
        "input_file",
        type=click.File("r"),
        required=False,
        callback=GenArgument.check_piped_arg,
    ),
    "is_interactive": GenOption.foo(
        "--interactive/--static",
        "is_interactive",
        category="Output and presentation",
        default=True,
        help="Produce an interactive (default) or static version of the chart, in HTML+JS",
    ),
    "json": GenOption.foo(
        "--json/--no-json",
        "-j /",
        "to_json",
        category="Output and presentation",
        default=False,
        help="Output to stdout the Vega JSON representation",
    ),
    "no_preview": GenOption.foo(
        "--no-preview",
        "--NP",
        category="Output and presentation",
        is_flag=True,
        help="By default, csvviz opens a web browser to show the chart",
    ),
}


def general_options_decor(fn, exclude_options=[]):
    """decorator"""
    for groupkey, opts in GENERAL_OPTS.items():
        for oname, o in opts.items():
            if oname not in exclude_options:
                fn = o(fn)
    return fn


#############################################
# Click Formatter stuff
#############################################
class MyCliHelpFormatter(click.formatting.HelpFormatter):
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


class MyCliContext(click.Context):
    # formatter_class = MyCliHelpFormatter  # this will only have an effect for Click 8.0

    def make_formatter(self):
        """
        On Click < 8.0, :attr`formatter_class` isn't yet available, so we have to
        override the function body of make_formatter(), i.e.

        return self.formatter_class(
            width=self.terminal_width, max_width=self.max_content_width
        )
        """
        return MyCliHelpFormatter(
            width=self.terminal_width, max_width=self.max_content_width
        )
