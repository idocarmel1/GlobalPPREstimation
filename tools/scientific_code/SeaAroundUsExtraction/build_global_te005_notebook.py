from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from nbclient import NotebookClient  # noqa: E402
import nbformat  # noqa: E402

from ppr_pipeline.notebook import build_scope_validation_notebook  # noqa: E402


def main() -> None:
    path = build_scope_validation_notebook(
        ROOT / "notebooks" / "global_te005_validation.ipynb",
        scope_label="global_te005",
        output_directory="global_output_te005",
        unit_description="all 66 LMEs and 18 High Seas units at TE=0.05",
    )
    notebook = nbformat.read(path, as_version=4)
    client = NotebookClient(
        notebook,
        timeout=600,
        kernel_name="python3",
        resources={"metadata": {"path": str(ROOT)}},
    )
    client.execute()
    nbformat.write(notebook, path)
    print(path)


if __name__ == "__main__":
    main()
