"""plot_2d: a one-sided map (default reds_cjc) and a signed map (cbar_symmetric)."""

from pathlib import Path

import numpy as np

from cjcplot import plot_2d

output_stem = Path(__file__).with_suffix("")

x = np.linspace(-1.0, 1.0, 201)
y = np.linspace(-1.0, 1.0, 201)
xx, yy = np.meshgrid(x, y)

# One-sided data mimicking a Gaussian beam spot, wider than it is tall.
pulse = np.exp(-2 * (xx**2 / 0.75**2 + yy**2 / 0.4**2))
plot_2d(
    x, y, pulse,
    clim=(0.0, 1.0),
    xlabel="X axis [arb. u]", ylabel="Y axis [arb. u]", cbar_label="C axis [arb. u]",
    xlim=(-1.0, 1.0), ylim=(-1.0, 1.0),
    aspect="equal",
    fig_aspect_ratio=(0.6, 0.5),
    save_path=f"{output_stem}_one_sided.png",
    fig_show=False,
)

# Signed data mimicking the potential of a dipole: positive right, negative left.
potential = 0.18 / np.sqrt((xx - 0.3) ** 2 + yy**2 + 0.02) - 0.18 / np.sqrt((xx + 0.3) ** 2 + yy**2 + 0.02)
plot_2d(
    x, y, potential,
    clim=(-1.0, 1.0),
    xlabel="X axis [arb. u]", ylabel="Y axis [arb. u]", cbar_label="C axis [arb. u]",
    cbar_symmetric=True,
    contour=True, contour_levels=[-0.8, -0.4, -0.2, -0.1, 0.1, 0.2, 0.4, 0.8],
    xlim=(-1.0, 1.0), ylim=(-1.0, 1.0),
    aspect="equal",
    fig_aspect_ratio=(0.6, 0.5),
    save_path=f"{output_stem}_signed.png",
    fig_show=False,
)
