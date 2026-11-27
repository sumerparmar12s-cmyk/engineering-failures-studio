"""Kokoro TTS for script.md. [PAUSE s cue] -> silence (cue recorded); [RADIO] text -> radio-filtered alarm voice."""
import sys, re, json, numpy as np, soundfile as sf
import subprocess, tempfile, os
from kokoro_onnx import Kokoro
M='/home/user/engineering-failures-studio/.toolchain/kokoro/'
P=sys.argv[1] if len(sys.argv)>1 else '.'; voice='am_michael'; speed=float(os.environ.get('SPEED',1.1))
txt=open(f'{P}/script.md').read().split('## Narration (final)')[1].split('## Claim')[0].strip()
paras=[p.strip() for p in txt.split('\n\n') if p.strip()]
SAY={'wts':'W T S','"k."':'"K."','Nargeolet':'Nar-zho-lay','Dawood':'Da-wood','Suleman':'Soo-lay-mahn','OceanGate':'Ocean Gate','St. John':'Saint John','Hamish':'Hay-mish','Newfoundland':'New-fund-land','psi':'P S I'}
k=Kokoro(M+'kokoro-v1.0.onnx',M+'voices-v1.0.bin'); SR=24000
def sil(s): return np.zeros(int(SR*s),dtype=np.float32)
out=[sil(0.4)]; segs=[]
def t(): return sum(len(x) for x in out)/SR
def times(s):  # 7:37 p.m. -> seven thirty-seven
    ones='zero one two three four five six seven eight nine ten eleven twelve'.split()
    def f(m):
        h=int(m.group(1)); mm=int(m.group(2))
        tens={1:'',2:'twenty',3:'thirty',4:'forty',5:'fifty'}
        if mm<10: mw='oh '+ones[mm]
        elif mm<20: mw=['ten','eleven','twelve','thirteen','fourteen','fifteen','sixteen','seventeen','eighteen','nineteen'][mm-10]
        else: mw=tens[mm//10]+('-'+ones[mm%10] if mm%10 else '')
        return f'{ones[h]} {mw}'
    return re.sub(r'\b(\d{1,2}):(\d\d)\b',f,s)
for p in paras:
    if p.startswith('Lines in ['): continue
    m=re.match(r'\[PAUSE ([\d.]+) ([\w-]+)\]',p)
    if m:
        segs.append(dict(kind='pause',start=t(),dur=float(m.group(1)),cue=m.group(2))); out.append(sil(float(m.group(1)))); continue
    if p.startswith('[RADIO]'):
        s=p[7:].strip()
        a,_=k.create(s,voice='am_adam',speed=1.12,lang='en-us'); a=a.astype(np.float32)
        sf.write('work/_r.wav',a,SR); subprocess.run(['ffmpeg','-y','-loglevel','error','-i','work/_r.wav','-af','highpass=f=380,highpass=f=380,lowpass=f=3000,lowpass=f=3000','work/_r2.wav'],check=True)
        a,_=sf.read('work/_r2.wav',dtype='float32')
        a=np.tanh(a/np.abs(a).max()*2.2)*0.55; a=a+np.random.default_rng(1).normal(0,0.01,len(a)).astype(np.float32)
        segs.append(dict(kind='radio',start=t(),text=s)); out.append(sil(0.15)); out.append(a.astype(np.float32)); continue
    s=times(p)
    for a_,b_ in SAY.items(): s=s.replace(a_,b_)
    a,_=k.create(s,voice=voice,speed=speed,lang='en-us')
    segs.append(dict(kind='vo',start=t(),text=p)); out.append(a.astype(np.float32))
    gap=0.5
    for kk,vv in {'Four days later':0.9,'Thirteen minutes':1.2,'Nobody answers':1.2,'They weren':1.2,'Six days later, he':1.0,'Stockton Rush. Paul':0.4,'So, what':0.8,'The search was over':1.0,'Depth:':0.6,'January 2018':0.6,'July 2022':0.6,'Six days earlier':0.6,'And then, the winter':0.6}.items():
        if p.startswith(kk): gap=vv
    out.append(sil(gap))
a=np.concatenate(out+[sil(float(os.environ.get('TAIL',2.0)))])
sf.write(f'{P}/work/vo_raw.wav',a,SR); json.dump(segs,open(f'{P}/work/segments.json','w'),indent=1)
print('total',round(len(a)/SR,1),'s')
