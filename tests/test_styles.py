"""Styles: bundled cjc style, custom style folders, and the cjc colormaps."""

import importlib

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pytest

import cjcplot
from cjcplot.styles.cjc import colors as cjc_colors


def _luminance(rgba: np.ndarray) -> np.ndarray:
    """Relative luminance of sRGB colours, as a proxy for perceived lightness.

    Used to check that a colormap gets steadily darker (or lighter): a dip or bump
    in lightness would show up as a band that looks like a step in the data.
    """
    rgb = rgba[..., :3]
    linear = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    return linear @ np.array([0.2126, 0.7152, 0.0722])


def test_cjc_is_bundled_and_applied_on_import():
    """Importing cjcplot applies the cjc style: its fonts, dpi, default colormap and palette."""
    assert "cjc" in cjcplot.available_styles()
    assert plt.rcParams["font.size"] == 14
    assert plt.rcParams["savefig.dpi"] == 300
    assert plt.rcParams["image.cmap"] == "reds_cjc"
    assert cjcplot.style_colors() == list(cjc_colors.PALETTE)


def test_cjc_colormaps_are_registered_with_reversed_versions():
    """Every cjc colormap works by name, and matplotlib's reversed _r copy exists too."""
    for name in (
        "reds_cjc", "blues_cjc", "bluered_cjc",
        "blueyellow_cjc", "yellowblue_cjc", "yellowred_cjc", "redyellow_cjc",
    ):
        assert name in matplotlib.colormaps
        assert f"{name}_r" in matplotlib.colormaps


# Each two-colour map with the palette indices of its low and high end.
@pytest.mark.parametrize(
    ("name", "low_index", "high_index"),
    [("blueyellow_cjc", 0, 1), ("yellowblue_cjc", 1, 0), ("yellowred_cjc", 1, 2), ("redyellow_cjc", 2, 1)],
)
def test_two_colour_maps_run_between_palette_colours_without_white(name, low_index, high_index):
    """Two-colour maps start and end at their palette colours and never pass through white."""
    # 256 evenly spaced samples along the colormap, from its low to its high end.
    colors = matplotlib.colormaps[name](np.linspace(0, 1, 256))
    assert np.allclose(colors[0], matplotlib.colors.to_rgba(cjc_colors.PALETTE[low_index]), atol=0.01)
    assert np.allclose(colors[-1], matplotlib.colors.to_rgba(cjc_colors.PALETTE[high_index]), atol=0.01)
    # No colour in between is lighter than the lighter end, so the map never passes through white.
    lightness = _luminance(colors)
    assert lightness.max() <= max(lightness[0], lightness[-1]) + 1e-9


def test_reds_cjc_runs_from_grey_and_darkens_monotonically():
    """reds_cjc starts at the style's grey (not white) and gets steadily darker."""
    colors = matplotlib.colormaps["reds_cjc"](np.linspace(0, 1, 256))
    assert np.allclose(colors[0], matplotlib.colors.to_rgba(cjc_colors.GREY), atol=0.01)
    assert np.all(np.diff(_luminance(colors)) <= 1e-9)


def test_blues_cjc_runs_from_grey_and_darkens_monotonically():
    """blues_cjc starts at the style's grey (not white) and gets steadily darker."""
    colors = matplotlib.colormaps["blues_cjc"](np.linspace(0, 1, 256))
    assert np.allclose(colors[0], matplotlib.colors.to_rgba(cjc_colors.GREY), atol=0.01)
    assert np.all(np.diff(_luminance(colors)) <= 1e-9)


def test_bluered_cjc_runs_blue_to_grey_to_red():
    """The diverging map runs dark blue -> grey (at zero) -> dark red, lightest at the centre."""
    colors = matplotlib.colormaps["bluered_cjc"](np.linspace(0, 1, 256))
    lightness = _luminance(colors)
    # Low end bluer than red, high end redder than blue (RGBA index 0 = red, 2 = blue).
    assert colors[0][2] > colors[0][0] and colors[-1][0] > colors[-1][2]
    # Sample 127 of 256 is the middle of the map.
    assert np.allclose(colors[127], matplotlib.colors.to_rgba(cjc_colors.GREY), atol=0.01)
    # Getting lighter up to the centre, darker after it.
    assert np.all(np.diff(lightness[:128]) >= -1e-9)
    assert np.all(np.diff(lightness[128:]) <= 1e-9)


def test_cjc_diverging_colormap_is_bluered():
    """The cjc style uses bluered_cjc for signed data (plot_2d with cbar_symmetric=True)."""
    assert cjcplot.style_diverging_colormap() == "bluered_cjc"


def test_custom_style_folder_sets_palette_and_cmap(tmp_path):
    """A user's own style folder sets its fonts, palette and colormaps (tmp_path is a temporary folder)."""
    # Build a minimal style folder: one .mplstyle setting and a colors.py.
    folder = tmp_path / "mystyle"
    folder.mkdir()
    (folder / "mystyle.mplstyle").write_text("font.size: 9\n")
    (folder / "colors.py").write_text(
        "from cjcplot import truncate_colormap\n"
        "PALETTE = ('#111111', '#222222')\n"
        "COLORMAPS = (truncate_colormap('Greens', 0.2, 1.0, 'greens_test'),)\n"
        "DEFAULT_COLORMAP = 'greens_test'\n"
        "DIVERGING_COLORMAP = 'PuOr'\n"
    )
    cjcplot.use_style(folder)
    assert plt.rcParams["font.size"] == 9
    assert cjcplot.style_colors() == ["#111111", "#222222"]
    assert plt.rcParams["image.cmap"] == "greens_test"
    assert cjcplot.style_diverging_colormap() == "PuOr"


def test_single_mplstyle_file_resets_previous_style(tmp_path):
    """A single .mplstyle file works too, and nothing of the previous (cjc) style remains."""
    style_file = tmp_path / "plain.mplstyle"
    style_file.write_text("lines.linewidth: 3.0\n")
    cjcplot.use_style(style_file)
    assert plt.rcParams["lines.linewidth"] == 3.0
    # cjc's font size is gone: settings are reset before a style is applied.
    assert plt.rcParams["font.size"] == matplotlib.rcParamsDefault["font.size"]
    # Without a colors.py, the diverging colormap falls back to matplotlib's RdBu_r.
    assert cjcplot.style_diverging_colormap() == "RdBu_r"


def test_unknown_style_raises():
    """A style name that does not exist gives a clear error."""
    with pytest.raises(ValueError, match="Unknown style"):
        cjcplot.use_style("does_not_exist")


def test_colors_from_colormap_runs_from_left_to_right_end():
    """colors_from_colormap returns colours from the map's left end to its right end."""
    colors = cjcplot.colors_from_colormap("blueyellow_cjc", 5)
    assert len(colors) == 5
    # Hex strings come back in lower case.
    assert colors[0] == cjc_colors.PALETTE[0].lower()
    assert colors[-1] == cjc_colors.PALETTE[1].lower()
    # One colour is the left end; zero colours is an error.
    assert cjcplot.colors_from_colormap("blueyellow_cjc", 1) == [cjc_colors.PALETTE[0].lower()]
    with pytest.raises(ValueError, match="count must be at least 1"):
        cjcplot.colors_from_colormap("blueyellow_cjc", 0)


def test_import_warns_and_keeps_matplotlib_defaults_without_cjc_folder(tmp_path, monkeypatch):
    """Without the styles/cjc/ folder, importing cjcplot warns instead of failing."""
    # Simulate a setup where styles/cjc/ was removed: point the style folder at an empty directory.
    # monkeypatch undoes this after the test.
    monkeypatch.setattr(cjcplot.styles, "STYLES_DIR", tmp_path)
    plt.style.use("default")
    # Reloading runs cjcplot's import code again, as a fresh "import cjcplot" would.
    with pytest.warns(UserWarning, match="Default style 'cjc' not found"):
        importlib.reload(cjcplot)
    assert plt.rcParams["font.size"] == matplotlib.rcParamsDefault["font.size"]
    # Plots still work, with matplotlib's colour cycle.
    _, ax = cjcplot.plot_1d([0.0, 1.0], [0.0, 1.0], fig_show=False)
    assert len(ax.get_lines()) == 1
