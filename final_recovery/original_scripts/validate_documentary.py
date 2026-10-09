import json,subprocess,hashlib,struct,csv,re
from pathlib import Path
R=Path('/workspace/badenoch-revision-preflight');F=R/'Final';p=F/'Badenoch_documentary_FINAL_4K.mp4'
d=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]));(F/'ffprobe_measured.json').write_text(json.dumps(d,indent=2))
v=next(x for x in d['streams'] if x['codec_type']=='video');a=next(x for x in d['streams'] if x['codec_type']=='audio')
assert (v['width'],v['height'])==(3840,2160)
assert v['codec_name']=='h264' and v['pix_fmt']=='yuv420p'
assert v['avg_frame_rate']=='30/1' and int(v['nb_frames'])==900
assert float(d['format']['duration'])==30.0 and float(v['duration'])==30.0
assert a['codec_name']=='aac' and a['sample_rate']=='48000' and float(a['duration'])==30.0
atoms=[]
with p.open('rb') as f:
 while h:=f.read(8):
  if len(h)!=8:break
  n,t=struct.unpack('>I4s',h);offset=f.tell()-8
  if n==1:n=struct.unpack('>Q',f.read(8))[0]
  if not n:break
  atoms.append((t.decode('ascii','replace'),offset,n));f.seek(offset+n)
assert next(x[1] for x in atoms if x[0]=='moov')<next(x[1] for x in atoms if x[0]=='mdat')
print('PASS: format, frame count, duration, audio and fast-start metadata',flush=True)
# Full decoding and black/freeze signal checks. A chart can intentionally pause for reading.
cmd=['ffmpeg','-hide_banner','-nostdin','-threads','3','-i',str(p),'-vf','blackdetect=d=0.1:pix_th=0.05:pic_th=0.98,freezedetect=n=-55dB:d=0.5','-af','silencedetect=noise=-40dB:d=0.2,loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json','-f','null','-']
r=subprocess.run(cmd,capture_output=True,text=True,check=True);(F/'full_decode_qc.log').write_text(r.stderr)
print('PASS: complete audio/video decode',flush=True)
print('\n'.join(x for x in r.stderr.splitlines() if any(w in x for w in ['black_start','freeze_start','freeze_end','freeze_duration','silence_start','silence_end','input_i','input_tp','input_lra'])),flush=True)
frames=[0,59,60,141,142,339,340,411,412,490,491,521,522,641,642,713,714,843,844,899]
expr='+'.join('eq(n\\,'+str(n)+')' for n in frames)
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-nostdin','-y','-threads','3','-i',str(p),'-vf',f"select='{expr}',scale=640:360,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:text='%{{pts\\:hms}}':x=8:y=8:fontsize=22:fontcolor=white:box=1:boxcolor=black@0.8,tile=4x5",'-frames:v','1',str(F/'shot_boundary_contact_sheet.jpg')],check=True)
print('Saved frames before/after every cut',flush=True)
summary={'sha256':hashlib.file_digest(p.open('rb'),'sha256').hexdigest(),'size_bytes':p.stat().st_size,'mp4_atoms':atoms,'width':v['width'],'height':v['height'],'fps':v['avg_frame_rate'],'frames':v['nb_frames'],'video_codec':v['codec_name'],'pixel_format':v['pix_fmt'],'audio_codec':a['codec_name'],'sample_rate':a['sample_rate'],'channels':a['channels'],'duration':d['format']['duration'],'full_decode':'passed','drive_upload':'NOT PERFORMED; no authenticated upload tool exposed'}
(F/'qc_summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary),flush=True)
