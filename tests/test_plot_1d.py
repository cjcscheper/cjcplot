"""plot_1d and plot_histogram_1d: traces, styling options, error checks."""

import matplotlib.pyplot as plt
import numpy as np
import pytest

import cjcplot

X = np.linspace(0.0, 1.0, 11)


def test_single_trace_returns_figure_and_axes_with_style_colour():
    fig, ax = cjcplot.plot_1d(X, X**2, fig_show=False)
    assert len(ax.get_lines()) == 1
    assert ax.get_lines()[0].get_color() == cjcplot.style_colors()[0]


def test_figure_size_follows_textwidth_and_aspect_ratio():
    fig, _ = cjcplot.plot_1d(X, X, fig_textwidth_pt=72.27, fig_aspect_ratio=(2.0, 1.0), fig_show=False)
    assert np.allclose(fig.get_size_inches(), (2.0, 1.0))


def test_colours_cycle_when_fewer_than_traces():
    _, ax = cjcplot.plot_1d([X, X, X], [X, 2 * X, 3 * X], colors=["red", "blue"], first_on_top=False, fig_show=False)
    assert [line.get_color() for line in ax.get_lines()] == ["red", "blue", "red"]


def test_mismatched_shapes_raise():
    with pytest.raises(ValueError, match="Trace 0 mismatch"):
        cjcplot.plot_1d(X, X[:-1], fig_show=False)
    with pytest.raises(ValueError, match="both be a single trace"):
        cjcplot.plot_1d([X, X], X, fig_show=False)


def test_yerr_shape_is_checked():
    with pytest.raises(ValueError, match="yerr_data trace 0 mismatch"):
        cjcplot.plot_1d(X, X, yerr_data=X[:-1], fig_show=False)


def test_single_error_array_is_shared_and_err_on_top_moves_bars_up():
    _, ax = cjcplot.plot_1d([X, X], [X, 2 * X], yerr_data=0.1 * X, err_on_top=True, fig_show=False)
    # One error-bar collection per trace, above the markers' zorder of 3.
    assert len(ax.collections) == 2
    assert all(c.get_zorder() > 3.0 for c in ax.collections)


def test_legend_contains_traces_and_reference_line_labels():
    _, ax = cjcplot.plot_1d(
        [X, X], [X, 2 * X],
        legend_labels=["a", "b"],
        vlines_pos=[0.5], vlines_labels=["edge"],
        hlines_pos=[0.2],
        fig_show=False,
    )
    labels = [text.get_text() for text in ax.get_legend().get_texts()]
    assert sorted(labels) == ["a", "b", "edge"]


def test_legend_follows_given_order_while_first_trace_is_on_top():
    _, ax = cjcplot.plot_1d([X, X], [X, 2 * X], legend_labels=["a", "b"], fig_show=False)
    assert [text.get_text() for text in ax.get_legend().get_texts()] == ["a", "b"]
    first, second = ax.get_lines()
    assert first.get_zorder() > second.get_zorder()


def test_histogram_legend_order_and_default_fill():
    _, ax = cjcplot.plot_histogram_1d([np.arange(10.0), np.arange(10.0) + 2], legend_labels=["a", "b"], fig_show=False)
    assert [text.get_text() for text in ax.get_legend().get_texts()] == ["a", "b"]
    first, second = ax.patches
    assert first.get_zorder() > second.get_zorder()
    assert first.get_fill() and np.isclose(first.get_alpha(), 0.8)


def test_none_legend_labels_are_left_out():
    _, ax = cjcplot.plot_1d([X, X, X, X], [X, 2 * X, 3 * X, 4 * X], legend_labels=["first", None, None, "last"], fig_show=False)
    assert [text.get_text() for text in ax.get_legend().get_texts()] == ["first", "last"]


def test_legend_reverse_reverses_entries():
    _, ax = cjcplot.plot_1d(
        [X, X], [X, 2 * X], legend_labels=["a", "b"], first_on_top=False, legend_reverse=True, fig_show=False
    )
    assert [text.get_text() for text in ax.get_legend().get_texts()] == ["b", "a"]


def test_scatter_only_trace_draws_markers_without_line():
    _, ax = cjcplot.plot_1d(X, X, line_show=False, scatter_show=True, fig_show=False)
    assert len(ax.get_lines()) == 0
    assert len(ax.collections) == 1


def test_draws_into_given_axes_without_new_figure():
    fig, ax = plt.subplots()
    figure_count = len(plt.get_fignums())
    out_fig, out_ax = cjcplot.plot_1d(X, X, ax=ax)
    assert out_ax is ax and out_fig is fig
    assert len(plt.get_fignums()) == figure_count


def test_explicit_ticks_and_label_mismatch():
    _, ax = cjcplot.plot_1d(X, X, yticks_pos=[0, 1], yticks_labels=["lo", "hi"], fig_show=False)
    assert [t.get_text() for t in ax.get_yticklabels()] == ["lo", "hi"]
    with pytest.raises(ValueError, match="yticks_pos and yticks_labels"):
        cjcplot.plot_1d(X, X, yticks_pos=[0, 1], yticks_labels=["lo"], fig_show=False)


def test_save_path_writes_file(tmp_path):
    path = tmp_path / "trace.png"
    cjcplot.plot_1d(X, X, save_path=str(path), fig_show=False)
    assert path.exists()


def test_histograms_share_bin_edges_and_accept_bin_range():
    rng = np.random.default_rng(0)
    _, ax = cjcplot.plot_histogram_1d(
        [rng.normal(0, 1, 500), rng.normal(1, 1, 500)], bins=20, bin_range=(-3, 4), fig_show=False
    )
    edges = [patch.get_path().vertices[:, 0] for patch in ax.patches]
    assert np.isclose(min(e.min() for e in edges), -3) and np.isclose(max(e.max() for e in edges), 4)


def test_histogram_density_plots_probability_density():
    rng = np.random.default_rng(1)
    samples = rng.normal(0, 1, 1000)
    density_values, _ = np.histogram(samples, bins=30, density=True)
    _, ax = cjcplot.plot_histogram_1d(samples, bins=30, density=True, fig_show=False)
    # The step outline's highest point is the tallest density bin, not a count.
    assert np.isclose(ax.patches[0].get_path().vertices[:, 1].max(), density_values.max())


def test_histogram_weights_shape_is_checked():
    with pytest.raises(ValueError, match="weights trace 0 mismatch"):
        cjcplot.plot_histogram_1d(np.ones(5), weights=np.ones(4), fig_show=False)


def test_histogram_draws_into_given_axes():
    fig, ax = plt.subplots()
    out_fig, out_ax = cjcplot.plot_histogram_1d(np.arange(10.0), ax=ax)
    assert out_ax is ax and out_fig is fig
