"""All colours of the cjc style: line palette, colormaps and default colormaps.

This file is read by :func:`cjcplot.use_style` when the ``cjc`` style is
applied. Every name below is optional; a style folder without a colors.py
simply keeps the colours of its .mplstyle file.

- ``PALETTE``: line colours, set as the colour cycle (``axes.prop_cycle``).
  Scripts get them with :func:`cjcplot.style_colors`, so they follow the
  active style instead of hard-coding this list.
- ``COLORMAPS``: colormaps registered with matplotlib under their name (plus a
  reversed ``<name>_r``), so ``cmap="reds_cjc"`` works everywhere.
- ``DEFAULT_CMAP``: default heatmap colormap (``image.cmap``).
- ``DIVERGING_CMAP``: colormap for signed data centred on zero, used by
  :func:`cjcplot.plot_2d` when ``cbar_symmetric=True`` and no ``cmap`` is given.
"""

import matplotlib
import numpy as np

from cjcplot.styles._colormap_tools import colormap_from_colors, join_colormaps

# Blue, yellow and red first; after that the colours alternate light and dark
# (CIELAB lightness L* in the comments), so neighbouring traces stay apart.
PALETTE = (
    "#003399",  # blue           L* 26
    "#FFCC00",  # yellow         L* 84
    "#B2182B",  # red            L* 38
    "#4BB3E0",  # light blue     L* 69
    "#264B1E",  # dark green     L* 28
    "#FF6700",  # orange         L* 62
    "#9853E3",  # purple         L* 50
    "#9ACD32",  # yellow-green   L* 77
    "#8C564B",  # brown          L* 42
    "#008B8B",  # dark cyan      L* 52
    "#C71585",  # magenta        L* 45
    "#80804C",  # olive          L* 52 (middle of blueyellow_cjc)
)

# Shared light grey where the single-hue ramps start and the diverging map is
# centred. It stays distinct from NaN cells, which plot_2d draws white.
GREY = "#E0E0E0"

# Naming: every map runs from low to high values in the order of its name, and
# matplotlib adds a reversed copy with the suffix _r (reds_cjc_r: dark red to grey).

# Single-hue ramps for one-sided data (spreads, |bias|, ratios): from GREY into
# the darker 70 % of matplotlib's Reds/Blues, getting steadily darker.
_RAMP_FRACTIONS = np.linspace(0.3, 1.0, 6)
_reds = colormap_from_colors([GREY, *matplotlib.colormaps["Reds"](_RAMP_FRACTIONS)], "reds_cjc")
_blues = colormap_from_colors([GREY, *matplotlib.colormaps["Blues"](_RAMP_FRACTIONS)], "blues_cjc")

# Diverging map for signed data: dark blue (negative) -> GREY (zero) -> dark red
# (positive), built from the two ramps so all three maps share their colours.
_bluered = join_colormaps(_blues.reversed(), _reds, "bluered_cjc")

# Two-colour maps straight between palette colours, without a white or grey
# midpoint, so they match the line colours of the same plots. Both directions
# have their own name; sample them for line colours with colors_from_cmap().
_blueyellow = colormap_from_colors([PALETTE[0], PALETTE[1]], "blueyellow_cjc")
_yellowblue = colormap_from_colors([PALETTE[1], PALETTE[0]], "yellowblue_cjc")
_yellowred = colormap_from_colors([PALETTE[1], PALETTE[2]], "yellowred_cjc")
_redyellow = colormap_from_colors([PALETTE[2], PALETTE[1]], "redyellow_cjc")

COLORMAPS = (_reds, _blues, _bluered, _blueyellow, _yellowblue, _yellowred, _redyellow)

DEFAULT_CMAP = "reds_cjc"
DIVERGING_CMAP = "bluered_cjc"
