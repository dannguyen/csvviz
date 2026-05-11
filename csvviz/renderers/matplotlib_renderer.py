from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure

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
        fig, ax = self._new_figure(spec)

        x, y = (spec.yvar, spec.xvar) if spec.horizontal else (spec.xvar, spec.yvar)

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
                orient="h" if spec.horizontal else "v",
            )
        else:
            sns.barplot(
                data=df,
                x=x,
                y=y,
                ax=ax,
                color=(spec.colors[0] if spec.colors else None),
                orient="h" if spec.horizontal else "v",
            )

        if spec.sort:
            self._apply_bar_sort(ax, spec)

        self._finalize(fig, ax, spec)
        return fig

    def render_line(self, spec: LineSpec, df: pd.DataFrame) -> Figure:
        self._apply_theme(spec)
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
        raise NotImplementedError

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

    def _apply_bar_sort(self, ax, spec: BarSpec) -> None:
        reverse = spec.sort.startswith("-")
        key = spec.sort.lstrip("-")
        if key not in ("x", "y"):
            return
        labels = [t.get_text() for t in ax.get_xticklabels()]
        heights = [p.get_height() for p in ax.patches[: len(labels)]]
        order = sorted(
            range(len(labels)),
            key=lambda i: heights[i],
            reverse=reverse if key == "y" else not reverse,
        )
        ax.set_xticks(range(len(order)))
        ax.set_xticklabels([labels[i] for i in order])
