"""Finite-difference operators with periodic boundary conditions and adjoints."""
import numpy as np

def dx(u): return np.roll(u,-1,axis=1)-u
def dy(u): return np.roll(u,-1,axis=0)-u
def dxt(p): return np.roll(p,1,axis=1)-p
def dyt(p): return np.roll(p,1,axis=0)-p
def dxx(u): return np.roll(u,-1,1)-2*u+np.roll(u,1,1)
def dyy(u): return np.roll(u,-1,0)-2*u+np.roll(u,1,0)
def dxy(u): return dx(dy(u))
def dxyt(p): return dyt(dxt(p))

def gradient_magnitude(u, eps=1e-12):
    return np.sqrt(dx(u)**2+dy(u)**2+eps)

def edge_weight(z):
    """Robust, normalized structure weight: near 0 on edges, near 1 in flats."""
    g=gradient_magnitude(z)
    scale=np.percentile(g,90)+1e-12
    return np.exp(-np.minimum(g/scale,4.0)**2)

