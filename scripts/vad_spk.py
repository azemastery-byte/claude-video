import numpy as np, wave, torch
from scipy.ndimage import uniform_filter1d, percentile_filter
from speechbrain.inference.speaker import EncoderClassifier
e=np.load('env.npy')[0]; d=20*np.log10(e)   # 10 Hz
ds=uniform_filter1d(d,3)
floor=percentile_filter(ds,10,size=600)
act=ds>floor+7
np.save('act.npy',act)
print('active frac',act.mean())
E=np.load('emb.npy'); cent=np.load('cent.npy'); lab=np.load('lab.npy')
C=np.stack([E[lab==k].mean(0) for k in (0,1)]); C/=np.linalg.norm(C,axis=1,keepdims=True)
have=set(np.round(cent*10).astype(int))
need=[t for t in range(0,len(act),5) if act[t] and t not in have]
print('need',len(need))
w=wave.open('IMG_6498.wav'); a=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768; sr=16000
m=EncoderClassifier.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb",savedir="ecapa")
L=int(1.5*sr); ch=[]
for t in need:
    i=max(0,int((t/10-0.75)*sr)); x=a[i:i+L]; ch.append(np.pad(x,(0,L-len(x))))
E2=[]
with torch.no_grad():
    for k in range(0,len(ch),64):
        E2.append(m.encode_batch(torch.from_numpy(np.stack(ch[k:k+64]))).squeeze(1).numpy())
E2=np.concatenate(E2); E2/=np.linalg.norm(E2,axis=1,keepdims=True)
allt=np.concatenate([np.round(cent*10).astype(int),np.array(need)])
allE=np.concatenate([E,E2])
score=allE@C[1]-allE@C[0]   # >0 => KS
o=np.argsort(allt)
np.save('spk_t.npy',allt[o]); np.save('spk_s.npy',score[o])
print('KS frac',(score>0).mean())
