"""Re-time caption words inside [a,b] by character length (for spans Whisper mangled). usage: fix_span.py a b 'exact script text'"""
import json,sys,re
a,b,txt=float(sys.argv[1]),float(sys.argv[2]),sys.argv[3]
W=[x for x in json.load(open('vo/vo.mp3.words.json')) if not (a-0.01<=x['s']<b)]
ws=txt.split(); L=[len(w)+(6 if re.search(r'[.,?!]$',w) else 1) for w in ws]; T=sum(L); t=a; new=[]
for w,l in zip(ws,L):
    d=(b-a)*l/T; new.append(dict(w=w,s=round(t,2),e=round(t+d*0.9,2))); t+=d
W=sorted(W+new,key=lambda x:x['s']); json.dump(W,open('vo/vo.mp3.words.json','w'))
lines,line,st=[],[],None
for x in W:
    st=x['s'] if st is None else st; line.append(x['w'])
    if re.search(r'[.?!]"?$',x['w']) and x['w'] not in ('p.m.',): lines.append(f"{st:7.2f} {' '.join(line)}"); line,st=[],None
if line: lines.append(f"{st:7.2f} {' '.join(line)}")
open('vo/sentences.txt','w').write('\n'.join(lines)+'\n'); print('ok',len(new))
