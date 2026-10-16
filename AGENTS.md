# AGENTS.md — cjcplot

Guidance for AI coding agents (and humans) working in this repository.

cjcplot makes publication-ready matplotlib figures sized to a LaTeX text width,
with one consistent, switchable style.

## Commands

```bash
pip install -e ".[test]"           # editable install with pytest
pytest                             # run all tests (headless, Agg backend)
python examples/example_plot_2d.py # each example saves its PNG next to itself
```

## Public API

Scripts import only from the package root, never from submodules:

```python
from cjcplot import plot_1d, plot_histogram_1d, plot_2d, plot_3d
from cjcplot import use_style, available_styles, style_colors, style_diverging_cmap
from cjcplot import colors_from_cmap, colormap_from_colors, join_colormaps, truncate_colormap, register_colormap
```

## Package layout

```
src/cjcplot/
  __init__.py        public API; applies the cjc style on import
  _figure.py         shared: figure sizing, ticks, final axis formatting, per-trace helpers
  plot_1d.py         plot_1d, plot_histogram_1d
  plot_2d.py         plot_2d
  plot_3d.py         plot_3d (placeholder, not implemented yet)
  styles/
    __init__.py      use_style(), available_styles(), style_colors(), style_diverging_cmap()
    _colormap_tools.py  colors_from_cmap(), colormap_from_colors(), join_colormaps(),
                        truncate_colormap(), register_colormap()
    cjc/
      cjc.mplstyle   fonts, ticks, dpi, line widths
      colors.py      PALETTE, COLORMAPS, DEFAULT_CMAP, DIVERGING_CMAP
```

## Design rules for every plot function

- Returns `(fig, ax)`.
- Accepts `ax=` to draw into existing axes; then no new figure and no `plt.show()`.
- Limits are `(min, max)` tuples with the same naming: `xlim`, `ylim`, `clim` (colour).
- Figure size: `fig_aspect_ratio = (width, height)` as fractions of `fig_textwidth_pt`.
  Figures use matplotlib's "compressed" layout, so `aspect="equal"` plots shrink to fit.
- Colorbar size: `cbar_aspect_ratio = (width, height)` as fractions of the plot box
  (the area inside the axes, excluding title and labels).
- One trace or a list of traces. Per-trace options shorter than the trace list are
  filled by the shared helpers in `_figure.py` (`cycle_to_length`, `pad_to_length`,
  `broadcast_to_length`), never by local copies.
- Styling (fonts, dpi, colours, default colormap, line widths) lives in the style
  folder, never hard-coded in plot functions.
- Defaults that come from the style are `None` in the signature (`colors=None`,
  `cmap=None`) and are resolved at call time, so they follow `use_style()`.
- Dependencies: numpy and matplotlib only.

## Styles

- Importing cjcplot applies `styles/cjc/`. It is the built-in default and must stay:
  add new styles next to it. If it is missing, import warns and keeps matplotlib's defaults.
- `use_style(name_or_path)` takes a bundled style name, a style folder, or a single
  `.mplstyle` file. It first resets matplotlib to its defaults.
- A style folder `<name>/` holds `<name>.mplstyle` and optionally `colors.py`.
  `colors.py` may define `PALETTE`, `COLORMAPS`, `DEFAULT_CMAP`, `DIVERGING_CMAP`
  (all optional); see `styles/cjc/colors.py` for the reference.
- Scripts get line colours with `style_colors()[i]`, not hard-coded hex values.
- New group styles: copy `styles/cjc/`, rename folder and `.mplstyle`, edit both.

## Coding conventions

- Every logical block inside a function gets a one-line `#` comment saying why it exists.
- SI units need no suffix; non-SI or scaled values carry one (`_pt`, `_mm`, `_ps`, `_thz`, `_um`).
- Physicist-first API: descriptive argument names over programmer idioms.
- No helper functions copied between modules; shared code goes in `_figure.py`.
- Remove unused code instead of leaving it commented out.
- Python 3.10 compatible (no syntax newer than 3.10).

## Tests

- `tests/` runs headless: `conftest.py` selects the Agg backend and resets the style
  before every test.
- Every option group has a test; wrong shapes and conflicting options raise
  `ValueError`s with clear messages, and those messages are tested.
- GitHub Actions (`.github/workflows/tests.yml`) runs `pytest` on Python 3.10 and 3.14
  for every push and pull request.
