import numpy as np, json, sys
from scipy.ndimage import uniform_filter1d, percentile_filter
e=np.load('env.npy'); d=20*np.log10(e[0])
ds=uniform_filter1d(d,3); fl=percentile_filter(ds,10,size=600)
TH=float(sys.argv[1])
act=ds>fl+TH
segs=[json.loads(l) for l in open('trans_A.jsonl')]
for s in segs:
    for (a,b,w,p) in s['words']:
        if p<0.3: continue
        c=(a+b)/2; h=min((b-a)/2,0.3)
        act[int((c-h)*10):int((c+h)*10)+1]=True
print('act',act.mean())
np.save('act.npy',act)
