from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure

from csvviz.exceptions import ConflictingFlagsError
from csvviz.specs import (
    AreaSpec,
    BarSpec,
    BaseSpec,
    HeatmapSpec,
    HistSpec,
    LineSpec,
    ScatterSpec,
)

DEFAULT_WIDTH_PX = 800
DEFAULT_HEIGHT_PX = 500
DEFAULT_DPI = 100


class MatplotlibRenderer:
    """Renders charts using matplotlib + seaborn. Returns matplotlib.figure.Figure."""

    def render_bar(self, spec: BarSpec, df: pd.DataFrame) -> Figure:
        self._apply_theme(spec)
        x, y = (spec.yvar, spec.xvar) if spec.horizontal else (spec.xvar, spec.yvar)

        if spec.facet:
            if spec.stacked:
                raise ConflictingFlagsError(
                    "--stacked/--normalized is not supported with --facet in v0.5"
                )
            if spec.sort:
                raise ConflictingFlagsError("--sort is not supported with --facet in v0.5")
            return self._facet_figure(
                spec,
                df,
                kind="bar",
                x=x,
                y=y,
                hue=spec.colorvar,
                orient="h" if spec.horizontal else "v",
                order=self._bar_order(df, spec),
            )

        if spec.stacked and spec.sort:
            raise ConflictingFlagsError(
                "--sort is not supported with --stacked/--normalized in v0.5"
            )

        fig, ax = self._new_figure(spec)
        order = self._bar_order(df, spec)
        if spec.stacked:
            self._draw_stacked_bar(ax, df, spec)
        elif spec.colorvar:
            sns.barplot(
                data=df,
                x=x,
                y=y,
                hue=spec.colorvar,
                ax=ax,
                palette=spec.palette,
                order=order,
                orient="h" if spec.horizontal else "v",
            )
        else:
            sns.barplot(
                data=df,
                x=x,
                y=y,
                ax=ax,
                color=(spec.colors[0] if spec.colors else None),
                order=order,
                orient="h" if spec.horizontal else "v",
            )
        self._finalize(fig, ax, spec)
        return fig

    def render_line(self, spec: LineSpec, df: pd.DataFrame) -> Figure:
        self._apply_theme(spec)
        if spec.facet:
            return self._facet_figure(
                spec,
                df,
                kind="line",
                x=spec.xvar,
                y=spec.yvar,
                hue=spec.colorvar,
            )
        fig, ax = self._new_figure(spec)
        sns.lineplot(
            data=df,
            x=spec.xvar,
            y=spec.yvar,
            hue=spec.colorvar,
            ax=ax,
            palette=spec.palette,
        )
        self._finalize(fig, ax, spec)
        return fig

    def render_scatter(self, spec: ScatterSpec, df: pd.DataFrame) -> Figure:
        self._apply_theme(spec)
        if spec.facet:
            return self._facet_figure(
                spec,
                df,
                kind="scatter",
                x=spec.xvar,
                y=spec.yvar,
                hue=spec.colorvar,
                size=spec.sizevar,
                alpha=spec.alpha,
            )
        fig, ax = self._new_figure(spec)
        sns.scatterplot(
            data=df,
            x=spec.xvar,
            y=spec.yvar,
            hue=spec.colorvar,
            size=spec.sizevar,
            alpha=spec.alpha,
            ax=ax,
            palette=spec.palette,
        )
        self._finalize(fig, ax, spec)
        return fig

    def render_hist(self, spec: HistSpec, df: pd.DataFrame) -> Figure:
        self._apply_theme(spec)
        if spec.facet:
            return self._facet_figure(
                spec,
                df,
                kind="hist",
                x=spec.xvar,
                hue=spec.colorvar,
                bins=spec.bins or "auto",
                cumulative=spec.cumulative,
            )
        fig, ax = self._new_figure(spec)
        sns.histplot(
            data=df,
            x=spec.xvar,
            hue=spec.colorvar,
            bins=spec.bins or "auto",
            cumulative=spec.cumulative,
            ax=ax,
            palette=spec.palette,
        )
        self._finalize(fig, ax, spec)
        return fig

    def render_area(self, spec: AreaSpec, df: pd.DataFrame) -> Figure:
        if spec.facet:
            raise ConflictingFlagsError(
                f"{spec.__class__.__name__} does not support faceting in v0.5"
            )
        self._apply_theme(spec)
        fig, ax = self._new_figure(spec)

        if spec.colorvar and spec.stacked:
            pivot = df.pivot_table(
                index=spec.xvar,
                columns=spec.colorvar,
                values=spec.yvar,
                aggfunc="sum",
            ).fillna(0)
            if spec.normalized:
                pivot = pivot.div(pivot.sum(axis=1), axis=0) * 100.0
            ax.stackplot(pivot.index, pivot.T.values, labels=list(pivot.columns))
            ax.legend(loc="best")
        elif spec.colorvar:
            for series_name, group in df.groupby(spec.colorvar):
                ax.fill_between(
                    group[spec.xvar], group[spec.yvar], alpha=0.4, label=str(series_name)
                )
            ax.legend(loc="best")
        else:
            ax.fill_between(df[spec.xvar], df[spec.yvar], alpha=0.6)

        self._finalize(fig, ax, spec)
        return fig

    def render_heatmap(self, spec: HeatmapSpec, df: pd.DataFrame) -> Figure:
        if spec.facet:
            raise ConflictingFlagsError(
                f"{spec.__class__.__name__} does not support faceting in v0.5"
            )
        self._apply_theme(spec)
        fig, ax = self._new_figure(spec)
        pivot = df.pivot_table(
            index=spec.yvar, columns=spec.xvar, values=spec.valuevar, aggfunc="sum"
        )
        sns.heatmap(pivot, ax=ax)
        self._finalize(fig, ax, spec)
        return fig

    def _facet_figure(self, spec: BaseSpec, df: pd.DataFrame, kind: str, **kwargs) -> Figure:
        """Use seaborn's faceted constructors. Returns g.fig from the FacetGrid."""
        common = dict(
            data=df,
            col=spec.facet,
            col_wrap=spec.facet_cols,
            palette=spec.palette,
        )
        if kind == "bar":
            g = sns.catplot(kind=kind, **common, **kwargs)
        elif kind in ("scatter", "line"):
            g = sns.relplot(kind=kind, **common, **kwargs)
        elif kind == "hist":
            g = sns.displot(kind="hist", **common, **kwargs)
        else:
            raise ValueError(f"no faceted constructor for kind={kind!r}")
        w_px = spec.width_px or DEFAULT_WIDTH_PX
        h_px = spec.height_px or DEFAULT_HEIGHT_PX
        g.fig.set_size_inches(w_px / DEFAULT_DPI, h_px / DEFAULT_DPI)
        if spec.title:
            g.fig.suptitle(spec.title)
        if spec.xlim:
            g.set(xlim=spec.xlim)
        if spec.ylim:
            g.set(ylim=spec.ylim)
        if spec.xlabel:
            g.set_xlabels(spec.xlabel)
        if spec.ylabel:
            g.set_ylabels(spec.ylabel)
        if spec.no_legend and g._legend is not None:
            g._legend.remove()
            g._legend = None
        return g.fig

    # --- helpers ---

    def _apply_theme(self, spec: BaseSpec) -> None:
        sns.set_theme(style=spec.theme, palette=spec.palette or "tab10")
        if spec.colors:
            sns.set_palette(spec.colors)

    def _new_figure(self, spec: BaseSpec):
        w_px = spec.width_px or DEFAULT_WIDTH_PX
        h_px = spec.height_px or DEFAULT_HEIGHT_PX
        fig, ax = plt.subplots(figsize=(w_px / DEFAULT_DPI, h_px / DEFAULT_DPI))
        return fig, ax

    def _finalize(self, fig: Figure, ax, spec: BaseSpec) -> None:
        if spec.title:
            ax.set_title(spec.title)
        if spec.xlabel:
            ax.set_xlabel(spec.xlabel)
        if spec.ylabel:
            ax.set_ylabel(spec.ylabel)
        if spec.xlim:
            ax.set_xlim(spec.xlim)
        if spec.ylim:
            ax.set_ylim(spec.ylim)
        if spec.no_legend and ax.get_legend() is not None:
            ax.get_legend().remove()
        fig.tight_layout()

    def _draw_stacked_bar(self, ax, df: pd.DataFrame, spec: BarSpec) -> None:
        pivot = df.pivot_table(
            index=spec.xvar, columns=spec.colorvar, values=spec.yvar, aggfunc="sum"
        ).fillna(0)
        if spec.normalized:
            pivot = pivot.div(pivot.sum(axis=1), axis=0) * 100.0
        kind = "barh" if spec.horizontal else "bar"
        pivot.plot(kind=kind, stacked=True, ax=ax, color=spec.colors)

    def _bar_order(self, df: pd.DataFrame, spec: BarSpec) -> list | None:
        """Compute category ordering for sns.barplot's order= from spec.sort."""
        if not spec.sort:
            return None
        reverse = spec.sort.startswith("-")
        key = spec.sort.lstrip("-")
        if key == "x":
            return sorted(df[spec.xvar].unique(), reverse=reverse)
        if key == "y":
            agg = df.groupby(spec.xvar)[spec.yvar].sum().sort_values(ascending=not reverse)
            return list(agg.index)
        return None
