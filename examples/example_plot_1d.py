"""plot_1d: a measurement with error bars and markers, a reference, and reference lines."""

from pathlib import Path

import numpy as np

from cjcplot import plot_1d

# A decaying sine as the measurement and a decaying cosine as the reference.
x = np.linspace(0.0, 1.0, 40)
measurement = np.exp(-x / 0.4) * np.sin(4 * np.pi * x)
reference = np.exp(-x / 0.25) * np.cos(4 * np.pi * x)

plot_1d(
    [x, x],
    [measurement, reference],
    yerr_data=[0.05 * np.ones_like(x), None],
    scatter_show=[True, False],
    line_styles=["-", "--"],
    legend_labels=["measurement", "reference"],
    vlines_pos=[0.6],
    vlines_labels=["vert. value"],
    hlines_pos=[0.0],
    hlines_styles=[":"],
    hlines_labels=["hor. value"],
    xlim=(0.0, 1.0),
    ylim=(-1.0, 1.0),
    xlabel="X axis [arb. u]",
    ylabel="Y axis [arb. u]",
    legend_ncols=2,
    legend_loc="lower right",
    fig_aspect_ratio=(0.75, 0.5),
    save_path=str(Path(__file__).with_suffix(".png")),
    fig_show=False,
)
