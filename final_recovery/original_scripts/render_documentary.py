"""Documentary refinement from original master and verified source captures.
Existing repository and downloaded production code are preserved.
"""
import json,math,subprocess,csv
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageChops,ImageOps
ROOT=Path('/workspace/badenoch-revision-preflight');E=ROOT/'evidence';W=ROOT/'composite_work';W.mkdir(exist_ok=True)
FINAL=ROOT/'Final';FINAL.mkdir(exist_ok=True)
SRC=ROOT/'downloads/original_master.mp4';FPS=30;SIZE=(3840,2160)
BG='#0a1421';WHITE='#f7f9fc';MUTED='#a7b4c3';BLUE='#49c2ff';GOLD='#f1cc67'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def ft(size,bold=False):return ImageFont.truetype(BOLD if bold else FONT,size)
F={s:ft(s) for s in [34,38,42,44,50,56,64,72,84,96,110,128]};FB={s:ft(s,True) for s in [48,64,72,84,96,112,144,230,300]}
def ease(p):p=max(0,min(1,p));return p*p*(3-2*p)
def text(im,xy,s,font,fill=WHITE):ImageDraw.Draw(im).text(xy,s,font=font,fill=fill,stroke_width=0)
def bg():return Image.new('RGB',SIZE,BG)
logo=Image.open(E/'sky-logo.png').convert('RGB')
# Pixel crop from the original browser screenshot. Article wording/layout is unaltered.
header=Image.open(E/'sky-article-header.png').convert('RGB').crop((1800,140,5670,640))
paras={k:Image.open(E/f'sky-{k}-paragraph.png').convert('RGB') for k in ['statement','dismissal']}
geo=json.loads((E/'article_geometry.json').read_text())
portraits={k:Image.open(E/f'{k}_portrait.jpg').convert('RGB') for k in ['jenrick','farage']}
# Factual text stays attributed; highlights multiply the genuine captured pixels.
highlight_times={'statement':{'clear, irrefutable evidence':5.44,'plotting in secret to defect':9.36},'dismissal':{'sacked Robert Jenrick from the shadow cabinet':24.04,'removed the whip':24.66,'suspended his party membership with immediate effect':26.16}}
def document(kind,t,start,end):
 im=bg();d=ImageDraw.Draw(im)
 d.rectangle((180,180,3660,190),fill=BLUE)
 im.paste(logo.resize((502,122),Image.Resampling.LANCZOS),(240,260))
 text(im,(2310,285),'15 JANUARY 2026',FB[48])
 if kind=='headline':
  doc=header.copy();label='THE PUBLISHED REPORT'
 else:
  doc=paras[kind].copy();label='BADENOCH’S STATEMENT' if kind=='statement' else 'THE DISMISSAL'
  mask=Image.new('RGB',doc.size,'white');md=ImageDraw.Draw(mask)
  for phrase,spans in geo[kind]['spans'].items():
   progress=ease((t-highlight_times[kind][phrase])/0.45)
   remaining=sum(x['width'] for x in spans)*progress
   for r in spans:
    width=min(remaining,r['width']);remaining-=width
    if width>0:md.rectangle((r['x'],r['y']-2,r['x']+width,r['y']+r['height']+5),fill='#ffe891')
  doc=ImageChops.multiply(doc,mask)
 text(im,(240,460),label,FB[64],MUTED)
 z=1+0.035*ease((t-start)/(end-start))
 width=int(3340*z);height=round(doc.height*width/doc.width)
 doc=doc.resize((width,height),Image.Resampling.LANCZOS)
 x=(SIZE[0]-width)//2;y=920-height//2
 d.rectangle((x-70,y-100,x+width+70,y+height+100),fill='white')
 im.paste(doc,(x,y))
 text(im,(240,1600),'SOURCE EXCERPT',FB[48],BLUE)
 text(im,(240,1690),'Sky News · Faye Brown · 15 January 2026',F[50])
 text(im,(240,1780),'news.sky.com / story 13494578',F[42],MUTED)
 if kind!='headline':text(im,(240,1900),'Allegation attributed to Kemi Badenoch.',F[42],MUTED)
 return im

def chart(t,start,end):
 im=bg();d=ImageDraw.Draw(im);local=t-start
 d.rectangle((240,185,500,197),fill=BLUE)
 text(im,(240,260),'CONSERVATIVE LEADERSHIP',FB[64],MUTED)
 text(im,(240,355),'THE MEMBERS’ VOTE',FB[112])
 text(im,(240,540),'2 NOVEMBER 2024',F[50],MUTED)
 maxw=2500;bx=240
 for name,value,yy,col,delay in [('Kemi Badenoch',56.5,750,BLUE,0),('Robert Jenrick',43.5,1180,'#7487a0',0.14)]:
  p=ease((local-delay)/0.85)
  text(im,(bx,yy),name,FB[72]);text(im,(2880,yy-20),f'{value*p:.1f}%',FB[112],col)
  d.rectangle((bx,yy+135,bx+maxw,yy+225),fill='#1e3046')
  d.rectangle((bx,yy+135,bx+maxw*(value/60)*p,yy+225),fill=col)
  for val in [0,20,40,60]:
   xx=bx+maxw*val/60;d.line((xx,yy+234,xx,yy+247),fill='#536477',width=3)
   text(im,(int(xx)-20,yy+256),f'{val}%',F[34],MUTED)
 p=ease((local-0.95)/0.35)
 if p>0:
  layer=Image.new('RGB',SIZE,BG)
  text(layer,(240,1680),'13',FB[230],BLUE)
  text(layer,(650,1710),'PERCENTAGE',FB[72]);text(layer,(650,1800),'POINTS APART',FB[72])
  crop=layer.crop((200,1630,2300,1920));under=im.crop((200,1630,2300,1920));im.paste(Image.blend(under,crop,p),(200,1630))
 text(im,(240,2040),'House of Commons Library · Briefing 01366, p.12 · 4 November 2024',F[38],MUTED)
 return im

def portrait_scene(t,start,end):
 im=bg();text(im,(240,90),'JENRICK & FARAGE',FB[72])
 text(im,(2660,115),'ILLUSTRATIVE PORTRAITS',F[42],MUTED)
 for person,x,name in [('jenrick',180,'ROBERT JENRICK'),('farage',1940,'NIGEL FARAGE')]:
  # Use the original 4482x6720 portrait. An upper-body crop, not a fabricated event image.
  src=portraits[person];p=ease((t-start)/(end-start));z=1+0.035*p
  box=(0,250,4482,4850)
  crop=src.crop(box);out=ImageOps.fit(crop,(1720,1640),method=Image.Resampling.LANCZOS,centering=(0.5,0.32))
  if z>1:
   out=out.resize((round(1720*z),round(1640*z)),Image.Resampling.LANCZOS)
   dx=(out.width-1720)//2;dy=(out.height-1640)//2;out=out.crop((dx,dy,dx+1720,dy+1640))
  im.paste(out,(x,230));text(im,(x+65,1745),name,FB[72])
 text(im,(180,1950),'© House of Commons · Roger Harris / Laurie Noble · CC BY 3.0',F[38],MUTED)
 text(im,(180,2010),'Official portraits · cropped and animated · source links in evidence manifest',F[38],MUTED)
 return im

shots=[
 {'start':0,'end':60,'kind':'presenter','frame':'medium','note':'Clean original presenter; recorded lead-in restores context.'},
 {'start':60,'end':142,'kind':'headline','note':'Genuine Sky News headline crop; controlled push-in.'},
 {'start':142,'end':340,'kind':'statement','note':'Genuine quoted statement; speech-timed highlight and restrained push-in.'},
 {'start':340,'end':412,'kind':'presenter','frame':'close','note':'Punch-in on damaging-as-possible statement.'},
 {'start':412,'end':491,'kind':'presenter','frame':'medium','note':'Return to medium as sentence completes.'},
 {'start':491,'end':522,'kind':'presenter','frame':'close','note':'Robert Jenrick introduction before result graphic.'},
 {'start':522,'end':642,'kind':'chart','note':'Verified 56.5% versus 43.5%; animated bars and 13-point reveal.'},
 {'start':642,'end':714,'kind':'presenter','frame':'medium','note':'Presenter returns for fourteen months earlier.'},
 {'start':714,'end':844,'kind':'dismissal','note':'Genuine Sky statement excerpt; successive highlights match dismissal/whip/suspension.'},
 {'start':844,'end':900,'kind':'portraits','note':'Licensed official portraits; split-screen and subtle push; complete Farage sentence and short decay.'}
]
(W/'shots.json').write_text(json.dumps(shots,indent=2))
edl=json.loads((ROOT/'work/narration_edl.json').read_text())['segments']

def render_graphic(index,shot):
 out=W/f'shot_{index:02}.mp4'
 if out.exists():
  try:
   d=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=nb_frames','-of','json',str(out)]))
   if int(d['streams'][0]['nb_frames'])==shot['end']-shot['start']:return out
  except Exception:pass
 cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','3840x2160','-r','30','-i','pipe:0','-an','-vf','format=yuv420p','-c:v','libx264','-crf','18','-preset','fast','-threads','4','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-movflags','+faststart',str(out)]
 with (W/f'shot_{index:02}.log').open('w') as log:
  proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
  for frame in range(shot['start'],shot['end']):
   t=frame/FPS;start=shot['start']/FPS;end=shot['end']/FPS
   if shot['kind'] in ['headline','statement','dismissal']:im=document(shot['kind'],t,start,end)
   elif shot['kind']=='chart':im=chart(t,start,end)
   else:im=portrait_scene(t,start,end)
   if frame in [shot['start'],(shot['start']+shot['end'])//2,shot['end']-1]:im.resize((1920,1080),Image.Resampling.LANCZOS).save(W/f'shot_{index:02}_{frame:03}.jpg',quality=95)
   proc.stdin.write(im.tobytes())
  proc.stdin.close()
  if proc.wait()!=0:raise RuntimeError(f'Graphic encode failed {index}')
 return out

def render_presenter(index,shot):
 s=next(x for x in edl if x['output_start_frame']<=shot['start'] and x['output_end_frame']>=shot['end'])
 sourceframe=s['start_frame']+shot['start']-s['output_start_frame'];out=W/f'shot_{index:02}.mp4'
 vf='setpts=PTS-STARTPTS,setsar=1'
 if shot['frame']=='close':vf+=',crop=3264:1836:220:100,scale=3840:2160:flags=lanczos'
 vf+=',format=yuv420p'
 cmd=['ffmpeg','-hide_banner','-loglevel','error','-nostdin','-y','-threads','2','-ss',str(sourceframe/FPS),'-i',str(SRC),'-an','-vf',vf,'-frames:v',str(shot['end']-shot['start']),'-r','30','-c:v','libx264','-crf','18','-preset','fast','-threads','4','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-movflags','+faststart',str(out)]
 subprocess.run(cmd,check=True);return out

def main():
 files=[]
 for i,shot in enumerate(shots):
  print('Rendering',i+1,'/',len(shots),shot['kind'],f'{shot["start"]/30:.2f}-{shot["end"]/30:.2f}',flush=True)
  files.append(render_presenter(i,shot) if shot['kind']=='presenter' else render_graphic(i,shot))
 (W/'concat.txt').write_text(''.join(f"file '{p.name}'\n" for p in files))
 out=FINAL/'Badenoch_documentary_FINAL_4K.mp4'
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-nostdin','-y','-f','concat','-safe','0','-i',str(W/'concat.txt'),'-i',str(ROOT/'work/normalized_audio.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','256k','-ar','48000','-t','30','-movflags','+faststart',str(out)],check=True)
 print('LOCAL MASTER RENDERED; Drive upload and QC still required:',out,flush=True)
if __name__=='__main__':main()
