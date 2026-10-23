# cjcplot

[![tests](https://github.com/cjcscheper/cjcplot/actions/workflows/tests.yml/badge.svg)](https://github.com/cjcscheper/cjcplot/actions/workflows/tests.yml)
[![release](https://img.shields.io/github/v/release/cjcscheper/cjcplot)](https://github.com/cjcscheper/cjcplot/releases)

Publication-ready matplotlib figures sized to a LaTeX text width, with one
consistent, switchable style.

## Install

```bash
pip install git+https://github.com/cjcscheper/cjcplot.git
```

To pin a fixed version, so a script keeps producing the same figures later on
(replace `v0.2.0` with the release you want, see
[Releases](https://github.com/cjcscheper/cjcplot/releases) and the
[changelog](CHANGELOG.md)):

```bash
pip install git+https://github.com/cjcscheper/cjcplot.git@v0.2.0
```

For development, clone the repository and install it editable:

```bash
pip install -e ".[test]"
```

## Quick start

```python
import numpy as np
from cjcplot import plot_1d

x = np.linspace(0.0, 1.0, 200)
y = np.exp(-x / 0.4) * np.sin(4 * np.pi * x)

fig, ax = plot_1d(
    x_data=x,
    y_data=y,
    xlabel="X axis [arb. u]",
    ylabel="Y axis [arb. u]",
    fig_aspect_ratio=(0.75, 0.5),   # (width, height) as fractions of the text width
)
```

**Importing cjcplot applies the built-in cjc style** to all matplotlib figures
(fonts, ticks, line colours, default colormap). It is easy to replace with your
own: create a style folder with your own `.mplstyle` (and optionally your own
colours), then switch to it with one line at the top of your script:

```python
from cjcplot import use_style
use_style("path/to/my_style")   # your own style folder, see "Styles" below
```

## Functions

| Function            | Use                                                                                                |
|---------------------|----------------------------------------------------------------------------------------------------|
| `plot_1d`           | one or more traces: lines, markers, x/y error bars, reference lines                                |
| `plot_histogram_1d` | one or more overlaid histograms (shared bins, `density`, `weights`, fills, hatches)                |
| `plot_2d`           | heatmap with optional contours; colorbar sized relative to the plot, `cbar_symmetric`, `nan_color` |
| `plot_3d`           | placeholder, not implemented yet                                                                   |

Every plot function returns `(fig, ax)` and accepts `ax=` to draw into an
existing figure. See `examples/` for one script per function.

<!-- widths = fig_aspect_ratio[0] x 640 px, so all fonts appear at the same size. -->

### `plot_1d` — `example_plot_1d.py`

A measurement with error bars and markers, a reference curve, and vertical and
horizontal reference lines, each with its own legend entry.

<p align="center">
  <img src="examples/example_plot_1d.png" alt="plot_1d" width="480">
</p>

### `colors_from_colormap` — `example_colors_from_colormap.py`

A series of spectra coloured from one end of a colormap to the other
(`redyellow_cjc`): the first curve red, the last yellow.

<p align="center">
  <img src="examples/example_colors_from_colormap.png" alt="colors_from_colormap" width="480">
</p>

### `plot_2d` — `example_plot_2d.py`

Left a one-sided map (a beam spot, default `reds_cjc`), right a signed map (a
dipole potential) with `cbar_symmetric=True`, which centres the diverging
colormap on zero.

<table align="center">
  <tr>
    <td><img src="examples/example_plot_2d_one_sided.png" alt="plot_2d one-sided" width="384"></td>
    <td><img src="examples/example_plot_2d_signed.png" alt="plot_2d signed" width="384"></td>
  </tr>
</table>

### `plot_histogram_1d` — `example_plot_histogram_1d.py`

Two overlaid histograms on shared bins, a Gaussian and a Lorentzian of similar
width, the second drawn on top.

<p align="center">
  <img src="examples/example_plot_histogram_1d.png" alt="plot_histogram_1d" width="320">
</p>

## Figure size: fractions of your document's text width

Figures are sized as fractions of the text width of the document they go into.
The default, `fig_textwidth_pt=497`, is the text width of the LaTeX document
cjcplot was built for, but any document with a known text width works the same
way, for example Word or PowerPoint. Inserted at that same width, nothing gets
rescaled, so **the fonts in the figure keep the exact point size of the style**
(14 pt labels, 11 pt ticks), in the same units as the document's own text. To
match your body text, set the font sizes in the style to that size.

1. Find the text width of your document in points and pass it as
   `fig_textwidth_pt` (default 497):
   - **LaTeX:** put `\the\textwidth` in the document; it prints e.g. `497.0pt`.
   - **Word:** page width minus the left and right margins, e.g. A4 with 2.5 cm
     margins: 21.0 − 5.0 = 16.0 cm = 454 pt (1 cm ≈ 28.35 pt).
   - **PowerPoint:** the slide width, e.g. 33.87 cm = 960 pt for a 16:9 slide,
     or the width of the area you place figures in.
   - **Anything else** (a poster, a web page, another editor): the width of the
     area the figure goes into, converted to points.
2. `fig_aspect_ratio=(width, height)` gives the figure size as fractions of that
   text width: `(0.5, 0.5)` is half the text width wide and half the text width
   tall. Defaults: `(0.5, 0.5)` for `plot_1d` and `plot_histogram_1d`,
   `(0.6, 0.5)` for `plot_2d`.
3. Insert the figure at the same width fraction, so it is not rescaled:
   - **LaTeX:**

     ```latex
     \includegraphics[width=0.5\textwidth]{figure.pdf}   % for fig_aspect_ratio=(0.5, ...)
     ```
   - **Word / PowerPoint:** insert the image and keep it at 100 % size (or set its
     width to the same fraction of the text width, e.g. 8.0 cm for 0.5 × 16.0 cm).

## Colorbar size

- `cbar_aspect_ratio=(width, height)` sizes the colorbar as fractions of the plot
  box (inside the axes, so titles and labels do not change it). The default
  `(0.03, 1.0)` is a bar as tall as the plot.

## Colours and colormaps

```python
from cjcplot import style_colors
color = style_colors()[2]       # third colour of the active style
```

Use `style_colors()` instead of hard-coded hex values, so scripts follow the
style when it is switched. The cjc style registers seven colormaps that work by
name everywhere (`cmap="reds_cjc"`), each with a reversed `_r` version:

- `reds_cjc` (default heatmap colormap): light grey to dark red.
- `blues_cjc`: light grey to dark blue.
- `bluered_cjc` (diverging, for signed data): dark blue, light grey at zero,
  dark red.
- `blueyellow_cjc`, `yellowblue_cjc`, `yellowred_cjc`, `redyellow_cjc`: straight
  between the first three palette colours (blue, yellow, red), without passing
  through white or grey. Both directions have their own name.

Line colours from a colormap, first trace at its left end and last at its right end:

```python
from cjcplot import colors_from_colormap, plot_1d
plot_1d(x_traces, y_traces, colors=colors_from_colormap("blueyellow_cjc", len(y_traces)))
```

Every name gives the order from low to high values; the suffix `_r` gives the
reversed map (`reds_cjc_r` runs from dark red to grey).

The grey ends and the grey centre stay distinct from NaN cells, which
`plot_2d` draws white (`nan_color`). For signed data use
`plot_2d(..., cbar_symmetric=True)`: the limits become symmetric around zero
and, without an explicit `cmap`, `bluered_cjc` is used.

![palette](examples/example_palette.png)

## Styles

```python
from cjcplot import use_style, available_styles

available_styles()                 # bundled styles, e.g. ['cjc']
use_style("cjc")                   # a bundled style
use_style("path/to/my_style")      # your own style folder
use_style("path/to/my.mplstyle")   # a single matplotlib style file
```

A style folder `my_style/` contains `my_style.mplstyle` (fonts, ticks, dpi) and
optionally `colors.py` with `PALETTE`, `COLORMAPS`, `DEFAULT_COLORMAP` and
`DIVERGING_COLORMAP`. To add a style to the package, copy `src/cjcplot/styles/cjc/`,
rename the folder and its `.mplstyle`, and edit both files.

**Keep `styles/cjc/`:** it is the built-in default that importing cjcplot applies.
Add your own style next to it instead of replacing it. If it is missing, cjcplot
warns on import and falls back to matplotlib's default style.

## License

MIT, see [LICENSE](LICENSE).
