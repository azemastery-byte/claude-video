import json, numpy as np, wave
allc=json.load(open('all_clips.json'))
src={0:'/home/user/work2/A48_df.wav',1:'/home/user/work/A48_df.wav'}
A={}
for k,p in src.items():
    w=wave.open(p); A[k]=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32); sr=w.getframerate()
F=int(0.012*sr); up=np.linspace(0,1,F); parts=[]; prev=None; ncut=0
for pi,ang,s,e,spk in allc:
    n=round((e-s)*30); i0=round(s*sr); L=n*sr//30
    x=A[pi][i0:i0+L].copy()
    if len(x)<L: x=np.pad(x,(0,L-len(x)))
    if prev is None or prev!=(pi,round(s,4)):
        x[:F]*=up
        if parts: parts[-1][-F:]*=up[::-1]
        ncut+=1
    parts.append(x); prev=(pi,round(s+n/30,4))
y=np.concatenate(parts)
F2=int(0.6*sr); y[:F2]*=np.linspace(0,1,F2); F3=int(0.8*sr); y[-F3:]*=np.linspace(1,0,F3)
wo=wave.open('audio_edit.wav','wb'); wo.setnchannels(1); wo.setsampwidth(2); wo.setframerate(sr)
wo.writeframes(np.clip(y,-32768,32767).astype(np.int16).tobytes()); wo.close()
print('cuts',ncut,'audio sec %.3f'%(len(y)/sr))
