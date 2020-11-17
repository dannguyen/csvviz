from altair import themes


AVAILABLE_THEMES = themes.names()

DEFAULT_COLOR_SCHEMES = {
    "categorical": "category10",
    "quantitative": "blues",
    "ordinal": "blues",  # not sure if this is ever used
}
DEFAULT_FACET_COLUMNS = 2
DEFAULT_LEGEND_ORIENTATION = "right"


DEFAULT_CHART_HEIGHT = 600
DEFAULT_CHART_WIDTH = 800
