import json, numpy as np, sys
from scipy.ndimage import maximum_filter1d
D=sys.argv[1]; FPS=30
ed=json.load(open(D+'/edl.json')); clips=[list(c) for c in ed['clips']]
env=np.load(D+'/env10.npy'); envs=maximum_filter1d(env,5)
words=[(a,b,w.strip().lower().strip('.,?!'),p) for l in open(D+'/trans_A.jsonl') for s in [json.loads(l)] for (a,b,w,p) in s['words']]
good=[(a,b) for a,b,w,p in words if p>=0.5 and w not in ('ha','haa','hmm')]
mids=np.array(sorted((a+b)/2 for a,b in good))
SIL=-48
CUTS=json.loads(sys.argv[2])
def lv(t0,t1): 
    i0,i1=int(t0*100),max(int(t0*100)+1,int(t1*100)); return env[i0:i1].max()
# --- A: extra pauses inside clips
newc=[]; npause=0; removed=0
for ang,s,e,spk in clips:
    i0,i1=int(s*100),int(e*100); q=envs[i0:i1]<SIL
    cur=s; k=0
    while k<len(q):
        if q[k]:
            j=k
            while j<len(q) and q[j]: j+=1
            r0,r1=s+k/100,s+j/100
            if r1-r0>=1.0 and not ((mids>r0+0.1)&(mids<r1-0.1)).any() and r0-cur>0.3 and e-r1>0.3:
                newc.append([ang,cur,r0+0.2,spk]); cur=r1-0.2; npause+=1; removed+=r1-r0-0.4
            k=j
        else: k+=1
    newc.append([ang,cur,e,spk])
clips=newc
print('extra pauses tightened:',npause,'removed %.1fs'%removed)
# --- B: boundary safety
fix_e=fix_s=0; flags=[]
for i in range(len(clips)-1):
    e=clips[i][2]; s=clips[i+1][1]
    if abs(e-s)<1e-6: continue
    if any(e<=b+0.01 and s>=a-0.01 for a,b in CUTS): continue   # manual content cut: keep chosen points
    # end side
    lim=min(e+0.6, s if s>e else e+0.6)
    e2=e
    for a,b in good:
        if a<e2<b: e2=b+0.04
    e2=min(e2,lim)
    while lv(e2-0.04,e2)>SIL+4 and e2<lim: e2+=0.01
    e2=min(e2,lim)
    s2=s
    for a,b in good:
        if a<s2<b: s2=a-0.04
    lo=max(s-0.6, e2 if e2<s else s-0.6)
    s2=max(s2,lo)
    while lv(s2,s2+0.04)>SIL+4 and s2>lo: s2-=0.01
    s2=max(s2,lo)
    if s2<=e2+1e-6: s2=e2   # gap closed -> play continuously
    if e2!=e: fix_e+=1
    if s2!=s: fix_s+=1
    clips[i][2]=e2; clips[i+1][1]=s2
    if (lv(e2-0.03,e2)>SIL+4 or lv(s2,s2+0.03)>SIL+4) and s2>e2:
        if s2-e2<0.6: s2=e2
        else:
            k=e2
            while lv(k-0.04,k)>SIL+4 and k>e2-0.8 and k>clips[i][1]+0.3: k-=0.01
            if lv(k-0.04,k)<=SIL+4: e2=k
            k=s2
            while lv(k,k+0.04)>SIL+4 and k<s2+0.8 and k<clips[i+1][2]-0.3: k+=0.01
            if lv(k,k+0.04)<=SIL+4: s2=k
        clips[i][2]=e2; clips[i+1][1]=s2
    if s2>e2 and (lv(e2-0.03,e2)>SIL+4 or lv(s2,s2+0.03)>SIL+4): flags.append((round(e2,2),round(s2,2),round(lv(e2-0.03,e2),1),round(lv(s2,s2+0.03),1)))
print('boundaries adjusted: ends %d starts %d; still loud: %d'%(fix_e,fix_s,len(flags))); print(flags[:20])
# snap + clean
out=[]
for ang,s,e,spk in clips:
    s=round(s*FPS)/FPS; e=round(e*FPS)/FPS
    if out and s<out[-1][2]-1e-6 and abs(out[-1][2]-s)<0.7: s=out[-1][2]  # avoid overlap
    if e-s>=1/FPS: out.append([ang,s,e,spk])
m=[]
for c in out:
    if m and m[-1][0]==c[0] and abs(m[-1][2]-c[1])<1e-6: m[-1][2]=c[2]
    else: m.append(c)
tot=sum(c[2]-c[1] for c in m)
print('clips',len(m),'duration %.1f min'%(tot/60))
json.dump(dict(clips=m),open(D+'/edl_final.json','w'))
