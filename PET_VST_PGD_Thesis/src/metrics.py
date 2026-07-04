import numpy as np
from skimage.metrics import peak_signal_noise_ratio, structural_similarity
from scipy.ndimage import sobel

def evaluate(gt, x):
    gt=np.asarray(gt); x=np.asarray(x)
    rmse=float(np.sqrt(np.mean((x-gt)**2)))
    re=float(np.linalg.norm(x-gt)/(np.linalg.norm(gt)+1e-12))
    gg=np.hypot(sobel(gt,0),sobel(gt,1)).ravel()
    gx=np.hypot(sobel(x,0),sobel(x,1)).ravel()
    epi=float(np.dot(gg,gx)/(np.linalg.norm(gg)*np.linalg.norm(gx)+1e-12))
    return {'PSNR':float(peak_signal_noise_ratio(gt,x,data_range=1.0)),
            'SSIM':float(structural_similarity(gt,x,data_range=1.0)),
            'RMSE':rmse,'RE':re,'EPI':epi}

