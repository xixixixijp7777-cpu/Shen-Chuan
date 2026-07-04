# Adaptive Variance-Stabilized Projected Gradient Descent for Low-Dose PET Image Preprocessing

This repository is a reproducible academic-paper project for simulated
low-dose PET preprocessing. The study combines the Anscombe variance-stabilizing
transform, an edge-adaptive first/second-order regularizer, non-negativity
projection, and a Barzilai-Borwein (BB) step safeguarded by Armijo backtracking.

## Reproduce the study

Python 3.9+ is recommended. From the project root:

```bash
pip install -r requirements.txt
python src/generate_data.py
python experiments/run_all_experiments.py
python experiments/ablation_study.py
python experiments/parameter_sensitivity.py
python src/visualization.py
```

The seed is fixed to `20260627`. The generated arrays include
`data/ground_truth.npy`, `data/lowdose_50.npy`, `data/lowdose_25.npy`, and
`data/lowdose_10.npy`; PNG previews are in `data/png_visualizations/`.
Processed arrays, measured CSV files, paper figures, and generated LaTeX tables
are written beneath `data/processed/`, `results/`, `thesis/figures/`, and
`thesis/tables/`, respectively. Running `python src/visualization.py` rebuilds
all paper figures, result tables, and numerical summary macros from the saved
arrays and CSV files.

## Compile the English paper

```bash
cd thesis
latexmk -xelatex main.tex
```

The paper is written entirely in English but uses a XeLaTeX university-style
font configuration. Times New Roman and SimSun are preferred; the source
automatically selects TeX Gyre Termes and FandolSong-Regular when those fonts
are unavailable. To compile manually with XeLaTeX, run the following commands
from `thesis/`:

```bash
xelatex main.tex
bibtex main
xelatex main.tex
xelatex main.tex
```

For Overleaf, upload the complete contents of the `thesis/` directory, set
`main.tex` as the main document, select **XeLaTeX** as the compiler, and choose
**Recompile**.

## Notes on interpretation

The study uses a synthetic activity phantom rather than patient data and is a
preprocessing experiment, not a clinical reconstruction study. Runtime is
machine-dependent. The inverse used here is the conventional algebraic inverse
requested for the study; an exact unbiased inverse is a useful extension.
