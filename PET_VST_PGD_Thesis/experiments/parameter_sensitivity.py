import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
import numpy as np,pandas as pd
from src.generate_data import generate,DOSES
from src.proposed_vst_pgd import solve
from src.metrics import evaluate
from src.utils import ensure_dirs

def run():
    ensure_dirs()
    if not (ROOT/'data/ground_truth.npy').exists(): generate()
    gt=np.load(ROOT/'data/ground_truth.npy'); y=np.load(ROOT/'data/lowdose_25.npy'); rows=[]
    for l1 in [.8,1.2,1.6,2.0]:
        for l2 in [.2,.35,.5,.7]:
            x,h,_=solve(y,DOSES['25'],l1=l1,l2=l2,max_iter=80,gt=gt)
            m=evaluate(gt,np.clip(x,0,1)); rows.append({'Lambda1':l1,'Lambda2':l2,**m,'Iterations':len(h)})
    pd.DataFrame(rows).to_csv(ROOT/'results/parameter_sensitivity.csv',index=False)
    print(pd.DataFrame(rows)[['Lambda1','Lambda2','PSNR','SSIM']].to_string(index=False))
if __name__=='__main__': run()
