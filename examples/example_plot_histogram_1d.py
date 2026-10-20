"""plot_histogram_1d: two overlaid histograms, the second drawn on top."""

from pathlib import Path

import numpy as np

from cjcplot import plot_histogram_1d

# Samples mimicking a Gaussian and a Lorentzian distribution of similar width.
rng = np.random.default_rng(0)
gaussian_samples = rng.normal(0.0, 0.12, 500000)
lorentzian_samples = 0.14 * rng.standard_cauchy(500000)

# A constant weight per sample scales the counts to arbitrary units below 1.
plot_histogram_1d(
    [gaussian_samples, lorentzian_samples],
    bins=200,
    bin_range=(-1.0, 1.0),
    weights=[np.full(500000, 4.25e-5)] * 2,
    first_on_top=False,
    legend_labels=["Gaussian", "Lorentzian"],
    legend_loc="upper left",
    xlabel="Value [arb. u]",
    ylabel="Count [arb. u]",
    xlim=(-1.0, 1.0),
    ylim=(0.0, 1.0),
    save_path=str(Path(__file__).with_suffix(".png")),
    fig_show=False,
)
