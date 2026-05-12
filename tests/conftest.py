import matplotlib

matplotlib.use("Agg")

import pytest


@pytest.fixture(autouse=True)
def _close_figures():
    yield
    import matplotlib.pyplot as plt

    plt.close("all")
