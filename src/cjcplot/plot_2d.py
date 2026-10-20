"""2D plots: heatmaps (pcolormesh) with optional contour overlays and a colorbar.

Designed for frequency-delay maps, parameter sweeps and other 2D fields. The
default colormap comes from the active style (``image.cmap``); with
``cbar_symmetric=True`` the style's diverging colormap is used instead.
"""

from __future__ import annotations

from typing import Literal, Optional, Sequence, Union

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.colors import Colormap, LogNorm, Normalize
from matplotlib.figure import Figure
import numpy as np
from numpy.typing import ArrayLike

from cjcplot._figure import configure_ticks, create_figure_and_axes, finalize_axes
from cjcplot.styles import style_diverging_colormap

# pcolormesh shading modes; listing them gives autocomplete in editors.
MeshShading = Literal["flat", "nearest", "gouraud", "auto"]


def _cell_edges(centers: np.ndarray, log: bool) -> np.ndarray:
    """Return N+1 pcolormesh cell edges bracketing N sorted 1D coordinate centers.

    matplotlib's default shading puts edges at the linear midpoint between
    neighbouring centers. On a log-scaled axis with irregular spacing that
    midpoint lands far off the visual centre and gives lopsided cells, so the
    midpoint is taken in log space (geometric mean) when the axis is logarithmic.
    """
    values = np.log10(centers) if log else centers
    mid = (values[:-1] + values[1:]) / 2.0
    first_edge = values[0] - (mid[0] - values[0])
    last_edge = values[-1] + (values[-1] - mid[-1])
    edges = np.concatenate(([first_edge], mid, [last_edge]))
    return 10.0**edges if log else edges


def plot_2d(
    x_data: ArrayLike,
    y_data: ArrayLike,
    z_data: ArrayLike,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    cbar_label: str = "",
    xlim: Optional[Sequence[float]] = None,
    ylim: Optional[Sequence[float]] = None,
    clim: Optional[Sequence[Optional[float]]] = None,
    cmap: Optional[Union[str, Colormap]] = None,
    nan_color: str = "white",
    shading: Optional[MeshShading] = "auto",
    aspect: Union[Literal["auto", "equal"], float] = "auto",
    fig_show: bool = True,
    save_path: Optional[str] = None,
    fig_textwidth_pt: float = 497.0,
    fig_aspect_ratio: tuple[float, float] = (0.6, 0.5),
    minor_tick_count: int = 1,
    xticks_pos: Optional[Sequence[float]] = None,
    xticks_labels: Optional[Sequence[str]] = None,
    yticks_pos: Optional[Sequence[float]] = None,
    yticks_labels: Optional[Sequence[str]] = None,
    grid_show: bool = False,
    cbar_show: bool = True,
    cbar_aspect_ratio: tuple[float, float] = (0.03, 1.0),
    cbar_pad: float = 0.02,
    cbar_ticks: Optional[Sequence[float]] = None,
    cbar_symmetric: bool = False,
    norm: Optional[Normalize] = None,
    alpha: float = 0.92,
    logx: bool = False,
    logy: bool = False,
    logcbar: bool = False,
    contour: bool = False,
    contour_levels: Optional[Union[int, Sequence[float]]] = 10,
    contour_cmap: Optional[str] = None,
    contour_linewidths: Optional[float] = None,
    contour_labels: bool = False,
    ax: Optional[Axes] = None,
    cax: Optional[Axes] = None,
) -> tuple[Figure, Axes]:
    """Render a 2D colormap (pcolormesh) with an optional contour overlay.

    Parameters
    ----------
    x_data, y_data : array-like
        1D coordinate arrays, or 2D meshgrids with the shape of ``z_data``.
    z_data : array-like
        2D array of shape ``(len(y_data), len(x_data))`` when x/y are 1D.
        NaN cells are drawn in ``nan_color``.
    xlabel, ylabel, title : str
        Axis labels and title.
    cbar_label : str
        Colorbar label.
    xlim, ylim : (min, max), optional
        Axis limits.
    clim : (min, max), optional
        Colour limits: the z values at the bottom and top of the colorbar.
        Either entry may be None to take it from the data.
    cmap : str or Colormap, optional
        Heatmap colormap. Default: the active style's ``image.cmap``
        (``reds_cjc`` for the cjc style), or the style's diverging colormap
        (``bluered_cjc`` for the cjc style) when ``cbar_symmetric=True``.
    nan_color : str, default "white"
        Colour of NaN cells, e.g. grid points outside the measured or swept region.
    shading : {"flat", "nearest", "gouraud", "auto"}, optional
        pcolormesh shading mode.
    aspect : {"auto", "equal"} or float, default "auto"
        Axes aspect ratio of the data.
    fig_show : bool, default True
        Call ``plt.show()`` at the end. Ignored when ``ax`` is given.
    save_path : str, optional
        Save the figure to this path (dpi from the style).
    fig_textwidth_pt : float, default 497.0
        LaTeX text width in points (print it with ``\\the\\textwidth`` in LaTeX).
        Ignored when ``ax`` is given.
    fig_aspect_ratio : (float, float), default (0.6, 0.5)
        Figure (width, height) as fractions of ``fig_textwidth_pt``; include it
        in LaTeX at ``width=<width>\\textwidth`` so fonts keep their true size.
    minor_tick_count : int, default 1
        Number of minor ticks between major ticks.
    xticks_pos, yticks_pos, xticks_labels, yticks_labels : optional
        Explicit major ticks and their labels.
    grid_show : bool, default False
        Show grid lines.
    cbar_show : bool, default True
        Show the colorbar.
    cbar_aspect_ratio : (float, float), default (0.03, 1.0)
        Colorbar (width, height) as fractions of the plot box -- the area inside
        the axes, excluding title and labels. ``(0.03, 1.0)`` is a bar as tall
        as the plot and 3 % of its width. Ignored when ``cax`` is given.
    cbar_pad : float, default 0.02
        Gap between plot and colorbar as a fraction of the plot width.
        Ignored when ``cax`` is given.
    cbar_ticks : sequence[float], optional
        Explicit colorbar tick positions.
    cbar_symmetric : bool, default False
        Make the colour limits symmetric around zero (``clim = (-a, a)``)
        so a diverging colormap has its centre exactly at 0. ``a`` is the
        largest absolute ``clim`` entry when given, else ``max(|z|)``.
    norm : matplotlib.colors.Normalize, optional
        Explicit normalisation; overrides ``clim``.
    alpha : float, default 0.92
        Heatmap opacity.
    logx, logy : bool, default False
        Logarithmic axes.
    logcbar : bool, default False
        Logarithmic colour scale (requires strictly positive data).
    contour : bool, default False
        Overlay contour lines.
    contour_levels : int or sequence[float], default 10
        Number of contour levels or explicit level values.
    contour_cmap : str, optional
        Colormap for the contour lines. Default: one colour, the style's
        ``axes.edgecolor``, so the lines stay visible on the heatmap.
    contour_linewidths : float, optional
        Contour line width. Default: the style's ``contour.linewidth``.
    contour_labels : bool, default False
        Label the contour lines with their values.
    ax : matplotlib.axes.Axes, optional
        Existing axes to draw into; ``fig_show``, ``fig_textwidth_pt`` and
        ``fig_aspect_ratio`` are then ignored.
    cax : matplotlib.axes.Axes, optional
        Existing axes for the colorbar, e.g. one bar shared by several plots.

    Returns
    -------
    (Figure, Axes)
    """
    x_array = np.asarray(x_data)
    y_array = np.asarray(y_data)
    z_array = np.asarray(z_data)
    if z_array.ndim != 2:
        raise ValueError("z_data must be a 2D array.")

    # Contours always use the cell centres; the heatmap may need cell edges.
    mesh_shading: Optional[MeshShading] = shading
    if x_array.ndim == 1 and y_array.ndim == 1:
        if z_array.shape != (y_array.size, x_array.size):
            raise ValueError("z_data shape must be (len(y_data), len(x_data)) when x_data/y_data are 1D.")
        # Only "auto"/"flat" want edges; "gouraud"/"nearest" want centres.
        if shading in (None, "auto", "flat"):
            x_plot = _cell_edges(x_array, log=logx) if x_array.size > 1 else x_array
            y_plot = _cell_edges(y_array, log=logy) if y_array.size > 1 else y_array
            mesh_shading = "flat" if x_array.size > 1 and y_array.size > 1 else shading
        else:
            x_plot, y_plot = x_array, y_array
    elif x_array.ndim == 2 and y_array.ndim == 2:
        if x_array.shape != y_array.shape or z_array.shape != x_array.shape:
            raise ValueError("x_data, y_data, and z_data must have matching shapes when using 2D grids.")
        x_plot, y_plot = x_array, y_array
    else:
        raise ValueError("x_data and y_data must both be 1D or both be 2D arrays.")

    # Options that cannot be combined.
    if norm is not None and logcbar:
        raise ValueError("logcbar cannot be used together with an explicit norm.")
    if cbar_symmetric and logcbar:
        raise ValueError("cbar_symmetric cannot be used with logcbar: a log scale cannot be symmetric around 0.")
    if cbar_symmetric and norm is not None:
        raise ValueError("cbar_symmetric cannot be used together with an explicit norm.")

    # Create a new figure, or draw into the axes provided by the caller.
    ax_provided = ax is not None
    if ax_provided:
        fig = ax.get_figure()
    else:
        fig, ax = create_figure_and_axes(fig_textwidth_pt, fig_aspect_ratio)
    configure_ticks(ax, minor_tick_count, xticks_pos, xticks_labels, yticks_pos, yticks_labels)

    # Colour limits; None entries are later taken from the data by matplotlib.
    clim_min, clim_max = (None, None) if clim is None else clim

    # Symmetric limits put the centre of a diverging colormap exactly at zero.
    if cbar_symmetric:
        given_limits = [abs(limit) for limit in (clim_min, clim_max) if limit is not None]
        half_range = max(given_limits) if given_limits else float(np.nanmax(np.abs(z_array)))
        clim_min, clim_max = -half_range, half_range

    # Logarithmic colour scale over strictly positive data.
    color_norm = norm
    if logcbar:
        if np.any(z_array <= 0):
            raise ValueError("logcbar=True requires all z_data values to be strictly positive.")
        clim_min = float(np.nanmin(z_array)) if clim_min is None else clim_min
        clim_max = float(np.nanmax(z_array)) if clim_max is None else clim_max
        if clim_min <= 0 or clim_max <= 0:
            raise ValueError("logcbar=True requires both clim limits to be strictly positive.")
        if clim_min >= clim_max:
            raise ValueError("clim[0] must be smaller than clim[1].")
        # matplotlib builds LogNorm at runtime, which PyCharm wrongly reads as abstract.
        # noinspection PyAbstractClass
        color_norm = LogNorm(vmin=clim_min, vmax=clim_max)

    # Colormap from the argument or the style, with NaN cells in nan_color.
    if cmap is None:
        cmap = style_diverging_colormap() if cbar_symmetric else plt.rcParams["image.cmap"]
    heatmap_cmap = matplotlib.colormaps.get_cmap(cmap).with_extremes(bad=nan_color)

    # Render the heatmap.
    im = ax.pcolormesh(
        x_plot, y_plot, z_array,
        cmap=heatmap_cmap,
        shading=mesh_shading,
        alpha=alpha,
        vmin=None if color_norm is not None else clim_min,
        vmax=None if color_norm is not None else clim_max,
        norm=color_norm,
    )

    # Contour lines in one style colour, unless a contour colormap is requested.
    if contour:
        contour_color_kwargs = (
            {"cmap": contour_cmap} if contour_cmap is not None else {"colors": plt.rcParams["axes.edgecolor"]}
        )
        cs = ax.contour(
            x_array, y_array, z_array,
            levels=contour_levels,
            linewidths=contour_linewidths,
            **contour_color_kwargs,
        )
        if contour_labels:
            ax.clabel(cs, inline=True, fontsize=8)

    # Colorbar placed in plot-box coordinates, so its size is relative to the plot.
    if cbar_show:
        if cax is None:
            cbar_width, cbar_height = cbar_aspect_ratio
            cax = ax.inset_axes((1.0 + cbar_pad, (1.0 - cbar_height) / 2.0, cbar_width, cbar_height))
        fig.colorbar(im, cax=cax, label=cbar_label, ticks=cbar_ticks)

    ax.set_aspect(aspect)

    finalize_axes(
        fig, ax,
        xlim=xlim, ylim=ylim,
        xlabel=xlabel, ylabel=ylabel, title=title,
        grid_show=grid_show,
        save_path=save_path,
        fig_show=fig_show and not ax_provided,
        logx=logx, logy=logy,
    )
    return fig, ax
