import json
parts=[dict(d='/home/user/work2',A='/home/user/media2/IMG_6497.mp4',B='/home/user/media2/phone_izyan1.mp4',o0=0.5557,o1=1.557e-5),
       dict(d='/home/user/work', A='/home/user/media/IMG_6498.mp4', B='/home/user/media/phone_izyan2.mp4', o0=0.798, o1=1.29e-5)]
allc=[]
for pi,p in enumerate(parts):
    for c in json.load(open(p['d']+'/edl_final.json'))['clips']: allc.append((pi,)+tuple(c))
json.dump(allc,open('all_clips.json','w'))
G='eq=contrast=1.04:saturation=1.06'
L=[]; lst=open('clips/list.txt','w'); N=len(allc)
for i,(pi,ang,s,e,spk) in enumerate(allc):
    p=parts[pi]; n=round((e-s)*30)
    if ang=='B': src,ss,vf=p['B'],s+p['o0']+p['o1']*s,f'fps=30,{G},unsharp=5:5:0.35'
    elif ang=='W': src,ss,vf=p['A'],s,f'fps=30,{G},unsharp=5:5:0.35'
    else: src,ss,vf=p['A'],s,f'crop=1280:720:640:170,scale=1920:1080:flags=lanczos,fps=30,{G},unsharp=5:5:0.7'
    if i==0: vf+=',fade=t=in:st=0:d=0.6'
    if i==N-1: vf+=f',fade=t=out:st={max(0,n/30-0.8):.3f}:d=0.8'
    L.append(f'ffmpeg -nostdin -v error -y -ss {ss:.4f} -i {src} -an -vf "{vf},format=yuv420p" -frames:v {n} -c:v libx264 -preset medium -crf 18 -profile:v high -g 60 -bf 2 -color_primaries bt709 -color_trc bt709 -colorspace bt709 -video_track_timescale 15360 -threads 2 clips/c{i:04d}.mp4')
    lst.write(f"file 'c{i:04d}.mp4'\n")
open('jobs.sh','w').write('\n'.join(L)+'\n'); print(N,'clips', sum(round((c[3]-c[2])*30) for c in allc)/30/60,'min')
