# Export figures from the running Colab presentation experiments.
import json, zipfile
from pathlib import Path
from google.colab import files
out = Path('/content/presentation-export-2026-10-18')
out.mkdir(exist_ok=True)
plt.rcParams.update({'font.size':15,'axes.titlesize':18,'axes.labelsize':15,'legend.fontsize':13,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'#FAFAF6','axes.facecolor':'#FAFAF6','savefig.facecolor':'#FAFAF6'})
palette = ['#2864A5','#C77D24','#007F78']
def save(name):
    plt.tight_layout()
    plt.savefig(out / name, dpi=180, bbox_inches='tight')
    plt.close()
fig, ax = plt.subplots(figsize=(9,4.5))
vc = df['label'].value_counts()
vals=[100*vc[0]/len(df),100*vc[1]/len(df)]
ax.barh(['Normal','Attack'],vals,color=['#007F78','#BC4D39'],height=0.5)
for i,v in enumerate(vals): ax.text(v+1,i,f'{v:.1f}%  ({vc[i]:,})',va='center')
ax.set_xlim(0,115);ax.set_xlabel('Share of cleaned records (%)');ax.set_xticks([0,25,50,75,100]);ax.set_title('117,922 records after cleaning')
save('class-balance.png')
def compare(names,filename):
    fig,ax=plt.subplots(figsize=(11.5,4.4))
    for name,color in zip(names,palette):
        h=presentation_runs[name]['history']['val_loss']
        ax.plot(range(1,len(h)+1),h,label=f'{name}  (best {min(h):.4f})',color=color,linewidth=2.5)
    ax.set_yscale('log');ax.set_xlabel('Epoch');ax.set_ylabel('Validation loss (log scale)');ax.grid(alpha=.18);ax.legend(loc='upper right')
    ax.xaxis.set_major_locator(MaxNLocator(integer=True));save(filename)
compare(['SGD 0.1','Momentum 0.01','Adam 0.001'],'optimizers.png')
compare(['Adam 0.00001','Adam 0.1','Adam 0.001'],'learning-rates.png')
o=presentation_runs['Overfit'];e=presentation_runs['Early stopping'];h=o['history']
fig,ax=plt.subplots(figsize=(9.4,4.7))
ax.plot(range(1,len(h['train_loss'])+1),h['train_loss'],color='#2864A5',label='Training loss',linewidth=2)
ax.plot(range(1,len(h['val_loss'])+1),h['val_loss'],color='#BC4D39',label='Validation loss',linewidth=2)
ax.axvline(o['best_epoch'],color='#007F78',linestyle=':',label=f"Best validation: epoch {o['best_epoch']}")
ax.set_yscale('log');ax.set_xlabel('Epoch');ax.set_ylabel('Loss (log scale)');ax.grid(alpha=.18);ax.legend(loc='lower right')
save('overfitting.png')
bm=np.array(presentation_runs['Adam 0.001']['confusion']);ratios=bm/bm.sum(axis=1,keepdims=True)
fig,ax=plt.subplots(figsize=(7.2,4.8))
ax.imshow(ratios,cmap='Blues',vmin=0,vmax=1)
for i in range(2):
    for j in range(2): ax.text(j,i,f'{bm[i,j]:,}\n{ratios[i,j]:.2%}',ha='center',va='center',color='white' if ratios[i,j]>.5 else '#172C3C',fontsize=23)
ax.set_xticks([0,1],['Normal','Attack']);ax.set_yticks([0,1],['Normal','Attack']);ax.set_xlabel('Predicted');ax.set_ylabel('Actual')
save('confusion.png')
(out/'colab-results.json').write_text(json.dumps({'metadata':meta,'runs':presentation_runs},indent=2))
bundle='/content/presentation-colab-2026-10-18.zip'
with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
    for p in out.iterdir(): z.write(p,p.name)
print('EXPORTED: '+', '.join(p.name for p in out.iterdir()))
files.download(bundle)
