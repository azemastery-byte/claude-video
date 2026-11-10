import numpy as np, json
FPS=30
act=np.load('act.npy')            # 10Hz
st=np.load('spk_t.npy'); ss=np.load('spk_s.npy')
from scipy.ndimage import median_filter
REGION=(1.0,3018.3)
CUTS=[(2201.7,2239.2),(2293.4,2312.8),(2602.2,2691.0)]
def allowed(t):
    return REGION[0]<=t<=REGION[1] and not any(a<=t<b for a,b in CUTS)
# speech islands
isl=[];i=0;n=len(act)
while i<n:
    if act[i]:
        j=i
        while j<n and act[j]: j+=1
        isl.append([i/10,j/10]); i=j
    else: i+=1
# merge small gaps
m=[]
for s,e in isl:
    if m and s-m[-1][1]<0.7: m[-1][1]=e
    else: m.append([s,e])
PRE,POST=0.15,0.25
keep=[]
for s,e in m:
    s-=PRE;e+=POST
    if e-s<0.45: continue      # drop isolated tiny blips
    if keep and s<=keep[-1][1]+0.05: keep[-1][1]=max(keep[-1][1],e)
    else: keep.append([s,e])
# apply region/cuts
out=[]
for s,e in keep:
    s=max(s,REGION[0]); e=min(e,REGION[1])
    if e<=s: continue
    pieces=[[s,e]]
    for a,b in CUTS:
        np_=[]
        for x,y in pieces:
            if y<=a or x>=b: np_.append([x,y])
            else:
                if x<a: np_.append([x,a])
                if y>b: np_.append([b,y])
        pieces=np_
    out+= [p for p in pieces if p[1]-p[0]>=0.3]
# snap to frames
out=[[round(s*FPS)/FPS, round(e*FPS)/FPS] for s,e in out]
# speaker per 0.1s
grid=np.arange(0,n)/10
sc=np.interp(grid,st/10,median_filter(ss,5))
ks=sc>0
# build atoms: (src_s, src_e, spk) splitting intervals at speaker changes (>=0.1s resolution)
atoms=[]
for s,e in out:
    t=s; cur=None; a0=s
    for k in range(int(round(s*10)),int(round(e*10))):
        lab='KS' if ks[min(k,n-1)] else 'H'
        if cur is None: cur=lab
        if lab!=cur:
            tt=round(k/10*FPS)/FPS
            if tt>a0: atoms.append([a0,tt,cur])
            a0=tt; cur=lab
    if e>a0: atoms.append([a0,e,cur or 'KS'])
# relabel short host runs (<1.4s in output time) as previous speaker; short KS runs (<0.8) too
def runs(at):
    r=[];
    for i,a in enumerate(at):
        if r and r[-1][0]==a[2]: r[-1][2].append(i)
        else: r.append([a[2],0,[i]])
    for x in r: x[1]=sum(at[i][1]-at[i][0] for i in x[2])
    return r
for it in range(3):
    r=runs(atoms)
    for ri,(lab,dur,idx) in enumerate(r):
        thr=1.4 if lab=='H' else 0.8
        if dur<thr:
            new = r[ri-1][0] if ri>0 else (r[ri+1][0] if ri+1<len(r) else lab)
            for i in idx: atoms[i][2]=new
# merge adjacent atoms with same label and contiguous source
m2=[]
for a in atoms:
    if m2 and m2[-1][2]==a[2] and abs(m2[-1][1]-a[0])<1e-6: m2[-1][1]=a[1]
    else: m2.append(list(a))
atoms=m2
# angle assignment
clips=[]; prev_spk=None; angle=None; on=0.0; outt=0.0
PRIM={'KS':'B','H':'H'}
for idx,(s,e,spk) in enumerate(atoms):
    boundary = idx==0 or abs(atoms[idx-1][1]-s)>1e-6   # a pause/content cut precedes
    if spk!=prev_spk:
        angle=PRIM[spk]; on=0.0
        if idx==0: angle='W'
    elif boundary:
        if angle=='W' and on>=3.5: angle=PRIM[spk]; on=0
        elif angle!='W' and on>=7.0: angle='W'; on=0
    # within long atom, allow mid-atom switches every so often
    t=s
    while True:
        lim = (6.0 if angle=='W' else 16.0) - on
        if e-t>lim+2.0:
            tt=round((t+lim)*FPS)/FPS
            clips.append([angle,t,tt,spk]); t=tt; on=0
            angle = PRIM[spk] if angle=='W' else 'W'
        else:
            clips.append([angle,t,e,spk]); on+=e-t; break
    prev_spk=spk
# merge same-angle contiguous
m3=[]
for c in clips:
    if m3 and m3[-1][0]==c[0] and abs(m3[-1][2]-c[1])<1e-6: m3[-1][2]=c[2]
    else: m3.append(list(c))
clips=m3
tot=sum(c[2]-c[1] for c in clips)
print('intervals',len(out),'clips',len(clips),'output %.1f min'%(tot/60))
from collections import Counter
cnt=Counter(); 
for c in clips: cnt[c[0]]+=c[2]-c[1]
print({k:round(v/60,1) for k,v in cnt.items()})
json.dump(dict(intervals=out,clips=clips),open('edl.json','w'))
# ---- enforce min clip length
for it in range(3):
    for i in range(len(clips)):
        if clips[i][2]-clips[i][1] < 1.0:
            if i>0: clips[i][0]=clips[i-1][0]
            elif i+1<len(clips): clips[i][0]=clips[i+1][0]
    m3=[]
    for c in clips:
        if m3 and m3[-1][0]==c[0] and abs(m3[-1][2]-c[1])<1e-6: m3[-1][2]=c[2]
        else: m3.append(list(c))
    clips=m3
print('after minlen clips',len(clips), 'min dur %.2f'%min(c[2]-c[1] for c in clips))
json.dump(dict(intervals=out,clips=clips),open('edl.json','w'))
