"""Styles: bundled cjc style, custom style folders, and the cjc colormaps."""

import importlib

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pytest

import cjcplot
from cjcplot.styles.cjc import colors as cjc_colors


def _luminance(rgba: np.ndarray) -> np.ndarray:
    """Relative luminance of sRGB colours, as a proxy for perceived lightness."""
    rgb = rgba[..., :3]
    linear = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    return linear @ np.array([0.2126, 0.7152, 0.0722])


def test_cjc_is_bundled_and_applied_on_import():
    assert "cjc" in cjcplot.available_styles()
    assert plt.rcParams["font.size"] == 14
    assert plt.rcParams["savefig.dpi"] == 300
    assert plt.rcParams["image.cmap"] == "reds_cjc"
    assert cjcplot.style_colors() == list(cjc_colors.PALETTE)


def test_cjc_colormaps_are_registered_with_reversed_versions():
    for name in (
        "reds_cjc", "blues_cjc", "bluered_cjc",
        "blueyellow_cjc", "yellowblue_cjc", "yellowred_cjc", "redyellow_cjc",
    ):
        assert name in matplotlib.colormaps
        assert f"{name}_r" in matplotlib.colormaps


@pytest.mark.parametrize(
    ("name", "low_index", "high_index"),
    [("blueyellow_cjc", 0, 1), ("yellowblue_cjc", 1, 0), ("yellowred_cjc", 1, 2), ("redyellow_cjc", 2, 1)],
)
def test_two_colour_maps_run_between_palette_colours_without_white(name, low_index, high_index):
    colors = matplotlib.colormaps[name](np.linspace(0, 1, 256))
    assert np.allclose(colors[0], matplotlib.colors.to_rgba(cjc_colors.PALETTE[low_index]), atol=0.01)
    assert np.allclose(colors[-1], matplotlib.colors.to_rgba(cjc_colors.PALETTE[high_index]), atol=0.01)
    # No colour in between is lighter than the lighter end, so the map never passes through white.
    lightness = _luminance(colors)
    assert lightness.max() <= max(lightness[0], lightness[-1]) + 1e-9


def test_reds_cjc_runs_from_grey_and_darkens_monotonically():
    colors = matplotlib.colormaps["reds_cjc"](np.linspace(0, 1, 256))
    assert np.allclose(colors[0], matplotlib.colors.to_rgba(cjc_colors.GREY), atol=0.01)
    assert np.all(np.diff(_luminance(colors)) <= 1e-9)


def test_blues_cjc_runs_from_grey_and_darkens_monotonically():
    colors = matplotlib.colormaps["blues_cjc"](np.linspace(0, 1, 256))
    assert np.allclose(colors[0], matplotlib.colors.to_rgba(cjc_colors.GREY), atol=0.01)
    assert np.all(np.diff(_luminance(colors)) <= 1e-9)


def test_bluered_cjc_runs_blue_to_grey_to_red():
    colors = matplotlib.colormaps["bluered_cjc"](np.linspace(0, 1, 256))
    lightness = _luminance(colors)
    # Blue (low) and red (high) ends, grey in the middle, lightest at the centre.
    assert colors[0][2] > colors[0][0] and colors[-1][0] > colors[-1][2]
    assert np.allclose(colors[127], matplotlib.colors.to_rgba(cjc_colors.GREY), atol=0.01)
    assert np.all(np.diff(lightness[:128]) >= -1e-9)
    assert np.all(np.diff(lightness[128:]) <= 1e-9)


def test_cjc_diverging_cmap_is_bluered():
    assert cjcplot.style_diverging_cmap() == "bluered_cjc"


def test_custom_style_folder_sets_palette_and_cmap(tmp_path):
    folder = tmp_path / "mystyle"
    folder.mkdir()
    (folder / "mystyle.mplstyle").write_text("font.size: 9\n")
    (folder / "colors.py").write_text(
        "from cjcplot import truncate_colormap\n"
        "PALETTE = ('#111111', '#222222')\n"
        "COLORMAPS = (truncate_colormap('Greens', 0.2, 1.0, 'greens_test'),)\n"
        "DEFAULT_CMAP = 'greens_test'\n"
        "DIVERGING_CMAP = 'PuOr'\n"
    )
    cjcplot.use_style(folder)
    assert plt.rcParams["font.size"] == 9
    assert cjcplot.style_colors() == ["#111111", "#222222"]
    assert plt.rcParams["image.cmap"] == "greens_test"
    assert cjcplot.style_diverging_cmap() == "PuOr"


def test_single_mplstyle_file_resets_previous_style(tmp_path):
    style_file = tmp_path / "plain.mplstyle"
    style_file.write_text("lines.linewidth: 3.0\n")
    cjcplot.use_style(style_file)
    assert plt.rcParams["lines.linewidth"] == 3.0
    # cjc's font size is gone: settings are reset before a style is applied.
    assert plt.rcParams["font.size"] == matplotlib.rcParamsDefault["font.size"]
    assert cjcplot.style_diverging_cmap() == "RdBu_r"


def test_unknown_style_raises():
    with pytest.raises(ValueError, match="Unknown style"):
        cjcplot.use_style("does_not_exist")


def test_colors_from_cmap_runs_from_left_to_right_end():
    colors = cjcplot.colors_from_cmap("blueyellow_cjc", 5)
    assert len(colors) == 5
    assert colors[0] == cjc_colors.PALETTE[0].lower()
    assert colors[-1] == cjc_colors.PALETTE[1].lower()
    assert cjcplot.colors_from_cmap("blueyellow_cjc", 1) == [cjc_colors.PALETTE[0].lower()]
    with pytest.raises(ValueError, match="count must be at least 1"):
        cjcplot.colors_from_cmap("blueyellow_cjc", 0)


def test_import_warns_and_keeps_matplotlib_defaults_without_cjc_folder(tmp_path, monkeypatch):
    # Simulate a setup where styles/cjc/ was removed: point the style folder at an empty directory.
    monkeypatch.setattr(cjcplot.styles, "STYLES_DIR", tmp_path)
    plt.style.use("default")
    with pytest.warns(UserWarning, match="Default style 'cjc' not found"):
        importlib.reload(cjcplot)
    assert plt.rcParams["font.size"] == matplotlib.rcParamsDefault["font.size"]
    # Plots still work, with matplotlib's colour cycle.
    _, ax = cjcplot.plot_1d([0.0, 1.0], [0.0, 1.0], fig_show=False)
    assert len(ax.get_lines()) == 1
