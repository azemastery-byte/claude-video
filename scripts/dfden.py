import sys, time, wave, numpy as np, torch
from df.enhance import init_df, enhance
inp,out=sys.argv[1],sys.argv[2]; lim=float(sys.argv[3]) if len(sys.argv)>3 else 15
m,st,_=init_df()
w=wave.open(inp); sr=w.getframerate(); ch=w.getnchannels()
a=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).reshape(-1,ch).astype(np.float32)/32768
mono=a.mean(1)
assert sr==st.sr()
CH=sr*60; ov=sr; outp=np.zeros_like(mono); t=time.time()
for s in range(0,len(mono),CH):
    a0=max(0,s-ov); b0=min(len(mono),s+CH+ov)
    e=enhance(m,st,torch.from_numpy(mono[a0:b0][None]),atten_lim_db=lim).numpy()[0]
    outp[s:min(s+CH,len(mono))]=e[s-a0:s-a0+min(CH,len(mono)-s)]
    print('%d/%d %.0fs'%(s//sr,len(mono)//sr,time.time()-t),flush=True)
y=np.clip(outp*32767,-32768,32767).astype(np.int16)
wo=wave.open(out,'wb'); wo.setnchannels(1); wo.setsampwidth(2); wo.setframerate(sr); wo.writeframes(y.tobytes()); wo.close()
