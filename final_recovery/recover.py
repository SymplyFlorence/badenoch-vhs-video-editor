"""Recover the existing master or run its preserved pipeline. No placeholders."""
import argparse, hashlib, json, shutil, subprocess, tempfile
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent

def digest(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def verify_package():
    manifest = json.loads((PACKAGE/'preserved_assets.json').read_text())
    for name, expected in manifest.items():
        path = PACKAGE/name
        if not path.is_file():
            raise FileNotFoundError(f'Required preserved asset missing: {path}. Re-clone the recovery repository; no substitute is permitted.')
        if path.stat().st_size != expected['bytes'] or digest(path) != expected['sha256']:
            raise RuntimeError(f'Preserved asset checksum mismatch: {path}')
    return json.loads((PACKAGE/'config.json').read_text())

def locate_source(project, explicit, cfg):
    candidates = [Path(explicit)] if explicit else [project/cfg['source_relative_path']]
    if not explicit and not candidates[0].is_file():
        candidates = [p for p in project.rglob('*') if p.is_file() and p.suffix.lower() in ('.mp4','.mov','.mkv') and p.stat().st_size == cfg['source_size']]
    for path in candidates:
        if path.is_file() and path.stat().st_size == cfg['source_size'] and digest(path) == cfg['source_sha256']:
            return path
    raise FileNotFoundError('Exact original 4K master missing or checksum mismatch. Place the file from '+cfg['source_url']+' at '+str(project/cfg['source_relative_path'])+' or set SOURCE_OVERRIDE. The compressed preview is not accepted.')

def load_renderer(root):
    # Only relocate paths. Preserve original code, shot timing, graphics and encoder arguments.
    path = PACKAGE/'original_scripts/render_documentary.py'
    source = path.read_text().replace("Path('/workspace/badenoch-revision-preflight')", 'Path('+repr(str(root))+')')
    source = source.replace('/usr/share/fonts/truetype/dejavu/', str(PACKAGE/'fonts')+'/')
    namespace = {'__name__':'preserved_renderer','__file__':str(path)}
    exec(compile(source,str(path),'exec'),namespace)
    expected = json.loads((PACKAGE/'timeline/shots.json').read_text())
    if namespace['shots'] != expected:
        raise RuntimeError('Preserved renderer differs from the final shot timeline')
    return namespace

def probe(path):
    data=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))
    v=next(s for s in data['streams'] if s['codec_type']=='video')
    a=next(s for s in data['streams'] if s['codec_type']=='audio')
    if not ((v['width'],v['height'])==(3840,2160) and v['codec_name']=='h264' and v['pix_fmt']=='yuv420p' and v['avg_frame_rate']=='30/1' and int(v['nb_frames'])==900 and a['codec_name']=='aac' and a['sample_rate']=='48000' and all(float(x)==30 for x in (v['duration'],a['duration'],data['format']['duration']))):
        raise RuntimeError('Export metadata failed required format checks')
    return data

def run(project, mode, source_override=None, check_only=False):
    cfg=verify_package()
    if not project.is_dir():
        raise FileNotFoundError(f'Drive project directory missing: {project}. Mount Drive and set PROJECT correctly.')
    source=locate_source(project,source_override,cfg) if mode=='render_original' else None
    if source: print('Verified exact original master:',source)
    if check_only:
        # Load definitions and validate all image/font dependencies without generating frames.
        with tempfile.TemporaryDirectory(prefix='badenoch-check-') as tmp:
            root=Path(tmp)
            for folder in ['evidence','work']:(root/folder).symlink_to(PACKAGE/folder,target_is_directory=True)
            load_renderer(root)
        print('PASS: all preserved checksums, images, fonts and timeline; no render executed')
        return
    final=project/'Final';final.mkdir(exist_ok=True)
    target=final/'Badenoch_documentary_FINAL_4K.mp4'
    if target.exists():
        if digest(target)==cfg['final_sha256']:
            print('Exact finished master already exists; refreshing companion reports:',target)
        else: raise FileExistsError(f'Refusing to overwrite a different existing file: {target}. Move/rename it before continuing.')
    if mode=='copy_exact':
        candidate=PACKAGE/'completed'/target.name
        data=probe(candidate)
    else:
        import PIL
        if PIL.__version__ != cfg['pillow']:raise RuntimeError('Install Pillow=='+cfg['pillow'])
        # Fresh workspace prevents reuse of stale shot caches.
        root=Path(tempfile.mkdtemp(prefix='badenoch-render-'))
        (root/'downloads').mkdir();(root/'downloads/original_master.mp4').symlink_to(source.resolve())
        for folder in ['evidence','work']:(root/folder).symlink_to(PACKAGE/folder,target_is_directory=True)
        renderer=load_renderer(root)
        renderer['main']()
        candidate=root/'Final'/target.name
        data=probe(candidate)
    staging=final/(target.name+'.partial')
    shutil.copyfile(candidate,staging)
    if digest(staging)!=digest(candidate):raise RuntimeError('Drive copy checksum failed; partial file retained')
    staging.rename(target)
    for name in ['Badenoch_final_storyboard.csv','Badenoch_evidence_manifest.csv']:
        shutil.copy2(PACKAGE/'historical_qc'/name,final/name)
    (final/'Badenoch_recovered_ffprobe.json').write_text(json.dumps(data,indent=2))
    historical=(PACKAGE/'historical_qc/Badenoch_4K_quality_report.txt').read_text()
    report='RECOVERY RUN\nMode: '+mode+'\nVerified Drive file: '+str(target)+'\nSHA256: '+digest(target)+'\nMeasured: 3840x2160; H.264 yuv420p; 30 fps; 900 frames; AAC 48000 Hz; 30.000 seconds.\n'
    report+='Exact original output bytes: '+str(digest(target)==cfg['final_sha256'])+'\n'
    report+='New render received metadata checks only; historical visual/audio QC below applies to the preserved original. Encoder versions can alter bytes.\n' if mode=='render_original' else 'Exact preserved output; historical QC applies.\n'
    report+='\n--- HISTORICAL REPORT (delivery status below describes the original Codex run) ---\n'+historical
    (final/'Badenoch_4K_quality_report.txt').write_text(report)
    print('VERIFIED IN MOUNTED DRIVE:',target,'bytes:',target.stat().st_size,'SHA256:',digest(target))

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--project',type=Path,required=True)
    parser.add_argument('--mode',choices=['copy_exact','render_original'],default='copy_exact')
    parser.add_argument('--source')
    parser.add_argument('--check-only',action='store_true')
    args=parser.parse_args()
    run(args.project,args.mode,args.source,args.check_only)
