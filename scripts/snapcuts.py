import json,numpy as np,sys
from scipy.ndimage import uniform_filter1d
d=sys.argv[1]; env=uniform_filter1d(np.load(d+'/env10.npy'),3)
c=json.load(open(d+'/edl_final.json'))['clips']
for i in range(len(c)-1):
    e,s=c[i][2],c[i+1][1]
    if s-e<5: continue
    ie=int(e*100); w=env[ie-30:ie+8]; k=int(np.argmin(w)); ne=(ie-30+k+1)/100
    js=int(s*100); w2=env[js-8:js+30]; k2=int(np.argmin(w2)); ns=(js-8+k2)/100
    ne=round(ne*30)/30; ns=round(ns*30)/30
    print('%.2f->%.2f (%.1f dB) | %.2f->%.2f (%.1f dB)'%(e,ne,env[int(ne*100)-1],s,ns,env[int(ns*100)]))
    c[i][2]=ne; c[i+1][1]=ns
json.dump(dict(clips=c),open(d+'/edl_final.json','w'))
