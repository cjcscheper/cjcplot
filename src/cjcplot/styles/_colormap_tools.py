"""Tools for building and registering colormaps, shared by all style folders."""

from __future__ import annotations

from typing import Sequence

import matplotlib
from matplotlib.colors import Colormap, LinearSegmentedColormap, ListedColormap
import numpy as np


def truncate_colormap(base_name: str, start: float, stop: float, name: str, color_count: int = 256) -> ListedColormap:
    """Return the ``start``..``stop`` slice (fractions 0..1) of an existing colormap.

    ``start > stop`` runs the slice in reverse. Typical uses: trimming the
    near-white end of a sequential map, so its faintest colour still reads as a
    colour and not as missing data, or keeping only the part of a diverging map
    that a plot's data range actually reaches.

    Example: ``truncate_colormap("Reds", 0.15, 1.0, "reds_cjc")``.
    """
    base = matplotlib.colormaps[base_name]
    return ListedColormap(base(np.linspace(start, stop, color_count)), name=name)


def colormap_from_colors(colors: Sequence, name: str, color_count: int = 256) -> LinearSegmentedColormap:
    """Return a colormap that runs smoothly through ``colors`` (equally spaced), low to high.

    Example: ``colormap_from_colors(["#E0E0E0", "#CB181D", "#67000D"], "my_reds")``.
    """
    return LinearSegmentedColormap.from_list(name, list(colors), N=color_count)


def join_colormaps(low: Colormap, high: Colormap, name: str, color_count: int = 256) -> ListedColormap:
    """Return ``low`` followed by ``high`` as one colormap, each taking half of the range.

    Used to build a diverging map from two single-hue arms that meet in the middle.
    """
    half_count = color_count // 2
    samples = np.linspace(0.0, 1.0, half_count)
    return ListedColormap(np.vstack((low(samples), high(samples))), name=name)


def colors_from_cmap(cmap: str | Colormap, count: int) -> list[str]:
    """Return ``count`` evenly spaced colours of a colormap, as hex strings.

    The first colour is the colormap's left (low) end and the last its right
    (high) end, so a series of line traces runs through the whole map. Pass the
    result as ``colors=`` to :func:`cjcplot.plot_1d`.

    Example: ``plot_1d(x_traces, y_traces, colors=colors_from_cmap("blueyellow_cjc", 5))``.
    """
    if count < 1:
        raise ValueError("count must be at least 1.")
    colormap = matplotlib.colormaps.get_cmap(cmap)
    positions = np.linspace(0.0, 1.0, count) if count > 1 else np.array([0.0])
    return [matplotlib.colors.to_hex(color) for color in colormap(positions)]


def register_colormap(cmap: Colormap) -> None:
    """Register ``cmap`` and its reversed version (``<name>_r``) with matplotlib.

    After registering, the colormap works by name everywhere, also outside
    cjcplot, e.g. ``plt.pcolormesh(..., cmap="reds_cjc")``. Registering again
    (for example when a style is re-applied) replaces the earlier version.
    """
    # Unregister an earlier version first; force=True alone warns on every re-apply.
    for colormap in (cmap, cmap.reversed()):
        if colormap.name in matplotlib.colormaps:
            matplotlib.colormaps.unregister(colormap.name)
        matplotlib.colormaps.register(colormap)
