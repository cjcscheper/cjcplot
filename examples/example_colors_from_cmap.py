"""colors_from_cmap: a series of spectra coloured from one end of a colormap to the other."""

from pathlib import Path

import numpy as np

from cjcplot import colors_from_cmap, plot_1d

# Curves mimicking Planck's law: as the parameter rises, the peak grows and shifts left.
x = np.linspace(0.01, 1.0, 400)
parameters = np.linspace(1.0, 2.0, 7)
spectra = [0.0146 * x**-5 / np.expm1(1.6 / (x * parameter)) for parameter in parameters]

# First spectrum at the red end of redyellow_cjc, last at the yellow end.
plot_1d(
    [x] * len(spectra),
    spectra,
    colors=colors_from_cmap("redyellow_cjc", len(spectra)),
    legend_labels=[f"Value {number}" for number in range(1, len(spectra) + 1)],
    first_on_top=False,
    xlim=(0.0, 1.0),
    ylim=(0.0, 1.0),
    xlabel="X axis [arb. u]",
    ylabel="Y axis [arb. u]",
    fig_aspect_ratio=(0.75, 0.5),
    save_path=str(Path(__file__).with_suffix(".png")),
    fig_show=False,
)
