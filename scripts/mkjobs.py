import json
c=json.load(open('edl.json'))['clips']
A='/home/user/media/IMG_6498.mp4'; B='/home/user/media/phone_izyan2.mp4'
off=lambda t:0.798+1.29e-5*t
L=[]; lst=open('clips/list.txt','w')
for i,(ang,s,e,spk) in enumerate(c):
    n=round((e-s)*30)
    if ang=='B': src,ss,vf=B,s+off(s),'fps=30'
    elif ang=='W': src,ss,vf=A,s,'fps=30'
    else: src,ss,vf=A,s,'crop=1280:720:640:170,scale=1920:1080:flags=lanczos,fps=30'
    out='clips/c%04d.mp4'%i
    L.append(f'ffmpeg -nostdin -v error -y -ss {ss:.4f} -i {src} -an -vf "{vf},format=yuv420p" -frames:v {n} -c:v libx264 -preset veryfast -crf 19 -g 60 -video_track_timescale 15360 -threads 2 {out}')
    lst.write(f"file 'c{i:04d}.mp4'\n")
open('jobs.sh','w').write('\n'.join(L)+'\n')
print(len(L))
