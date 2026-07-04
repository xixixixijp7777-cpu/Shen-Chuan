"""Generate publication-ready figures exclusively from saved arrays and CSVs."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np,pandas as pd
import matplotlib.pyplot as plt
from src.utils import ROOT,ensure_dirs

plt.rcParams.update({
    'font.family':'serif',
    'font.serif':['Times New Roman','Times','TeX Gyre Termes','DejaVu Serif'],
    'font.size':9,
    'figure.dpi':150,
    'savefig.dpi':300,
    'axes.spines.top':False,
    'axes.spines.right':False,
})
METHODS=['Low-dose','Gaussian','NLM','TV-GD','Adaptive VST-PGD']
SLUG=lambda s:s.lower().replace(' ','_').replace('-','_')

def save(fig,name): fig.tight_layout(); fig.savefig(ROOT/f'thesis/figures/{name}.pdf',bbox_inches='tight'); fig.savefig(ROOT/f'thesis/figures/{name}.png',bbox_inches='tight'); plt.close(fig)

def generate_figures():
    ensure_dirs(); (ROOT/'thesis/tables').mkdir(parents=True,exist_ok=True)
    gt=np.load(ROOT/'data/ground_truth.npy'); dose='25'
    imgs={m:np.load(ROOT/f'data/processed/{dose}_{SLUG(m)}.npy') for m in METHODS}
    fig,axs=plt.subplots(2,3,figsize=(10,6.6)); panels=[('Ground truth',gt)]+list(imgs.items())
    for ax,(name,x) in zip(axs.flat,panels): ax.imshow(x,cmap='hot',vmin=0,vmax=1); ax.set_title(name); ax.axis('off')
    save(fig,'method_comparison')
    fig,allaxs=plt.subplots(1,6,figsize=(12,2.5),gridspec_kw={'width_ratios':[1,1,1,1,1,.045]})
    axs,cbax=allaxs[:5],allaxs[5]
    for ax,(name,x) in zip(axs,imgs.items()): im=ax.imshow(np.abs(x-gt),cmap='magma',vmin=0,vmax=.25); ax.set_title(name); ax.axis('off')
    fig.colorbar(im,cax=cbax,label='Absolute error'); save(fig,'error_maps')
    roi=(slice(85,120),slice(145,180)); fig,axs=plt.subplots(1,6,figsize=(12,2.2))
    for ax,(name,x) in zip(axs,[('Ground truth',gt)]+list(imgs.items())): ax.imshow(x[roi],cmap='hot',vmin=0,vmax=1); ax.set_title(name,fontsize=8); ax.axis('off')
    save(fig,'zoom_in')
    met=pd.read_csv(ROOT/'results/metrics.csv'); sub=met[met['Dose Level']=='25%']
    fig,axs=plt.subplots(1,2,figsize=(9,3.2))
    for ax,col in zip(axs,['PSNR','SSIM']): ax.bar(sub.Method,sub[col],color=plt.cm.viridis(np.linspace(.15,.85,len(sub)))); ax.set_ylabel(col); ax.tick_params(axis='x',rotation=25)
    save(fig,'metric_bars')
    conv=pd.read_csv(ROOT/'results/convergence.csv'); c=conv[(conv['Dose Level']=='25%') & (conv['Method']=='Adaptive VST-PGD')]
    fig,axs=plt.subplots(1,2,figsize=(9,3.2))
    for method,g in c.groupby('Method'):
        axs[0].semilogy(g.Iteration,g.Objective,label=method); 
        if g.RelativeError.notna().any(): axs[1].plot(g.Iteration,g.RelativeError,label=method)
    axs[0].set(xlabel='Iteration',ylabel='Objective value'); axs[1].set(xlabel='Iteration',ylabel='Relative error'); axs[0].legend(); axs[1].legend(); save(fig,'convergence_curves')
    abl=pd.read_csv(ROOT/'results/ablation_results.csv'); fig,axs=plt.subplots(1,2,figsize=(9,3.2))
    for ax,col in zip(axs,['PSNR','SSIM']): ax.bar(abl.Variant,abl[col],color='#4C78A8'); ax.set_ylabel(col); ax.tick_params(axis='x',rotation=20)
    save(fig,'ablation_bars')
    ps=pd.read_csv(ROOT/'results/parameter_sensitivity.csv'); mat=ps.pivot(index='Lambda1',columns='Lambda2',values='PSNR')
    fig,ax=plt.subplots(figsize=(5.2,4)); im=ax.imshow(mat.values,cmap='viridis',aspect='auto'); ax.set_xticks(range(len(mat.columns)),mat.columns); ax.set_yticks(range(len(mat.index)),mat.index); ax.set(xlabel=r'$\lambda_2$',ylabel=r'$\lambda_1$')
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]): ax.text(j,i,f'{mat.iloc[i,j]:.2f}',ha='center',va='center',color='white',fontsize=8)
    fig.colorbar(im,ax=ax,label='PSNR (dB)'); save(fig,'parameter_heatmap')
    row=102; fig,ax=plt.subplots(figsize=(9,3.2)); ax.plot(gt[row],label='Ground truth',lw=2,color='black')
    for name,x in imgs.items(): ax.plot(x[row],label=name,alpha=.85); ax.set(xlabel='Pixel position',ylabel='Normalized activity'); ax.legend(ncol=3,fontsize=7)
    save(fig,'line_profile')
    # LaTeX tables are generated from measured CSVs and never hand-entered.
    lines=['\\begin{table}[tbp]','\\centering',
           '\\caption{Measured performance across dose levels.}','\\label{tab:metrics}',
           '\\setlength{\\tabcolsep}{3pt}',
           '\\begin{tabular}{@{}llrrrrrrr@{}}\\toprule',
           'Dose & Method & PSNR & SSIM & RMSE & RE & EPI & Time (s) & Iter.\\\\ \\midrule']
    for _,r in met.iterrows():
        dose=r['Dose Level'].replace('%',r'\%')
        lines.append(f"{dose} & {r.Method} & {r.PSNR:.2f} & {r.SSIM:.3f} & {r.RMSE:.4f} & {r.RE:.3f} & {r.EPI:.3f} & {r.Runtime:.4f} & {int(r.Iterations)} \\\\")
    lines+=['\\bottomrule\\end{tabular}','\\end{table}']
    (ROOT/'thesis/tables/metrics_table.tex').write_text('\n'.join(lines),encoding='utf-8')
    lines=['\\begin{table}[tbp]','\\centering',
           '\\caption{Ablation study at 25\\% dose.}','\\label{tab:ablation}',
           '\\setlength{\\tabcolsep}{3pt}',
           '\\begin{tabular}{@{}lrrrrrrr@{}}\\toprule',
           'Variant & PSNR & SSIM & RMSE & RE & EPI & Time (s) & Iter.\\\\ \\midrule']
    for _,r in abl.iterrows(): lines.append(f"{r.Variant} & {r.PSNR:.2f} & {r.SSIM:.3f} & {r.RMSE:.4f} & {r.RE:.3f} & {r.EPI:.3f} & {r.Runtime:.4f} & {int(r.Iterations)} \\\\")
    lines+=['\\bottomrule\\end{tabular}','\\end{table}']
    (ROOT/'thesis/tables/ablation_table.tex').write_text('\n'.join(lines),encoding='utf-8')
    proposed=met[met.Method=='Adaptive VST-PGD'].set_index('Dose Level')
    low=met[met.Method=='Low-dose'].set_index('Dose Level')
    nlm=met[met.Method=='NLM'].set_index('Dose Level')
    variants=abl.set_index('Variant')
    complete=variants.loc['Complete method']
    fixed=variants.loc['Fixed-step PGD']
    no_weight=variants.loc['No adaptive weight']
    best=ps.loc[ps.PSNR.idxmax()]
    macros=[
        f"\\newcommand{{\\ProposedPSNRFifty}}{{{proposed.loc['50%','PSNR']:.2f}}}",
        f"\\newcommand{{\\ProposedPSNRTwentyFive}}{{{proposed.loc['25%','PSNR']:.2f}}}",
        f"\\newcommand{{\\ProposedPSNRTen}}{{{proposed.loc['10%','PSNR']:.2f}}}",
        f"\\newcommand{{\\ProposedGainTwentyFive}}{{{proposed.loc['25%','PSNR']-low.loc['25%','PSNR']:.2f}}}",
        f"\\newcommand{{\\ProposedOverNLMTwentyFive}}{{{proposed.loc['25%','PSNR']-nlm.loc['25%','PSNR']:.2f}}}",
        f"\\newcommand{{\\ProposedIterFifty}}{{{int(proposed.loc['50%','Iterations'])}}}",
        f"\\newcommand{{\\ProposedIterTwentyFive}}{{{int(proposed.loc['25%','Iterations'])}}}",
        f"\\newcommand{{\\ProposedIterTen}}{{{int(proposed.loc['10%','Iterations'])}}}",
        f"\\newcommand{{\\AdaptiveWeightPSNRLoss}}{{{complete.PSNR-no_weight.PSNR:.2f}}}",
        f"\\newcommand{{\\FixedStepPSNR}}{{{fixed.PSNR:.2f}}}",
        f"\\newcommand{{\\FixedStepIterations}}{{{int(fixed.Iterations)}}}",
        f"\\newcommand{{\\FixedStepRuntimeRatio}}{{{fixed.Runtime/complete.Runtime:.1f}}}",
        f"\\newcommand{{\\BestLambdaOne}}{{{best.Lambda1:g}}}",
        f"\\newcommand{{\\BestLambdaTwo}}{{{best.Lambda2:g}}}",
        f"\\newcommand{{\\BestSensitivityPSNR}}{{{best.PSNR:.2f}}}",
    ]
    (ROOT/'thesis/tables/results_macros.tex').write_text('\n'.join(macros)+'\n',encoding='utf-8')
    print(f'Figures written to {ROOT/"thesis/figures"}.')
if __name__=='__main__': generate_figures()
