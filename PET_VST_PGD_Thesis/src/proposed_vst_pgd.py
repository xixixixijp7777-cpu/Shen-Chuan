"""Adaptive variance-stabilized projected gradient descent."""
import numpy as np
from .operators import dx,dy,dxt,dyt,dxx,dyy,dxy,dxyt,edge_weight

def anscombe(y_counts): return 2*np.sqrt(np.maximum(y_counts,0)+3/8)
def inverse_anscombe(u): return np.maximum((u/2)**2-3/8,0)

def energy_grad(u,z,w,l1,l2,eps=1e-3):
    ux,uy=dx(u),dy(u); q=np.sqrt(ux*ux+uy*uy+eps*eps)
    a,b,c=dxx(u),dxy(u),dyy(u); r=np.sqrt(a*a+2*b*b+c*c+eps*eps)
    e=.5*np.sum((u-z)**2)+l1*np.sum(w*q)+l2*np.sum((1-w)*r)
    g=(u-z)+l1*(dxt(w*ux/q)+dyt(w*uy/q))
    g+=l2*(dxx((1-w)*a/r)+2*dxyt((1-w)*b/r)+dyy((1-w)*c/r))
    return float(e),g

def solve(y, peak, l1=.10, l2=.035, max_iter=120, tol=2e-5,
          adaptive=True, use_vst=True, fixed_step=False, gt=None):
    counts=np.maximum(y*peak,0)
    z=anscombe(counts) if use_vst else counts
    w=edge_weight(z) if adaptive else np.full_like(z,.5)
    u=z.copy(); hist=[]; prev_u=prev_g=None; step=.08
    for k in range(max_iter):
        e,g=energy_grad(u,z,w,l1,l2)
        if fixed_step: step=.015
        elif prev_u is not None:
            s=(u-prev_u).ravel(); yy=(g-prev_g).ravel()
            step=float(np.clip(np.dot(s,s)/(abs(np.dot(s,yy))+1e-12),1e-4,.2))
        # Armijo safeguard stabilizes the BB proposal.
        trial=step
        for _ in range(12):
            un=np.maximum(u-trial*g,0)
            en,_=energy_grad(un,z,w,l1,l2)
            if en <= e-1e-4*trial*np.sum((un-u)**2)/(trial**2+1e-12): break
            trial*=.5
        rel=float(np.linalg.norm(un-u)/(np.linalg.norm(u)+1e-12))
        x_iter=inverse_anscombe(un)/peak if use_vst else un/peak
        rei=(float(np.linalg.norm(x_iter-gt)/(np.linalg.norm(gt)+1e-12))
             if gt is not None else np.nan)
        hist.append({'Iteration':k+1,'Objective':en,'RelativeChange':rel,
                     'RelativeError':rei,'StepSize':trial})
        prev_u,prev_g=u,g; u=un; step=trial
        if rel<tol and k>=10: break
    x=inverse_anscombe(u)/peak if use_vst else u/peak
    return np.clip(x,0,1.5),hist,w
