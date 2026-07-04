from pathlib import Path
import json
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SEED = 20260627

def ensure_dirs():
    for p in [ROOT/'data/raw', ROOT/'data/processed', ROOT/'data/figures',
              ROOT/'data/png_visualizations', ROOT/'results', ROOT/'thesis/figures']:
        p.mkdir(parents=True, exist_ok=True)

def save_json(obj, path):
    Path(path).write_text(json.dumps(obj, indent=2), encoding='utf-8')

def normalize(x):
    x = np.asarray(x, dtype=np.float64)
    lo, hi = x.min(), x.max()
    return (x-lo)/(hi-lo+1e-12)

