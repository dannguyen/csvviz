"""a holding place for functionality that I haven't figured out how to separate"""

import altair as alt
from altair.utils import parse_shorthand as alt_parse_shorthand
import altair_viewer as altview
import click
import pandas as pd
from typing import (
    Dict as DictType,
    NoReturn as NoReturnType,
    Optional as OptionalType,
    Tuple as TupleType,
    Union as UnionType,
)


from csvviz.exceptions import VizValueError
from csvviz.helpers import parse_delimited_str
from csvviz.utils.sysio import (
    clout,
    clerr,
    clexit,
)  # TODO: this should be refactored, vizkit should not know about these
from csvviz.vizkit.clicky import (
    Clicky,
    general_options_decor,
)  # TODO: general_options_decor should not be knowable here?


class ClickFace:
    """The interface for making a click command, including meta info for generating the help"""

    """TODO most of this should be in clicky.py?"""

    @classmethod
    def cmd_wrapper(klass):
        # TODO: this is bad OOP; func should be properly named and in some more logical place
        def func(**options):
            try:
                vk = klass(input_file=options.get("input_file"), options=options)
            except VizValueError as err:
                # TODO: dude what?
                clexit(1, err)
            else:
                vk.output_chart()
                [clerr(f"Warning: {w}") for w in vk.warnings]
                vk.preview_chart()

        return func

    @classmethod
    def register_command(klass):
        command = klass.cmd_wrapper()
        command = click.command(
            cls=Clicky,
            name=klass.viz_commandname,
            help=klass.help_info,
            epilog=klass.help_epilog,
        )(command)
        command = general_options_decor(command)
        for decor in klass.COMMAND_DECORATORS:
            command = decor(command)

        return command


class OutputFace:
    """a namespace/mixin for functions that output the viz"""

    def output_chart(self) -> NoReturnType:
        """Send to stdout the desired representation of a chart"""
        if self.options["to_json"]:
            clout(self.chart_json())

    def preview_chart(self) -> NoReturnType:
        if not self.options.get("no_preview"):
            self.open_chart_in_browser(self.raw_chart)

    @staticmethod
    def open_chart_in_browser(chart: alt.Chart) -> NoReturnType:
        # a helpful wrapper around altair_viewer.altview
        altview.show(chart)
