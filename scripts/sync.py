import numpy as np, wave, sys
def load(p):
    w=wave.open(p); a=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32); return a
a=load('IMG_6498.wav'); b=load('phone_izyan2.wav')
sr=16000
def env(x,hop=160):  # 100 Hz envelope
    n=len(x)//hop; return np.abs(x[:n*hop]).reshape(n,hop).mean(1)
for start in [100,1000,2000,2800]:
    s=start*sr; seg=a[s:s+60*sr]; ref=b[max(0,s-10*sr):s+70*sr]
    # fine xcorr via FFT
    n=len(seg)+len(ref)
    N=1<<int(np.ceil(np.log2(n)))
    c=np.fft.irfft(np.fft.rfft(ref,N)*np.conj(np.fft.rfft(seg,N)),N)
    lag=np.argmax(c[:len(ref)])
    off=(max(0,s-10*sr)+lag-s)/sr
    print(start, 'B_time = A_time + %.4f'%off, c.max()/ (np.linalg.norm(seg)*np.linalg.norm(ref[lag:lag+len(seg)])+1e-9))
