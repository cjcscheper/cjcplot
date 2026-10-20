"""plot_2d: shapes, colour limits, colormaps, colorbar placement, contours."""

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pytest

import cjcplot

# A small signed test map: z = x * y on a 6 x 5 grid, shape (len(Y), len(X)).
X = np.linspace(-1.0, 1.0, 6)
Y = np.linspace(0.0, 2.0, 5)
Z = np.outer(Y, X)


def _mesh(ax):
    """Return the heatmap itself: pcolormesh stores it as a QuadMesh in ax.collections."""
    return next(c for c in ax.collections if isinstance(c, matplotlib.collections.QuadMesh))


def test_shape_mismatch_raises():
    """z_data must have shape (len(y), len(x)); the transposed map gives a clear error."""
    with pytest.raises(ValueError, match="z_data shape"):
        cjcplot.plot_2d(X, Y, Z.T, fig_show=False)


def test_default_cmap_comes_from_style():
    """Without cmap=, the heatmap uses the style's default colormap (reds_cjc)."""
    _, ax = cjcplot.plot_2d(X, Y, np.abs(Z), fig_show=False)
    # plot_2d adds the NaN colour to a copy of the colormap, so compare the start of the name.
    assert _mesh(ax).get_cmap().name.startswith("reds_cjc")


def test_cbar_symmetric_centres_limits_and_uses_diverging_colormap():
    """cbar_symmetric makes the colour limits -a..+a and switches to the diverging colormap."""
    _, ax = cjcplot.plot_2d(X, Y, Z, cbar_symmetric=True, fig_show=False)
    # The colour limits end up in the heatmap's norm as vmin and vmax.
    mesh = _mesh(ax)
    assert mesh.norm.vmin == -mesh.norm.vmax == -np.abs(Z).max()
    assert mesh.get_cmap().name.startswith(cjcplot.style_diverging_colormap())


def test_cbar_symmetric_uses_largest_given_limit():
    """With clim given, cbar_symmetric uses its largest absolute value for both limits."""
    _, ax = cjcplot.plot_2d(X, Y, Z, cbar_symmetric=True, clim=(-0.5, 1.5), fig_show=False)
    assert (_mesh(ax).norm.vmin, _mesh(ax).norm.vmax) == (-1.5, 1.5)


def test_clim_sets_colour_limits_and_accepts_none_entries():
    """clim sets the colour limits; a None entry is taken from the data."""
    _, ax = cjcplot.plot_2d(X, Y, Z, clim=(0.0, 1.0), fig_show=False)
    assert (_mesh(ax).norm.vmin, _mesh(ax).norm.vmax) == (0.0, 1.0)
    _, ax = cjcplot.plot_2d(X, Y, Z, clim=(None, 1.0), fig_show=False)
    assert (_mesh(ax).norm.vmin, _mesh(ax).norm.vmax) == (Z.min(), 1.0)


def test_equal_aspect_fits_inside_figure():
    """aspect="equal" gives a square plot that still fits, with its labels, in a (0.6, 0.5) figure."""
    x = np.linspace(-1.0, 1.0, 21)
    fig, ax = cjcplot.plot_2d(
        x, x, np.outer(x, x),
        xlabel="X axis [arb. u]", ylabel="Y axis [arb. u]", cbar_label="C axis [arb. u]",
        aspect="equal", fig_aspect_ratio=(0.6, 0.5), fig_show=False,
    )
    # Positions are only final after drawing; the renderer measures text extents.
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    # The plot box is square: its width equals its height in pixels.
    plot_box = ax.get_position()
    assert np.isclose(plot_box.width * fig.bbox.width, plot_box.height * fig.bbox.height, rtol=1e-3)
    # The y-label stays inside the left edge, the colorbar label inside the right edge.
    assert ax.get_tightbbox(renderer).x0 >= fig.bbox.x0 - 1e-6
    assert ax.child_axes[0].get_tightbbox(renderer).x1 <= fig.bbox.x1 + 1e-6


def test_cbar_symmetric_conflicts_raise():
    """cbar_symmetric cannot be combined with a log colour scale or an explicit norm."""
    with pytest.raises(ValueError, match="cbar_symmetric cannot be used with logcbar"):
        cjcplot.plot_2d(X, Y, np.abs(Z) + 1, cbar_symmetric=True, logcbar=True, fig_show=False)
    with pytest.raises(ValueError, match="explicit norm"):
        cjcplot.plot_2d(X, Y, Z, cbar_symmetric=True, norm=matplotlib.colors.Normalize(), fig_show=False)


def test_nan_cells_use_nan_color():
    """NaN cells are drawn in nan_color."""
    z = Z.copy()
    z[0, 0] = np.nan
    _, ax = cjcplot.plot_2d(X, Y, z, nan_color="black", fig_show=False)
    # matplotlib calls the NaN colour of a colormap its "bad" colour.
    assert np.allclose(_mesh(ax).get_cmap().get_bad(), (0, 0, 0, 1))


def test_cbar_aspect_ratio_is_relative_to_plot_box_and_fits_in_figure():
    """cbar_aspect_ratio sizes the colorbar relative to the plot, and its label fits in the figure."""
    fig, ax = cjcplot.plot_2d(X, Y, Z, cbar_label="a long colorbar label", cbar_aspect_ratio=(0.05, 0.5), fig_show=False)
    fig.canvas.draw()
    # The colorbar is an inset of the plot, so it is the plot's first child axes.
    cax = ax.child_axes[0]
    plot_box = ax.get_position()
    cbar_box = cax.get_position()
    assert np.isclose(cbar_box.height, 0.5 * plot_box.height)
    assert np.isclose(cbar_box.width, 0.05 * plot_box.width)
    # The layout leaves room for the colorbar and its label inside the figure.
    assert cax.get_tightbbox(fig.canvas.get_renderer()).x1 <= fig.bbox.x1 + 1e-6


def test_contours_default_to_one_style_colour():
    """Without contour_cmap, all contour lines get the style's axis colour (black for cjc)."""
    _, ax = cjcplot.plot_2d(X, Y, Z, contour=True, contour_levels=3, fig_show=False)
    # The contour lines are stored as a ContourSet in ax.collections, one edge colour per level.
    contour_set = next(c for c in ax.collections if isinstance(c, matplotlib.contour.ContourSet))
    edge = matplotlib.colors.to_rgba(plt.rcParams["axes.edgecolor"])
    assert all(np.allclose(color, edge) for color in contour_set.get_edgecolor())


def test_logcbar_requires_positive_data():
    """A log colour scale needs strictly positive data; Z contains zero and negatives."""
    with pytest.raises(ValueError, match="strictly positive"):
        cjcplot.plot_2d(X, Y, Z, logcbar=True, fig_show=False)


def test_draws_into_given_axes():
    """With ax=, plot_2d draws into that axes instead of a new figure."""
    fig, ax = plt.subplots()
    out_fig, out_ax = cjcplot.plot_2d(X, Y, Z, ax=ax)
    assert out_ax is ax and out_fig is fig


def test_plot_3d_placeholder():
    """plot_3d exists as a placeholder and does nothing yet."""
    assert cjcplot.plot_3d() is None
