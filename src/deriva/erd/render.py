import shutil
import subprocess
import sys
from pathlib import Path


def _install_hint() -> str:
    if sys.platform == "darwin":
        return "brew install graphviz"
    if sys.platform.startswith("linux"):
        return "sudo dnf install graphviz (or: sudo apt install graphviz)"
    return "see https://graphviz.org/download/"


def render(
    dot_source: str, output_path: Path, layout: str = "dot", fmt: str = "pdf"
) -> Path:
    """
    Write the DOT source next to output_path, then render it.

    The .dot is always written first so a missing graphviz still leaves
    something useful on disk.
    """
    dot_path = output_path.with_suffix(".dot")
    dot_path.write_text(dot_source, encoding="utf-8")

    binary = shutil.which("dot")
    if binary is None:
        raise RuntimeError(
            f"graphviz not found, wrote {dot_path} only. Install it with: {_install_hint()}"
        )

    # -K picks the engine. The layout attribute is deliberately left out of the
    # emitted file so one .dot can be re-rendered with every engine.
    subprocess.run(
        [binary, f"-K{layout}", f"-T{fmt}", str(dot_path), "-o", str(output_path)],
        check=True,
    )
    return dot_path
