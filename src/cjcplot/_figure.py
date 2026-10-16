"""Shared figure helpers used by every plot function.

Figure creation sized to a LaTeX text width, tick configuration, the final axis
formatting step, and the helpers that bring per-trace options to the number of
traces. Plot modules import from here instead of keeping their own copies.
"""

from __future__ import annotations

from typing import Optional, Sequence, TypeVar

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.ticker import AutoMinorLocator
import numpy as np
from numpy.typing import ArrayLike

# LaTeX points per inch, used to convert a text width in pt to inches.
POINTS_PER_INCH = 72.27

T = TypeVar("T")


def create_figure_and_axes(
    fig_textwidth_pt: float,
    fig_aspect_ratio: tuple[float, float],
) -> tuple[Figure, Axes]:
    """Create a figure sized as (width, height) fractions of the LaTeX text width.

    The "compressed" layout works like "constrained" (labels and colorbars kept
    inside the figure), but also shrinks plots with a fixed aspect such as
    ``aspect="equal"`` until they fit, instead of letting labels fall off the edge.
    """
    fig_width_in = fig_aspect_ratio[0] * fig_textwidth_pt / POINTS_PER_INCH
    fig_height_in = fig_aspect_ratio[1] * fig_textwidth_pt / POINTS_PER_INCH
    fig, ax = plt.subplots(figsize=(fig_width_in, fig_height_in), layout="compressed")
    return fig, ax


def configure_ticks(
    ax: Axes,
    minor_tick_count: int,
    xticks_pos: Optional[Sequence[float]],
    xticks_labels: Optional[Sequence[str]],
    yticks_pos: Optional[Sequence[float]],
    yticks_labels: Optional[Sequence[str]],
) -> None:
    """Apply explicit major ticks (if given) and minor ticks on both axes."""
    # Explicit major ticks per axis, with labels that must match them one to one.
    for axis, positions, labels, name in (
        (ax.xaxis, xticks_pos, xticks_labels, "xticks"),
        (ax.yaxis, yticks_pos, yticks_labels, "yticks"),
    ):
        if positions is not None:
            axis.set_ticks(positions)
            if labels is not None:
                if len(positions) != len(labels):
                    raise ValueError(f"{name}_pos and {name}_labels lengths must match.")
                axis.set_ticklabels(labels)
        axis.set_minor_locator(AutoMinorLocator(n=minor_tick_count + 1))


def finalize_axes(
    fig: Figure,
    ax: Axes,
    *,
    xlim: Optional[Sequence[float]],
    ylim: Optional[Sequence[float]],
    xlabel: str,
    ylabel: str,
    title: str,
    grid_show: bool,
    save_path: Optional[str],
    fig_show: bool,
    logx: bool,
    logy: bool,
    legend_show: bool = False,
    legend_loc: str = "best",
    legend_ncols: int = 1,
    legend_reverse: bool = False,
) -> None:
    """Apply shared axis formatting, the legend, and the optional save/show actions."""
    # Log scales first, so limits are interpreted on the final scale.
    if logx:
        ax.set_xscale("log")
    if logy:
        ax.set_yscale("log")
    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)

    # Labels and title; their font sizes come from the active style.
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)

    # Legend only when something on the axes carries a label.
    if legend_show:
        handles, labels = ax.get_legend_handles_labels()
        if handles:
            if legend_reverse:
                handles, labels = handles[::-1], labels[::-1]
            ax.legend(handles, labels, frameon=False, loc=legend_loc, ncol=legend_ncols)

    if grid_show:
        ax.grid()

    # Save this figure (not whatever pyplot considers current); dpi comes from the style.
    if save_path:
        fig.savefig(save_path)
    if fig_show:
        plt.show()


def is_trace_sequence(data: object) -> bool:
    """Return True if ``data`` is a sequence of traces rather than a single trace."""
    if isinstance(data, np.ndarray):
        return False
    if not isinstance(data, Sequence) or isinstance(data, (str, bytes)):
        return False
    if len(data) == 0:
        return False
    # The first non-None element decides; an all-None list is a per-trace list.
    first = next((item for item in data if item is not None), None)
    if first is None:
        return True
    return isinstance(first, (Sequence, np.ndarray)) and not isinstance(first, (str, bytes))


def as_trace_list(
    data: Optional[ArrayLike | Sequence[ArrayLike]],
    name: str,
    trace_count: int,
) -> Optional[list[Optional[np.ndarray]]]:
    """Convert one trace or a list of traces to arrays, checking the trace count.

    A single trace is broadcast to all traces when ``trace_count`` > 1, so one
    error array can serve several traces. ``None`` entries are kept as ``None``.
    """
    if data is None:
        return None
    traces = list(data) if is_trace_sequence(data) else [data] * trace_count
    if len(traces) != trace_count:
        raise ValueError(f"You provided {len(traces)} {name} traces, but expected {trace_count}.")
    return [None if trace is None else np.asarray(trace) for trace in traces]


def cycle_to_length(values: Sequence[T], length: int, name: str) -> list[T]:
    """Repeat ``values`` from the start until there are ``length`` of them (used for colours)."""
    values_list = list(values)
    if not values_list:
        raise ValueError(f"{name} must contain at least one value.")
    repeats = -(-length // len(values_list))
    return (values_list * repeats)[:length]


def pad_to_length(values: Optional[Sequence[T]], length: int, default: T) -> list[T]:
    """Fill missing entries with ``default`` (``None`` means all default)."""
    values_list = [] if values is None else list(values)
    return values_list[:length] + [default] * (length - len(values_list))


def broadcast_to_length(value: T | Sequence[T], length: int, name: str) -> list[T]:
    """Broadcast a single value, or extend a sequence by repeating its last entry."""
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return [value] * length
    values_list = list(value)
    if not values_list:
        raise ValueError(f"{name} must contain at least one value when given as a sequence.")
    return values_list[:length] + [values_list[-1]] * (length - len(values_list))


def stacking_offset(index: int, count: int, first_on_top: bool) -> float:
    """Small zorder offset that stacks traces without changing their draw order.

    Added to an element's base zorder (line, marker, error bar); it stays below
    0.1 so traces never cross into another element type's layer.
    """
    rank = count - index if first_on_top else index + 1
    return 0.09 * rank / (count + 1)
