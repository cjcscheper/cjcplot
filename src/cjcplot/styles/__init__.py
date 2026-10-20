"""Switchable plot styles.

Each style is a folder in this directory::

    styles/<name>/
        <name>.mplstyle   fonts, ticks, dpi, line widths (matplotlib settings)
        colors.py         optional: line palette and colormaps (see cjc/colors.py)

Importing cjcplot applies the ``cjc`` style. Switch with ``use_style("<name>")``
for a bundled style, or pass the path to your own style folder or .mplstyle file.

Adding a style: copy the ``cjc`` folder, rename the folder and its .mplstyle to
the new name, and edit both files. ``available_styles()`` then lists it.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Optional, Union

from cycler import cycler
import matplotlib.pyplot as plt

from cjcplot.styles._colormap_tools import (
    colormap_from_colors,
    colors_from_colormap,
    join_colormaps,
    register_colormap,
    truncate_colormap,
)

STYLES_DIR = Path(__file__).resolve().parent

# Diverging colormap of the active style, used by plot_2d(cbar_symmetric=True).
_active_diverging_colormap = "RdBu_r"


def available_styles() -> list[str]:
    """Return the names of the bundled styles (folders containing ``<name>.mplstyle``)."""
    return sorted(
        folder.name for folder in STYLES_DIR.iterdir()
        if folder.is_dir() and (folder / f"{folder.name}.mplstyle").exists()
    )


def _load_colors_module(colors_path: Path) -> ModuleType:
    """Import a style's colors.py from its file path, so style folders need no package setup."""
    spec = importlib.util.spec_from_file_location(f"cjcplot_style_colors_{colors_path.parent.name}", colors_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def use_style(name_or_path: Union[str, Path]) -> None:
    """Apply a style: a bundled name, a style folder, or a single .mplstyle file.

    Matplotlib's settings are first reset to their defaults, so nothing of the
    previous style remains. For a style folder, its colors.py (if present) is
    then applied: colormaps are registered, ``PALETTE`` becomes the colour cycle
    and ``DEFAULT_COLORMAP`` the default heatmap colormap.

    Examples
    --------
    ``use_style("cjc")``, ``use_style("path/to/my_style")`` (a folder with
    ``my_style.mplstyle`` and optionally ``colors.py``), or
    ``use_style("path/to/my.mplstyle")`` (settings only, no colors.py).
    """
    global _active_diverging_colormap

    # Resolve the argument to an .mplstyle file and an optional colors.py.
    path = Path(name_or_path)
    colors_path: Optional[Path] = None
    if (STYLES_DIR / str(name_or_path)).is_dir():
        path = STYLES_DIR / str(name_or_path)
    if path.is_dir():
        mplstyle_path = path / f"{path.name}.mplstyle"
        colors_path = path / "colors.py"
    elif path.suffix == ".mplstyle":
        mplstyle_path = path
    else:
        raise ValueError(
            f"Unknown style {name_or_path!r}. Use one of {available_styles()}, "
            "a style folder, or an .mplstyle file."
        )
    if not mplstyle_path.exists():
        raise FileNotFoundError(f"Style file {mplstyle_path} not found.")

    # Load colours first, so colormaps exist before anything refers to them by name.
    colors = _load_colors_module(colors_path) if colors_path is not None and colors_path.exists() else None
    if colors is not None:
        for cmap in getattr(colors, "COLORMAPS", ()):
            register_colormap(cmap)

    # Reset to matplotlib defaults, then apply the style's settings.
    plt.style.use(["default", str(mplstyle_path)])

    # The style's colours override whatever the .mplstyle file set.
    _active_diverging_colormap = "RdBu_r"
    if colors is not None:
        if getattr(colors, "PALETTE", None):
            plt.rcParams["axes.prop_cycle"] = cycler(color=list(colors.PALETTE))
        if getattr(colors, "DEFAULT_COLORMAP", None):
            plt.rcParams["image.cmap"] = colors.DEFAULT_COLORMAP
        _active_diverging_colormap = getattr(colors, "DIVERGING_COLORMAP", _active_diverging_colormap)


def style_colors() -> list[str]:
    """Return the line colours of the active style, in order.

    These come from the colour cycle (``axes.prop_cycle``) that the active style
    set -- for the cjc style the ``PALETTE`` in ``styles/cjc/colors.py``. Use
    ``style_colors()[i]`` instead of hard-coding hex values, so a script follows
    the style when someone switches with :func:`use_style`.
    """
    return list(plt.rcParams["axes.prop_cycle"].by_key().get("color", []))


def style_diverging_colormap() -> str:
    """Return the diverging colormap of the active style (``RdBu_r`` unless the style sets one)."""
    return _active_diverging_colormap


__all__ = [
    "available_styles",
    "colormap_from_colors",
    "colors_from_colormap",
    "join_colormaps",
    "register_colormap",
    "style_colors",
    "style_diverging_colormap",
    "truncate_colormap",
    "use_style",
]
