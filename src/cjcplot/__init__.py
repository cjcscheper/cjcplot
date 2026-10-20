"""cjcplot: publication-ready matplotlib figures sized to a LaTeX text width.

Importing cjcplot applies the ``cjc`` style (fonts, ticks, colours, default
colormap) to all matplotlib figures. Switch with :func:`use_style`.
"""

import warnings

from cjcplot.styles import (
    available_styles,
    colormap_from_colors,
    colors_from_colormap,
    join_colormaps,
    register_colormap,
    style_colors,
    style_diverging_colormap,
    truncate_colormap,
    use_style,
)
from cjcplot.plot_1d import plot_1d, plot_histogram_1d
from cjcplot.plot_2d import plot_2d
from cjcplot.plot_3d import plot_3d

__version__ = "0.2.0"

# The default style, so every figure looks consistent without extra calls. If its
# folder was removed, plots keep working with matplotlib's own defaults.
DEFAULT_STYLE = "cjc"
if DEFAULT_STYLE in available_styles():
    use_style(DEFAULT_STYLE)
else:
    warnings.warn(
        f"Default style {DEFAULT_STYLE!r} not found in cjcplot/styles/; using matplotlib's defaults. "
        "Restore the styles/cjc/ folder, or call use_style() with your own style.",
        UserWarning,
        stacklevel=2,
    )

__all__ = [
    "available_styles",
    "colormap_from_colors",
    "colors_from_colormap",
    "join_colormaps",
    "plot_1d",
    "plot_2d",
    "plot_3d",
    "plot_histogram_1d",
    "register_colormap",
    "style_colors",
    "style_diverging_colormap",
    "truncate_colormap",
    "use_style",
]
