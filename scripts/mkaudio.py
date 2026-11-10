import json, numpy as np, wave
c=json.load(open('edl.json'))['clips']
w=wave.open('A48.wav'); sr=w.getframerate(); a=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).reshape(-1,2).astype(np.float32)
F=int(0.006*sr); ramp=np.linspace(0,1,F)[:,None]
parts=[]; prev_e=None
for ang,s,e,spk in c:
    n=round((e-s)*30); i0=round(s*sr); L=n*sr//30
    x=a[i0:i0+L].copy()
    if prev_e is None or abs(prev_e-s)>1e-6:
        x[:F]*=ramp
        if parts: parts[-1][-F:]*=ramp[::-1]
    parts.append(x); prev_e=s+n/30
y=np.concatenate(parts)
F2=int(0.5*sr); y[:F2]*=np.linspace(0,1,F2)[:,None]; y[-F2:]*=np.linspace(1,0,F2)[:,None]
wo=wave.open('out_audio.wav','wb'); wo.setnchannels(2); wo.setsampwidth(2); wo.setframerate(sr)
wo.writeframes(np.clip(y,-32768,32767).astype(np.int16).tobytes()); wo.close()
print('audio sec',len(y)/sr)
