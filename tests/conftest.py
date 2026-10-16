"""Shared test setup: headless backend, and a clean style and figure state per test."""

import matplotlib

# Draw in memory; CI machines have no screen. Must run before pyplot is imported.
matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import pytest  # noqa: E402

import cjcplot  # noqa: E402


@pytest.fixture(autouse=True)
def _clean_state():
    """Start every test from the cjc style and close its figures afterwards."""
    cjcplot.use_style("cjc")
    yield
    plt.close("all")
