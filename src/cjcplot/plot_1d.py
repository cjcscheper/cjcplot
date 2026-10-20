"""1D plots: line/scatter traces with error bars, and histograms.

Both functions accept a single trace or a list of traces, size the figure as a
fraction of the LaTeX text width, and return ``(fig, ax)`` for further edits.
Colours default to the active style's palette (see :func:`cjcplot.style_colors`).
"""

from __future__ import annotations

from typing import Literal, Optional, Sequence

from matplotlib.axes import Axes
from matplotlib.figure import Figure
import numpy as np
from numpy.typing import ArrayLike

from cjcplot._figure import (
    LegendLocation,
    as_trace_list,
    broadcast_to_length,
    configure_ticks,
    create_figure_and_axes,
    cycle_to_length,
    finalize_axes,
    is_trace_sequence,
    pad_to_length,
    stacking_offset,
)
from cjcplot.styles import style_colors

# Histogram drawing styles matplotlib accepts; listing them gives autocomplete in editors.
HistogramType = Literal["bar", "barstacked", "step", "stepfilled"]


def plot_1d(
    x_data: ArrayLike | Sequence[ArrayLike],
    y_data: ArrayLike | Sequence[ArrayLike],
    xerr_data: Optional[ArrayLike | Sequence[ArrayLike]] = None,
    yerr_data: Optional[ArrayLike | Sequence[ArrayLike]] = None,
    colors: Optional[Sequence[str]] = None,
    line_show: bool | Sequence[bool] = True,
    line_styles: Optional[Sequence[str]] = None,
    scatter_show: bool | Sequence[bool] = False,
    scatter_colors: Optional[Sequence[str]] = None,
    yerr_show: bool | Sequence[bool] = True,
    xlim: Optional[Sequence[float]] = None,
    ylim: Optional[Sequence[float]] = None,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    legend_show: bool = True,
    legend_labels: Optional[Sequence[str]] = None,
    legend_loc: LegendLocation = "best",
    legend_ncols: int = 1,
    legend_reverse: bool = False,
    save_path: Optional[str] = None,
    grid_show: bool = False,
    fig_show: bool = True,
    fig_textwidth_pt: float = 497.0,
    fig_aspect_ratio: tuple[float, float] = (0.5, 0.5),
    minor_tick_count: int = 1,
    xticks_pos: Optional[Sequence[float]] = None,
    xticks_labels: Optional[Sequence[str]] = None,
    yticks_pos: Optional[Sequence[float]] = None,
    yticks_labels: Optional[Sequence[str]] = None,
    vlines_pos: Optional[Sequence[float]] = None,
    vlines_colors: Optional[Sequence[str]] = None,
    vlines_styles: Optional[Sequence[str]] = None,
    vlines_labels: Optional[Sequence[str]] = None,
    hlines_pos: Optional[Sequence[float]] = None,
    hlines_colors: Optional[Sequence[str]] = None,
    hlines_styles: Optional[Sequence[str]] = None,
    hlines_labels: Optional[Sequence[str]] = None,
    err_colors: Optional[Sequence[str]] = None,
    err_linewidth: float = 1.0,
    err_on_top: bool = False,
    logx: bool = False,
    logy: bool = False,
    first_on_top: bool = True,
    ax: Optional[Axes] = None,
) -> tuple[Figure, Axes]:
    """Plot one or more 1D traces (time traces, spectra, fit results) with error bars.

    Parameters
    ----------
    x_data, y_data : array-like or sequence[array-like]
        X- and y-values. Give a single trace or a list of traces of equal shapes.
    xerr_data, yerr_data : array-like or sequence[array-like], optional
        Standard-deviation error bars. One array per trace, or a single array
        that is used for every trace. ``None`` entries skip that trace.
    colors : sequence[str], optional
        Line colours, cycled when shorter than the number of traces.
        Default: the active style's palette (:func:`cjcplot.style_colors`).
    line_show, scatter_show : bool or sequence[bool]
        Draw lines and/or scatter markers. One flag for all traces, or one per
        trace (a shorter list repeats its last flag).
    line_styles : sequence[str], optional
        Line style per trace (e.g. ``'-'``, ``'--'``); missing entries are ``'-'``.
    scatter_colors : sequence[str], optional
        Marker fill colours; missing entries are white.
    yerr_show : bool or sequence[bool], default True
        Show the y error bars, overall or per trace.
    xlim, ylim : (min, max), optional
        Axis limits.
    xlabel, ylabel, title : str
        Axis labels and title.
    legend_show : bool, default True
        Draw a legend when at least one trace or reference line has a label.
    legend_labels : sequence[str], optional
        Legend label per trace; missing, empty or None labels are left out, e.g.
        ``["first", None, None, "last"]`` labels only the first and last trace.
    legend_loc : str, default "best"
        Legend position: "best", "upper right", "upper left", "lower left",
        "lower right", "right", "center left", "center right", "lower center",
        "upper center" or "center".
    legend_ncols : int, default 1
        Number of legend columns.
    legend_reverse : bool, default False
        Reverse the order of the legend entries.
    save_path : str, optional
        Save the figure to this path (dpi from the style).
    grid_show : bool, default False
        Show grid lines.
    fig_show : bool, default True
        Call ``plt.show()`` at the end. Ignored when ``ax`` is given.
    fig_textwidth_pt : float, default 497.0
        LaTeX text width in points (print it with ``\\the\\textwidth`` in LaTeX).
    fig_aspect_ratio : (float, float), default (0.5, 0.5)
        Figure (width, height) as fractions of ``fig_textwidth_pt``; include it
        in LaTeX at ``width=<width>\\textwidth`` so fonts keep their true size.
    minor_tick_count : int, default 1
        Number of minor ticks between major ticks.
    xticks_pos, yticks_pos : sequence[float], optional
        Explicit major tick positions.
    xticks_labels, yticks_labels : sequence[str], optional
        Labels for the explicit tick positions.
    vlines_pos, hlines_pos : sequence[float], optional
        Positions of vertical / horizontal reference lines.
    vlines_colors, hlines_colors : sequence[str], optional
        Reference line colours (default gray).
    vlines_styles, hlines_styles : sequence[str], optional
        Reference line styles (default ``'--'``).
    vlines_labels, hlines_labels : sequence[str], optional
        Legend labels for the reference lines (default none).
    err_colors : sequence[str], optional
        Error bar colour per trace (default gray).
    err_linewidth : float, default 1.0
        Error bar line width.
    err_on_top : bool, default False
        Draw the error bars on top of lines and markers instead of behind them.
    logx, logy : bool, default False
        Logarithmic axes.
    first_on_top : bool, default True
        Put the first trace on top of the others. The legend always lists
        the traces in the order given.
    ax : matplotlib.axes.Axes, optional
        Existing axes to draw into. Then no new figure is created and
        ``fig_show``, ``fig_textwidth_pt`` and ``fig_aspect_ratio`` are ignored.

    Returns
    -------
    (Figure, Axes)
    """
    # Create a new figure, or draw into the axes provided by the caller.
    ax_provided = ax is not None
    if ax_provided:
        fig = ax.get_figure()
    else:
        fig, ax = create_figure_and_axes(fig_textwidth_pt, fig_aspect_ratio)
    configure_ticks(ax, minor_tick_count, xticks_pos, xticks_labels, yticks_pos, yticks_labels)

    # x and y must both be one trace or both be lists of traces.
    if is_trace_sequence(x_data) != is_trace_sequence(y_data):
        raise ValueError("x_data and y_data must both be a single trace or both be sequences of traces.")
    x_traces = list(x_data) if is_trace_sequence(x_data) else [x_data]
    y_traces = list(y_data) if is_trace_sequence(y_data) else [y_data]
    if len(x_traces) != len(y_traces):
        raise ValueError(
            f"You provided {len(x_traces)} x-traces and {len(y_traces)} y-traces; they must match."
        )
    trace_count = len(x_traces)

    # Each x/y pair must have the same shape.
    x_arrays = [np.asarray(trace) for trace in x_traces]
    y_arrays = [np.asarray(trace) for trace in y_traces]
    for i, (x_array, y_array) in enumerate(zip(x_arrays, y_arrays)):
        if x_array.shape != y_array.shape:
            raise ValueError(f"Trace {i} mismatch: x has shape {x_array.shape}, y has shape {y_array.shape}.")

    # Error arrays must match their trace; hidden y errors are not checked.
    yerr_show_flags = broadcast_to_length(yerr_show, trace_count, "yerr_show")
    xerr_arrays = as_trace_list(xerr_data, "xerr_data", trace_count)
    yerr_arrays = as_trace_list(yerr_data, "yerr_data", trace_count)
    for name, err_arrays, ref_arrays, show_flags in (
        ("xerr_data", xerr_arrays, x_arrays, [True] * trace_count),
        ("yerr_data", yerr_arrays, y_arrays, yerr_show_flags),
    ):
        if err_arrays is None:
            continue
        for i, (err_array, ref_array) in enumerate(zip(err_arrays, ref_arrays)):
            if err_array is not None and show_flags[i] and err_array.shape != ref_array.shape:
                raise ValueError(
                    f"{name} trace {i} mismatch: data has shape {ref_array.shape}, "
                    f"error has shape {err_array.shape}."
                )

    # Per-trace styling, filled up to the number of traces.
    colors = cycle_to_length(style_colors() if colors is None else colors, trace_count, "colors")
    line_show_flags = broadcast_to_length(line_show, trace_count, "line_show")
    scatter_show_flags = broadcast_to_length(scatter_show, trace_count, "scatter_show")
    scatter_colors = pad_to_length(scatter_colors, trace_count, "white")
    legend_labels = pad_to_length(legend_labels, trace_count, "")
    line_styles = pad_to_length(line_styles, trace_count, "-")
    err_colors = pad_to_length(err_colors, trace_count, "gray")

    # Draw in the given order, so the legend follows legend_labels; first_on_top
    # only lifts each trace's zorder slightly within its element type.
    for i in range(trace_count):
        if not line_show_flags[i] and not scatter_show_flags[i]:
            continue
        layer = stacking_offset(i, trace_count, first_on_top)

        # The legend entry goes on the markers when present, otherwise on the line.
        if line_show_flags[i]:
            ax.plot(
                x_arrays[i], y_arrays[i],
                label=None if scatter_show_flags[i] else legend_labels[i],
                color=colors[i],
                linestyle=line_styles[i],
                zorder=1.0 + layer,
            )
        if scatter_show_flags[i]:
            ax.scatter(
                x_arrays[i], y_arrays[i],
                label=legend_labels[i],
                edgecolor=colors[i],
                color=scatter_colors[i],
                s=30, linewidth=1.5,
                zorder=3.0 + layer,
            )

        # Error bars sit just behind the line, or above everything with err_on_top.
        yerr_i = yerr_arrays[i] if (yerr_arrays is not None and yerr_show_flags[i]) else None
        xerr_i = None if xerr_arrays is None else xerr_arrays[i]
        if xerr_i is not None or yerr_i is not None:
            ax.errorbar(
                x_arrays[i], y_arrays[i],
                xerr=xerr_i, yerr=yerr_i,
                fmt="none",
                ecolor=err_colors[i],
                elinewidth=err_linewidth,
                barsabove=err_on_top,
                capsize=3,
                zorder=(4.0 if err_on_top else 0.9) + layer,
            )

    # Vertical and horizontal reference lines behind the data.
    for positions, line_colors, styles, labels, draw_line in (
        (vlines_pos, vlines_colors, vlines_styles, vlines_labels, ax.axvline),
        (hlines_pos, hlines_colors, hlines_styles, hlines_labels, ax.axhline),
    ):
        if positions is None:
            continue
        count = len(positions)
        for pos, color, style, label in zip(
            positions,
            pad_to_length(line_colors, count, "gray"),
            pad_to_length(styles, count, "--"),
            pad_to_length(labels, count, ""),
        ):
            draw_line(pos, color=color, linestyle=style, label=label or None, linewidth=1.0, zorder=0.5)

    finalize_axes(
        fig, ax,
        xlim=xlim, ylim=ylim,
        xlabel=xlabel, ylabel=ylabel, title=title,
        grid_show=grid_show,
        save_path=save_path,
        fig_show=fig_show and not ax_provided,
        logx=logx, logy=logy,
        legend_show=legend_show,
        legend_loc=legend_loc,
        legend_ncols=legend_ncols,
        legend_reverse=legend_reverse,
    )
    return fig, ax


def plot_histogram_1d(
    data: ArrayLike | Sequence[ArrayLike],
    bins: int | Sequence[float] | str = 10,
    bin_range: Optional[tuple[float, float]] = None,
    density: bool = False,
    weights: Optional[ArrayLike | Sequence[ArrayLike]] = None,
    histtype: HistogramType | Sequence[HistogramType] = "step",
    fill: bool | Sequence[bool] = True,
    hatch: Optional[str | Sequence[Optional[str]]] = None,
    alpha: float | Sequence[float] = 0.8,
    edgecolor: Optional[str | Sequence[str]] = None,
    linewidth: float | Sequence[float] = 1.5,
    colors: Optional[Sequence[str]] = None,
    xlim: Optional[Sequence[float]] = None,
    ylim: Optional[Sequence[float]] = None,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    legend_show: bool = True,
    legend_labels: Optional[Sequence[str]] = None,
    legend_loc: LegendLocation = "best",
    legend_ncols: int = 1,
    legend_reverse: bool = False,
    save_path: Optional[str] = None,
    grid_show: bool = False,
    fig_show: bool = True,
    fig_textwidth_pt: float = 497.0,
    fig_aspect_ratio: tuple[float, float] = (0.5, 0.5),
    minor_tick_count: int = 1,
    xticks_pos: Optional[Sequence[float]] = None,
    xticks_labels: Optional[Sequence[str]] = None,
    yticks_pos: Optional[Sequence[float]] = None,
    yticks_labels: Optional[Sequence[str]] = None,
    logx: bool = False,
    logy: bool = False,
    first_on_top: bool = True,
    ax: Optional[Axes] = None,
) -> tuple[Figure, Axes]:
    """Plot one or more histograms of sample values (fit spreads, residuals, MC outputs).

    For paired x/y traces use :func:`plot_1d` instead.

    Parameters
    ----------
    data : array-like or sequence[array-like]
        Sample values: one array, or a list of arrays for overlaid histograms.
    bins : int, sequence[float] or str, default 10
        Number of bins, explicit bin edges, or a NumPy strategy such as ``"auto"``.
        Overlaid histograms always share the same bin edges.
    bin_range : (min, max), optional
        Range covered by the bins; samples outside it are ignored.
    density : bool, default False
        Normalise each histogram to unit area, so the y-axis is a probability
        density (per unit of x). Use it to compare datasets of different sizes.
    weights : array-like or sequence[array-like], optional
        Weight per sample instead of 1 (e.g. ``1/N`` for fractions). One array
        per dataset, matching its shape.
    histtype : str or sequence[str], default "step"
        ``"step"``, ``"bar"``, ``"barstacked"`` or ``"stepfilled"``, per dataset.
    fill : bool or sequence[bool], default True
        Fill the area of ``"step"`` histograms with their colour (switches them
        to ``"stepfilled"``). ``fill=False`` draws only the coloured outline.
    hatch : str or sequence[str | None], optional
        Hatch pattern(s) such as ``"/"``, ``"//"``, ``"x"``; visible on filled styles.
    alpha : float or sequence[float], default 0.8
        Opacity per dataset.
    edgecolor : str or sequence[str], optional
        Edge colour per dataset.
    linewidth : float or sequence[float], default 1.5
        Edge/line width per dataset.
    colors : sequence[str], optional
        Colour per dataset, cycled. Default: the active style's palette.
    xlim, ylim, xlabel, ylabel, title, legend_*, save_path, grid_show, fig_show,
    fig_textwidth_pt, fig_aspect_ratio, minor_tick_count, xticks_*, yticks_*,
    logx, logy, first_on_top, ax
        As in :func:`plot_1d`.

    Returns
    -------
    (Figure, Axes)

    Examples
    --------
    ``plot_histogram_1d(samples, bins=60, density=True)`` for filled bins (default).
    ``plot_histogram_1d(samples, bins=60, fill=False, alpha=1.0)`` for outline-only bins.
    ``plot_histogram_1d(samples, bins=40, fill=True, hatch="//")`` for striped fills.
    """
    # Create a new figure, or draw into the axes provided by the caller.
    ax_provided = ax is not None
    if ax_provided:
        fig = ax.get_figure()
    else:
        fig, ax = create_figure_and_axes(fig_textwidth_pt, fig_aspect_ratio)
    configure_ticks(ax, minor_tick_count, xticks_pos, xticks_labels, yticks_pos, yticks_labels)

    datasets = list(data) if is_trace_sequence(data) else [data]
    data_arrays = [np.asarray(dataset) for dataset in datasets]
    dataset_count = len(data_arrays)

    # Overlaid histograms share one set of bin edges so their bins line up.
    histogram_bins: int | Sequence[float] | str | np.ndarray = bins
    bins_are_edges = isinstance(bins, Sequence) and not isinstance(bins, (str, bytes))
    if dataset_count > 1 and not bins_are_edges:
        finite_values = [arr[np.isfinite(arr)] for arr in data_arrays]
        finite_values = [arr for arr in finite_values if arr.size > 0]
        if finite_values:
            histogram_bins = np.histogram_bin_edges(np.concatenate(finite_values), bins=bins, range=bin_range)

    # Weights must match their dataset sample by sample.
    weights_arrays = as_trace_list(weights, "weights", dataset_count)
    if weights_arrays is not None:
        for i, (values, w) in enumerate(zip(data_arrays, weights_arrays)):
            if w is not None and values.shape != w.shape:
                raise ValueError(
                    f"weights trace {i} mismatch: data has shape {values.shape}, weights has shape {w.shape}."
                )

    # Per-dataset styling, filled up to the number of datasets.
    colors = cycle_to_length(style_colors() if colors is None else colors, dataset_count, "colors")
    legend_labels = pad_to_length(legend_labels, dataset_count, "")
    histtype_list: list[HistogramType] = broadcast_to_length(histtype, dataset_count, "histtype")
    fill_list = broadcast_to_length(fill, dataset_count, "fill")
    hatch_list = broadcast_to_length(hatch, dataset_count, "hatch")
    alpha_list = broadcast_to_length(alpha, dataset_count, "alpha")
    edgecolor_list = broadcast_to_length(edgecolor, dataset_count, "edgecolor")
    linewidth_list = broadcast_to_length(linewidth, dataset_count, "linewidth")

    # Draw in the given order, so the legend follows legend_labels; first_on_top
    # only sets which histogram lies on top through its zorder.
    for i in range(dataset_count):
        histtype_i: HistogramType = "stepfilled" if (fill_list[i] and histtype_list[i] == "step") else histtype_list[i]
        _, _, patches = ax.hist(
            data_arrays[i],
            bins=histogram_bins,
            range=bin_range,
            density=density,
            weights=None if weights_arrays is None else weights_arrays[i],
            histtype=histtype_i,
            alpha=float(alpha_list[i]),
            edgecolor=edgecolor_list[i],
            linewidth=float(linewidth_list[i]),
            color=colors[i],
            label=legend_labels[i],
            zorder=1.0 + stacking_offset(i, dataset_count, first_on_top),
        )

        # Hatching is set on the drawn patches, as hist() takes one pattern only.
        if hatch_list[i] is not None:
            for patch in patches:
                patch.set_hatch(str(hatch_list[i]))

    finalize_axes(
        fig, ax,
        xlim=xlim, ylim=ylim,
        xlabel=xlabel, ylabel=ylabel, title=title,
        grid_show=grid_show,
        save_path=save_path,
        fig_show=fig_show and not ax_provided,
        logx=logx, logy=logy,
        legend_show=legend_show,
        legend_loc=legend_loc,
        legend_ncols=legend_ncols,
        legend_reverse=legend_reverse,
    )
    return fig, ax
