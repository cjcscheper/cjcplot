"""Show the active style's line palette and the cjc colormaps."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from cjcplot import style_colors

colors = style_colors()
# Vertical distance between colormap rows; each gradient is 1.2 tall.
CMAP_ROW_STEP = 1.4

cmap_names = ["reds_cjc", "blues_cjc_r", "bluered_cjc", "blueyellow_cjc", "yellowred_cjc"]

fig, (ax_palette, ax_cmaps) = plt.subplots(
    2, 1, figsize=(6.5, 4.4), layout="constrained",
    height_ratios=(len(colors), CMAP_ROW_STEP * len(cmap_names)),
)

# One swatch per palette colour, labelled with its index and hex value.
for i, color in enumerate(colors):
    ax_palette.barh(i, 1.0, color=color)
    ax_palette.text(1.02, i, f"{i}: {color}", va="center", fontsize=8)
ax_palette.set_xlim(0, 1.6)
ax_palette.invert_yaxis()
ax_palette.set_axis_off()
ax_palette.set_title("style_colors()")

# Each colormap as a horizontal gradient.
gradient = np.linspace(0, 1, 256)[None, :]
for row, name in enumerate(cmap_names):
    top = CMAP_ROW_STEP * row + 0.1
    ax_cmaps.imshow(gradient, cmap=name, aspect="auto", extent=(0, 1, top + 1.2, top))
    ax_cmaps.text(1.02, top + 0.6, name, va="center", fontsize=8)
ax_cmaps.set_xlim(0, 1.6)
ax_cmaps.set_ylim(CMAP_ROW_STEP * len(cmap_names), 0)
ax_cmaps.set_axis_off()

fig.savefig(Path(__file__).with_suffix(".png"))
