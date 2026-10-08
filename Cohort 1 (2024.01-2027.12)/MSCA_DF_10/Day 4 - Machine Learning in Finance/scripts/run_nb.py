#!/usr/bin/env python3
"""Execute a notebook from a clean kernel; cwd = notebooks/."""
import sys
import time
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbformat.validator import normalize

def main(rel: str) -> None:
    root = Path(__file__).resolve().parents[1]
    path = (root / rel).resolve()
    nb = nbformat.read(path, as_version=4)
    normalize(nb)
    for c in nb.cells:
        if c.cell_type == "code":
            c.outputs = []
            c.execution_count = None
    t0 = time.time()
    NotebookClient(
        nb,
        timeout=600,
        kernel_name="python3",
        resources={"metadata": {"path": str((root / "notebooks").resolve())}},
    ).execute()
    nbformat.write(nb, path)
    print(f"OK {path.name}  {time.time() - t0:.1f}s")

if __name__ == "__main__":
    main(sys.argv[1])
