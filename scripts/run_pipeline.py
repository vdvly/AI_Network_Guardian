"""Execute the data-preparation notebooks and capture proof artifacts."""
from __future__ import annotations

import json
import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.show = lambda *args, **kwargs: None


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ROOT / "notebooks"
BUILD = ROOT / "build"
PLOTS = ROOT / "plots"
NOTEBOOK_NAMES = [
    "01_data_cleaning.ipynb",
    "02_data_transformation.ipynb",
    "03_data_integration.ipynb",
    "04_data_enrichment.ipynb",
]


def run_notebook(path: Path, namespace: dict[str, object], graph_number: list[int]) -> None:
    notebook = json.loads(path.read_text(encoding="utf-8"))
    for cell_number, cell in enumerate(notebook["cells"]):
        if cell["cell_type"] != "code":
            continue
        try:
            exec(compile("".join(cell["source"]), str(path), "exec"), namespace)
        except Exception as error:
            raise RuntimeError(f"{path.name}, code cell {cell_number} failed") from error


def save_graphs(graph_number: list[int]) -> None:
    figure_numbers = plt.get_fignums()
    for figure_number in figure_numbers:
        graph_number[0] += 1
        filename = f"graph_{graph_number[0]:02d}.png"
        for output_directory in (BUILD, PLOTS):
            plt.figure(figure_number).savefig(
                output_directory / filename,
                dpi=120,
                bbox_inches="tight",
            )
    plt.close("all")


def main() -> None:
    BUILD.mkdir(exist_ok=True)
    PLOTS.mkdir(exist_ok=True)
    graph_number = [0]
    original_directory = Path.cwd()
    os.chdir(NOTEBOOKS)
    namespace: dict[str, object] = {"display": print}
    completed = []
    try:
        for notebook_name in NOTEBOOK_NAMES:
            run_notebook(NOTEBOOKS / notebook_name, namespace, graph_number)
            save_graphs(graph_number)
            completed.append(notebook_name)
    finally:
        os.chdir(original_directory)

    manifest = {
        "status": "success",
        "notebooks": completed,
        "graphs": sorted(path.name for path in BUILD.glob("graph_*.png")),
        "plot_directory": str(PLOTS.relative_to(ROOT)),
        "processed_outputs": sorted(
            path.name for path in (ROOT / "data" / "processed").iterdir()
        ),
        "model_outputs": sorted(path.name for path in (ROOT / "models").iterdir()),
    }
    (BUILD / "pipeline_success.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
