from pathlib import Path
from unittest.mock import patch

import matplotlib
import matplotlib.pyplot as plt
import pytest

from csvviz.exceptions import OutputError
from csvviz.output import deliver, has_display, fallback_path


def _make_figure():
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [4, 5, 6])
    return fig


def test_has_display_linux_with_display():
    with patch("csvviz.output.sys.platform", "linux"):
        with patch.dict("os.environ", {"DISPLAY": ":0"}, clear=True):
            assert has_display() is True


def test_has_display_linux_without_display():
    with patch("csvviz.output.sys.platform", "linux"):
        with patch.dict("os.environ", {}, clear=True):
            assert has_display() is False


def test_has_display_linux_with_wayland():
    with patch("csvviz.output.sys.platform", "linux"):
        with patch.dict("os.environ", {"WAYLAND_DISPLAY": "wayland-0"}, clear=True):
            assert has_display() is True


def test_has_display_macos_local():
    with patch("csvviz.output.sys.platform", "darwin"):
        with patch.dict("os.environ", {}, clear=True):
            assert has_display() is True


def test_has_display_macos_ssh():
    with patch("csvviz.output.sys.platform", "darwin"):
        with patch.dict("os.environ", {"SSH_CONNECTION": "1.2.3.4"}, clear=True):
            assert has_display() is False


def test_has_display_windows():
    with patch("csvviz.output.sys.platform", "win32"):
        with patch.dict("os.environ", {}, clear=True):
            assert has_display() is True


def test_fallback_path_uses_csv_stem():
    p = fallback_path("data/sales.csv", "bar")
    assert p.name == "sales-bar.png"


def test_fallback_path_for_stdin():
    p = fallback_path(None, "hist")
    assert p.name == "stdin-hist.png"


def test_deliver_saves_to_output_path(tmp_path):
    fig = _make_figure()
    out = tmp_path / "chart.png"
    deliver(fig, chart_type="bar", input_path="x.csv", output=out, no_show=False, dpi=100)
    assert out.exists()
    assert out.stat().st_size > 0


def test_deliver_unknown_extension_raises(tmp_path):
    fig = _make_figure()
    out = tmp_path / "chart.xyz"
    with pytest.raises(OutputError):
        deliver(fig, chart_type="bar", input_path="x.csv", output=out, no_show=False, dpi=100)


def test_deliver_no_show_writes_fallback(tmp_path, monkeypatch):
    fig = _make_figure()
    monkeypatch.chdir(tmp_path)
    deliver(fig, chart_type="bar", input_path="data.csv", output=None, no_show=True, dpi=100)
    assert (tmp_path / "data-bar.png").exists()


def test_deliver_headless_writes_fallback(tmp_path, monkeypatch):
    fig = _make_figure()
    monkeypatch.chdir(tmp_path)
    with patch("csvviz.output.has_display", return_value=False):
        deliver(fig, chart_type="bar", input_path="data.csv", output=None, no_show=False, dpi=100)
    assert (tmp_path / "data-bar.png").exists()
