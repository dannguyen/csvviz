from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from csvviz.exceptions import OutputError

if TYPE_CHECKING:
    from matplotlib.figure import Figure

VALID_EXTENSIONS = {".png", ".svg", ".pdf"}


def has_display() -> bool:
    """Best-effort detection of a graphical display."""
    if sys.platform.startswith("linux"):
        return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))
    if sys.platform == "darwin":
        # macOS GUI doesn't use DISPLAY; SSH session means no GUI.
        return not os.environ.get("SSH_CONNECTION")
    if sys.platform.startswith("win"):
        return True
    return False


def fallback_path(input_path: str | None, chart_type: str) -> Path:
    stem = Path(input_path).stem if input_path else "stdin"
    return Path.cwd() / f"{stem}-{chart_type}.png"


def deliver(
    figure: "Figure",
    *,
    chart_type: str,
    input_path: str | None,
    output: Path | None,
    no_show: bool,
    dpi: int,
) -> None:
    """Show the figure or save it to disk per the spec's §2 decision table."""
    if output is not None:
        _save(figure, output, dpi)
        print(f"wrote {output}", file=sys.stderr)
        return

    if no_show:
        path = fallback_path(input_path, chart_type)
        _save(figure, path, dpi)
        print(f"wrote {path}", file=sys.stderr)
        return

    if has_display():
        import matplotlib.pyplot as plt

        plt.show()
        return

    path = fallback_path(input_path, chart_type)
    _save(figure, path, dpi)
    print(f"wrote {path} (no display detected)", file=sys.stderr)


def _save(figure: "Figure", path: Path, dpi: int) -> None:
    ext = path.suffix.lower()
    if ext not in VALID_EXTENSIONS:
        raise OutputError(
            f"output extension '{ext}' not supported; use one of {sorted(VALID_EXTENSIONS)}"
        )
    figure.savefig(path, dpi=dpi, bbox_inches="tight")
