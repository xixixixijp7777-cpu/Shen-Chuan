import sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
import numpy as np, pandas as pd
from src.generate_data import generate,DOSES
from src.proposed_vst_pgd import solve
from src.metrics import evaluate
from src.utils import ensure_dirs

def run():
    ensure_dirs()
    if not (ROOT/'data/ground_truth.npy').exists(): generate()
    gt=np.load(ROOT/'data/ground_truth.npy'); y=np.load(ROOT/'data/lowdose_25.npy'); peak=DOSES['25']
    configs={'No Anscombe':dict(use_vst=False),'No adaptive weight':dict(adaptive=False),
             'Fixed-step PGD':dict(fixed_step=True),'Complete method':{}}
    rows=[]
    for name,kw in configs.items():
        t=time.perf_counter(); x,h,_=solve(y,peak,l1=2.0,l2=.5,max_iter=140,gt=gt,**kw); rt=time.perf_counter()-t
        m=evaluate(gt,np.clip(x,0,1)); m.update({'Variant':name,'Runtime':rt,'Iterations':len(h)}); rows.append(m)
        np.save(ROOT/f'data/processed/ablation_{name.lower().replace(" ","_")}.npy',x)
    pd.DataFrame(rows).to_csv(ROOT/'results/ablation_results.csv',index=False)
    print(pd.DataFrame(rows).to_string(index=False))
if __name__=='__main__': run()
