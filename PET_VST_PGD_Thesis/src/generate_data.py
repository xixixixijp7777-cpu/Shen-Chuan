"""Generate a reproducible 256x256 PET-like phantom and Poisson observations."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import matplotlib.pyplot as plt
from skimage.data import shepp_logan_phantom
from skimage.transform import resize
from src.utils import ROOT, SEED, ensure_dirs, normalize

DOSES = {"full": 120.0, "50": 60.0, "25": 30.0, "10": 12.0}

def make_phantom():
    x = resize(shepp_logan_phantom(), (256,256), anti_aliasing=True)
    yy, xx = np.mgrid[:256,:256]
    # Small hot lesions make edge preservation measurable.
    for cy, cx, r, amp in [(102,166,7,0.32),(148,91,6,0.25),(126,126,4,0.20)]:
        x += amp*np.exp(-((xx-cx)**2+(yy-cy)**2)/(2*(r/2.4)**2))
    return normalize(x)

def generate(seed=SEED):
    ensure_dirs(); rng=np.random.default_rng(seed); gt=make_phantom()
    np.save(ROOT/'data/ground_truth.npy', gt)
    np.save(ROOT/'data/raw/ground_truth.npy', gt)
    for name, peak in DOSES.items():
        counts=rng.poisson(peak*gt).astype(np.float64)
        obs=counts/peak
        np.save(ROOT/f'data/lowdose_{name}.npy', obs)
        np.save(ROOT/f'data/raw/lowdose_{name}.npy', obs)
        plt.imsave(ROOT/f'data/png_visualizations/lowdose_{name}.png', obs, cmap='hot', vmin=0, vmax=1)
    plt.imsave(ROOT/'data/png_visualizations/ground_truth.png', gt, cmap='hot', vmin=0, vmax=1)
    print(f'Generated data in {ROOT / "data"} (seed={seed}).')

if __name__=='__main__': generate()

