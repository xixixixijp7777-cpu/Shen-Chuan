"""Run all comparison methods on 50%, 25%, and 10% simulated doses."""
import sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
import numpy as np
import pandas as pd
from src.generate_data import generate, DOSES
from src.metrics import evaluate
from src.methods import gaussian,nlm,tv_gd,proposed,timed
from src.utils import ensure_dirs

def run():
    ensure_dirs()
    if not (ROOT/'data/ground_truth.npy').exists(): generate()
    gt=np.load(ROOT/'data/ground_truth.npy'); rows=[]; conv=[]
    for dose in ['50','25','10']:
        y=np.load(ROOT/f'data/lowdose_{dose}.npy'); peak=DOSES[dose]
        cases={}
        cases['Low-dose']=((y,None),0.0)
        (x,_),rt=timed(gaussian,y); cases['Gaussian']=((x,None),rt)
        (x,_),rt=timed(nlm,y); cases['NLM']=((x,None),rt)
        (x,h),rt=timed(tv_gd,y); cases['TV-GD']=((x,h),rt)
        (out,rt)=timed(proposed,y,peak,l1=2.0,l2=.5,max_iter=140,gt=gt)
        x,h,w=out; cases['Adaptive VST-PGD']=((x,h),rt)
        np.save(ROOT/f'data/processed/weight_{dose}.npy',w)
        for method,((x,h),rt) in cases.items():
            np.save(ROOT/f'data/processed/{dose}_{method.lower().replace(" ","_").replace("-","_")}.npy',x)
            m=evaluate(gt,np.clip(x,0,1)); m.update({'Dose Level':f'{dose}%','Method':method,
                    'Runtime':rt,'Iterations':len(h) if h else 0}); rows.append(m)
            if h:
                for q in h: conv.append({'Dose Level':f'{dose}%','Method':method,**q})
        print(f'Finished {dose}% dose.')
    cols=['Dose Level','Method','PSNR','SSIM','RMSE','RE','EPI','Runtime','Iterations']
    pd.DataFrame(rows)[cols].to_csv(ROOT/'results/metrics.csv',index=False)
    pd.DataFrame(conv).to_csv(ROOT/'results/convergence.csv',index=False)
    print(pd.DataFrame(rows)[cols].to_string(index=False))

if __name__=='__main__': run()
