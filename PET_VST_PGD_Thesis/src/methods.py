import time
import numpy as np
from scipy.ndimage import gaussian_filter
from skimage.restoration import denoise_nl_means
from .operators import dx,dy,dxt,dyt
from .proposed_vst_pgd import solve

def gaussian(y): return gaussian_filter(y,1.0),0

def nlm(y):
    # Robust noise estimate from first differences; avoids a PyWavelets dependency.
    d=np.abs((y[:,1:]-y[:,:-1]).ravel())
    d=d[d>1e-10]
    sigma=float(np.median(d)/(0.6745*np.sqrt(2))+1e-6)
    return denoise_nl_means(y,h=.8*sigma,fast_mode=True,patch_size=5,
                            patch_distance=6,channel_axis=None,preserve_range=True),0

def tv_gd(y, lam=.08, max_iter=120, eps=1e-3):
    u=y.copy(); hist=[]; step=.12
    for k in range(max_iter):
        ux,uy=dx(u),dy(u); q=np.sqrt(ux*ux+uy*uy+eps*eps)
        g=u-y+lam*(dxt(ux/q)+dyt(uy/q)); un=np.maximum(u-step*g,0)
        rel=np.linalg.norm(un-u)/(np.linalg.norm(u)+1e-12); u=un
        hist.append({'Iteration':k+1,'Objective':.5*np.sum((u-y)**2)+lam*np.sum(q),'RelativeChange':rel})
        if rel<2e-5 and k>=10: break
    return u,hist

def timed(fn,*args,**kwargs):
    t=time.perf_counter(); out=fn(*args,**kwargs); return out,time.perf_counter()-t

def proposed(y,peak,**kw): return solve(y,peak,**kw)
