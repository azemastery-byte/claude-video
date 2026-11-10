# Podcast multicam edit – Zafesha Simply (Host Najwa × KS)

Source (Google Drive): `IMG_6498.mp4` (Cam A – wide 2-shot) and `phone izyan 2.mp4` (Cam B – close-up KS), ~50:25 each.

## Output
`final_full.mp4` – 1920x1080 30fps, ~47:01 (from 50:25).

## What the edit does
1. **Audio/video sync** – Cam B is aligned to Cam A by audio cross-correlation
   (`B = A + 0.798s + 1.29e-5·A`, i.e. small clock drift corrected). Audio track = Cam A (cleaned: highpass, light denoise, loudnorm −16 LUFS).
2. **Pauses removed** – every silence ≥0.7s is tightened to ~0.4s (77+ gaps).
3. **Off-topic / bloopers removed** (Cam A time):
   - 36:41–37:19 – asking off-script who "Puan Ashiman" is (doctor/homeopathy check)
   - 38:13–38:33 – fumbling "Ini apa? … ini apa pesanan dia eh?" before the retake
   - 43:22–44:51 – discussing the question sheet ("kita pergi ke arah bisnes pula…", "second last", "cuba tengok soalan asal") before the retaken question
4. **Camera switching by speaker** – speaker diarization (ECAPA voice embeddings, 2 clusters):
   - KS speaking → Cam B close-up
   - Host speaking → punch-in on host from Cam A (crop 1280x720 → 1080p)
   - Wide 2-shot used as opener and for variety/hiding jump cuts in long answers
   - Short host back-channels ("betul", "okay") stay on KS.

## Pipeline (`scripts/`)
`sync.py` → `transcribe.py` (faster-whisper large-v3-turbo, ms) → `diarize.py` / `vad_spk.py` → `mkact.py` → `edl.py` (EDL in `edit/edl.json`) → `mkjobs.py` (per-clip ffmpeg render) → `mkaudio.py` → concat + mux.
