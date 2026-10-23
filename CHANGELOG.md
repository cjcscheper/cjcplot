# Changelog

All notable changes to cjcplot. Versions follow MAJOR.MINOR.PATCH: patch for
fixes, minor for new features, major for changes that break existing scripts.

## [Unreleased]

### Changed
- README: the example figures are grouped per example, each with a short
  explanation of what it shows.

## [0.2.0] - 2026-10-20

### Added
- `CHANGELOG.md`, a release badge and a pinned-version install command in the README.

### Changed
- **Breaking:** `colormap` is now written out in names: `colors_from_cmap` →
  `colors_from_colormap`, `style_diverging_cmap` → `style_diverging_colormap`, and in
  a style's `colors.py` `DEFAULT_CMAP` → `DEFAULT_COLORMAP`, `DIVERGING_CMAP` →
  `DIVERGING_COLORMAP`. The example `example_colors_from_cmap.py` is now
  `example_colors_from_colormap.py`. Keyword arguments keep matplotlib's `cmap=`.
- The version now lives only in `src/cjcplot/__init__.py`; `pyproject.toml` reads it from there.
- README: example images centred one per row, in a new order; the figure-size
  section now covers LaTeX, Word, PowerPoint and other documents; the quick
  start passes `x_data=` and `y_data=` and explains how to switch to your own
  style.
- Tests: every test has a docstring, and non-obvious lines a comment.
- Fuller explanations of the per-trace helpers and `POINTS_PER_INCH` in `_figure.py`.
- The histogram example uses more samples and finer bins, so it looks smooth.
- AGENTS.md: rules for keeping tests, docs and this changelog up to date.

### Fixed
- Type hints for `xlim`/`ylim` and `legend_loc` now match matplotlib's, so editors
  such as PyCharm no longer warn; `legend_loc` also autocompletes its allowed values.
- The same for `histtype` in `plot_histogram_1d` and `shading` in `plot_2d`.

## [0.1.0] - 2026-10-16

First release.

### Added
- `plot_1d`, `plot_histogram_1d` and `plot_2d`, sized as fractions of a
  document's text width; `plot_3d` as a placeholder.
- Switchable styles (`use_style`, `available_styles`, `style_colors`), with the
  bundled `cjc` style applied on import.
- cjc colormaps: `reds_cjc`, `blues_cjc`, `bluered_cjc` (diverging), and
  `blueyellow_cjc`, `yellowblue_cjc`, `yellowred_cjc`, `redyellow_cjc`.
- `colors_from_cmap` to sample line colours from a colormap.
- Colormap tools: `truncate_colormap`, `colormap_from_colors`,
  `join_colormaps`, `register_colormap`.
- Tests, examples and a GitHub Actions workflow.
