import json, numpy as np, wave, torch
from speechbrain.inference.speaker import EncoderClassifier
from sklearn.cluster import AgglomerativeClustering, KMeans
w=wave.open('IMG_6498.wav'); a=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768; sr=16000
segs=[json.loads(l) for l in open('trans_A.jsonl')]
words=[(s0,e0,t) for s in segs for (s0,e0,t,p) in s['words']]
# windows: 1.5s centered every 0.5s where speech
speech=np.zeros(int(len(a)/sr*10)+10,bool)
for s0,e0,_ in words: speech[int(s0*10):int(e0*10)+1]=True
m=EncoderClassifier.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb",savedir="ecapa")
cent=[t/10 for t in range(0,len(speech),5) if speech[t:t+1].any()]
embs=[];B=64
chunks=[]
for c in cent:
    i=int((c-0.75)*sr); i=max(i,0); x=a[i:i+int(1.5*sr)]
    if len(x)<int(1.5*sr): x=np.pad(x,(0,int(1.5*sr)-len(x)))
    chunks.append(x)
chunks=np.stack(chunks)
with torch.no_grad():
    for k in range(0,len(chunks),B):
        e=m.encode_batch(torch.from_numpy(chunks[k:k+B])).squeeze(1).numpy(); embs.append(e)
E=np.concatenate(embs); E/=np.linalg.norm(E,axis=1,keepdims=True)
np.save('emb.npy',E); np.save('cent.npy',np.array(cent))
lab=AgglomerativeClustering(n_clusters=2,metric='cosine',linkage='average').fit_predict(E)
print('agglo counts',np.bincount(lab))
km=KMeans(2,n_init=10,random_state=0).fit_predict(E); print('km counts',np.bincount(km))
np.save('lab.npy',km)
