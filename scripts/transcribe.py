import json, sys, time
from faster_whisper import WhisperModel
m=WhisperModel(sys.argv[2], device='cpu', compute_type='int8', cpu_threads=4)
import numpy as np, wave
w=wave.open(sys.argv[1]); aud=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768
t=time.time()
segs,info=m.transcribe(aud, language='ms', word_timestamps=True, vad_filter=True, beam_size=1,
    vad_parameters=dict(min_silence_duration_ms=400))
out=[]
with open(sys.argv[3],'w') as f:
    for s in segs:
        d=dict(start=s.start,end=s.end,text=s.text,words=[(w.start,w.end,w.word,w.probability) for w in s.words])
        f.write(json.dumps(d,ensure_ascii=False)+'\n'); f.flush()
print('done',time.time()-t)
