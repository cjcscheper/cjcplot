"""Shared figure helpers used by every plot function.

Figure creation sized to a LaTeX text width, tick configuration, the final axis
formatting step, and the helpers that bring per-trace options to the number of
traces. Plot modules import from here instead of keeping their own copies.
"""

from __future__ import annotations

from typing import Any, Literal, Optional, Sequence, TypeVar

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.ticker import AutoMinorLocator
import numpy as np
from numpy.typing import ArrayLike

# Points per inch, used to convert fig_textwidth_pt to inches. 72.27 is the TeX
# point of LaTeX's \the\textwidth. For figures that are not used in LaTeX, e.g.
# Word or PowerPoint (72 points per inch), it can be changed from a script with
#     import cjcplot._figure
#     cjcplot._figure.POINTS_PER_INCH = 72.0
# All plot functions share this one value, so the change applies to every figure
# created after it in that script, while figures created before it keep the old
# size; set it once at the top of the script, before any plot.
POINTS_PER_INCH = 72.27

T = TypeVar("T")

# Legend positions matplotlib accepts by name; listing them gives autocomplete in editors.
LegendLocation = Literal[
    "best", "upper right", "upper left", "lower left", "lower right", "right",
    "center left", "center right", "lower center", "upper center", "center",
]


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
    legend_loc: LegendLocation = "best",
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
        x_min, x_max = xlim
        ax.set_xlim(x_min, x_max)
    if ylim is not None:
        y_min, y_max = ylim
        ax.set_ylim(y_min, y_max)

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


# --- Per-trace options -------------------------------------------------------
# Plot functions accept options either once for all traces or as a list with one
# entry per trace, and such a list may be shorter than the number of traces. The
# three helpers below turn every option into a list with exactly one entry per
# trace, each with its own rule for filling up a short list:
#   cycle_to_length      repeat the whole list         (colours)
#   pad_to_length        fill with a fixed default     (labels, line styles)
#   broadcast_to_length  repeat the last entry         (on/off flags, alpha, widths)


def cycle_to_length(values: Sequence[T], length: int, name: str) -> list[T]:
    """Repeat ``values`` from the start until there are ``length`` of them.

    Used for colours: with more traces than colours, the colours start over, so
    every trace still gets a palette colour.

    Examples: ``(["red", "blue"], 3)`` -> ``["red", "blue", "red"]``;
    ``(["red", "blue", "green"], 2)`` -> ``["red", "blue"]``.

    ``name`` is only used in the error message for an empty list.
    """
    values_list = list(values)
    if not values_list:
        raise ValueError(f"{name} must contain at least one value.")
    # Enough whole repeats to cover `length` (rounded up), then cut to size.
    repeats = -(-length // len(values_list))
    return (values_list * repeats)[:length]


def pad_to_length(values: Optional[Sequence[T]], length: int, default: T) -> list[T]:
    """Fill missing entries with ``default`` until there are ``length`` of them.

    Used where a missing entry has an obvious neutral value: no legend label
    (``""``), a solid line (``"-"``), grey error bars. ``None`` means "nothing
    given", so every entry gets the default.

    Examples: ``(["a"], 3, "")`` -> ``["a", "", ""]``;
    ``(None, 2, "-")`` -> ``["-", "-"]``;
    ``(["a", "b", "c"], 2, "")`` -> ``["a", "b"]`` (extra entries are dropped).
    """
    values_list = [] if values is None else list(values)
    return values_list[:length] + [default] * (length - len(values_list))


# Typed as Any: a string is itself a sequence, so "T | Sequence[T]" would be
# ambiguous for string options such as histtype and confuse type checkers.
def broadcast_to_length(value: Any, length: int, name: str) -> list[Any]:
    """Give every trace a value: one value for all, or a list extended with its last entry.

    Used for on/off switches and style numbers (``line_show``, ``fill``,
    ``alpha``, ``linewidth``), where "the rest like the last one" is the
    natural reading of a short list.

    Examples: ``(True, 3)`` -> ``[True, True, True]``;
    ``([True, False], 4)`` -> ``[True, False, False, False]``;
    ``(0.8, 2)`` -> ``[0.8, 0.8]``.

    A string counts as one value, not as a list of characters, so
    ``("step", 2)`` -> ``["step", "step"]``. ``name`` is only used in the error
    message for an empty list.
    """
    # A single value (including a string) is copied to every trace.
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return [value] * length
    values_list = list(value)
    if not values_list:
        raise ValueError(f"{name} must contain at least one value when given as a sequence.")
    # A short list is extended with its last entry; a long one is cut to size.
    return values_list[:length] + [values_list[-1]] * (length - len(values_list))


def stacking_offset(index: int, count: int, first_on_top: bool) -> float:
    """Small zorder offset that decides which trace lies on top of which.

    matplotlib draws elements with a higher zorder on top. Each element type has
    a base zorder (error bars 0.9, lines 1.0, markers 3.0, raised error bars
    4.0); this offset (always below 0.1) is added to it per trace. That way the
    traces stack in the wanted order, while every line still stays below every
    marker, and the traces can be drawn in their given order, so the legend
    lists them in the order of ``legend_labels``.

    ``first_on_top=True`` gives the first trace the largest offset (on top);
    ``False`` gives it to the last trace.

    Example for three traces with ``first_on_top=True``: offsets 0.0675,
    0.045, 0.0225 for traces 0, 1, 2.
    """
    # Rank 1..count: the trace with the highest rank ends up on top.
    rank = count - index if first_on_top else index + 1
    return 0.09 * rank / (count + 1)
