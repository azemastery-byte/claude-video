import json,numpy as np,wave,sys
d,Aw,Bw,o0,o1=sys.argv[1],sys.argv[2],sys.argv[3],float(sys.argv[4]),float(sys.argv[5])
def load(p):
    w=wave.open(p); return np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)
a=load(Aw); b=load(Bw); sr=16000
c=json.load(open(d+'/edl_final.json'))['clips']
res=[]
for ang,s,e,spk in c:
    if ang!='B' or e-s<3: continue
    off=o0+o1*s; L=int((e-s)*sr); i=int(s*sr); j=int((s+off)*sr); M=int(0.1*sr)
    x=a[i:i+L]; y=b[j-M:j+L+M]
    if len(y)<L+2*M: continue
    N=1<<int(np.ceil(np.log2(len(y)+L)))
    cc=np.fft.irfft(np.fft.rfft(y,N)*np.conj(np.fft.rfft(x,N)),N)[:2*M+1]
    lag=(np.argmax(cc)-M)/sr*1000
    res.append((s,lag,e-s))
r=np.array([x[1] for x in res])
print('B clips checked',len(r),'median lag %.1f ms, |lag|>20ms: %d, >40ms: %d'%(np.median(r),(abs(r)>20).sum(),(abs(r)>40).sum()))
print('worst',sorted(res,key=lambda x:-abs(x[1]))[:8])
