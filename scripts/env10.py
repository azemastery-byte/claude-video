import numpy as np, wave, sys
w=wave.open(sys.argv[1]); sr=w.getframerate()
a=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768
h=sr//100; n=len(a)//h
r=np.sqrt((a[:n*h].reshape(n,h)**2).mean(1)+1e-10); d=20*np.log10(r)
np.save(sys.argv[2],d.astype(np.float32))
print(np.percentile(d,[5,10,20,30,40,50,60,80,95]).round(1))
