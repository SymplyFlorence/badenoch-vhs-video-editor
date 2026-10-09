"""Source-master narration assembly for review. Not the final documentary composite."""
import json,subprocess,re
from pathlib import Path
ROOT=Path('/workspace/badenoch-revision-preflight')
SRC=ROOT/'downloads/original_master.mp4'
OUT=ROOT/'work';OUT.mkdir(exist_ok=True)
# Integer source/output frames. No rate change, image holds or invented words.
segments=[
 {'start_frame':9831,'end_frame':9932,'framing':'medium','phrase':'On the same morning ... had published a statement on X.'},
 {'start_frame':11634,'end_frame':11794,'framing':'close','phrase':'She had been presented, she wrote, with clear and irrefutable evidence ...'},
 {'start_frame':11794,'end_frame':12024,'framing':'medium','phrase':'... her shadow justice secretary was plotting ... colleagues.'},
 {'start_frame':12038,'end_frame':12261,'framing':'close','phrase':'Robert Jenrick ... thirteen percentage points ... fourteen months earlier'},
 {'start_frame':12269,'end_frame':12399,'framing':'medium','phrase':'was sacked, stripped of the whip and suspended with immediate effect.'},
 {'start_frame':12436,'end_frame':12492,'framing':'close','phrase':'he was on a stage with Nigel Farage.'},
]
assert sum(s['end_frame']-s['start_frame'] for s in segments)==900
pos=0
for s in segments:
 s['output_start_frame']=pos;pos+=s['end_frame']-s['start_frame'];s['output_end_frame']=pos
 s['source_start']=s['start_frame']/30;s['source_end']=s['end_frame']/30
(OUT/'narration_edl.json').write_text(json.dumps({'status':'REVIEW ONLY; source words/cuts need listening verification; evidence composite pending','source':str(SRC),'fps':30,'segments':segments},indent=2))
# Assemble audio at sample precision from frame-based cuts and smooth exposed boundaries.
args=['ffmpeg','-hide_banner','-nostdin','-y']
fg=[]
for i,s in enumerate(segments):
 dur=(s['end_frame']-s['start_frame'])/30
 args+=['-ss',str(s['source_start']),'-t',str(dur),'-i',str(SRC)]
 fg.append(f'[{i}:a]atrim=duration={dur},asetpts=PTS-STARTPTS,aresample=48000,afade=t=in:d=0.005,afade=t=out:st={dur-0.005}:d=0.005[a{i}]')
fg.append(''.join(f'[a{i}]' for i in range(len(segments)))+f'concat=n={len(segments)}:v=0:a=1,highpass=f=70,afftdn=nr=6:nf=-45,atrim=duration=30[a]')
subprocess.run(args+['-filter_complex_threads','1','-filter_complex',';'.join(fg),'-map','[a]','-c:a','pcm_s24le',str(OUT/'assembled_audio.wav')],check=True,stdout=subprocess.DEVNULL,stderr=(OUT/'audio_assembly.log').open('w'))
measure=subprocess.run(['ffmpeg','-hide_banner','-nostdin','-i',str(OUT/'assembled_audio.wav'),'-af','loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json','-f','null','-'],check=True,capture_output=True,text=True)
(OUT/'loudness_first_pass.log').write_text(measure.stderr)
m=json.loads(re.findall(r'\{\s*"input_i".*?\}',measure.stderr,re.S)[-1])
norm=f'loudnorm=I=-16:TP=-1.5:LRA=9:measured_I={m["input_i"]}:measured_TP={m["input_tp"]}:measured_LRA={m["input_lra"]}:measured_thresh={m["input_thresh"]}:offset={m["target_offset"]}:linear=true,aresample=48000'
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-nostdin','-y','-i',str(OUT/'assembled_audio.wav'),'-af',norm,'-c:a','pcm_s24le',str(OUT/'normalized_audio.wav')],check=True)
for i,s in enumerate(segments):
 dur=(s['end_frame']-s['start_frame'])/30
 vf='setpts=PTS-STARTPTS,setsar=1'
 if s['framing']=='close':vf+=',crop=3264:1836:220:100,scale=3840:2160:flags=lanczos'
 vf+=',format=yuv420p'
 cmd=['ffmpeg','-hide_banner','-loglevel','error','-nostdin','-y','-threads','2','-ss',str(s['source_start']),'-i',str(SRC),'-an','-vf',vf,'-frames:v',str(s['end_frame']-s['start_frame']),'-r','30','-c:v','libx264','-preset','fast','-crf','18','-threads','4','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-movflags','+faststart',str(OUT/f'part_{i}.mp4')]
 print('Rendering original-master segment',i+1,'of',len(segments),flush=True)
 subprocess.run(cmd,check=True)
(OUT/'concat.txt').write_text(''.join(f"file 'part_{i}.mp4'\n" for i in range(len(segments))))
final=ROOT/'Badenoch_narration_REVIEW_30s_4K.mp4'
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-nostdin','-y','-f','concat','-safe','0','-i',str(OUT/'concat.txt'),'-i',str(OUT/'normalized_audio.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','256k','-ar','48000','-t','30','-movflags','+faststart',str(final)],check=True)
print('REVIEW assembly rendered:',final,flush=True)
