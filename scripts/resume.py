import json,subprocess,os
allc=json.load(open('all_clips.json')); jobs=open('jobs.sh').read().strip().split('\n'); todo=[]
for i,(pi,ang,s,e,spk) in enumerate(allc):
    f='clips/c%04d.mp4'%i; n=round((e-s)*30); ok=False
    if os.path.exists(f):
        r=subprocess.run(['ffprobe','-v','error','-count_packets','-select_streams','v','-show_entries','stream=nb_read_packets','-of','csv=p=0',f],capture_output=True,text=True).stdout.strip()
        ok = r.isdigit() and int(r)==n
    if not ok: todo.append(jobs[i])
open('jobs_todo.sh','w').write('\n'.join(todo)+'\n'); print('todo',len(todo))
