"""Colab-friendly FFmpeg proof-of-concept render. Uses existing Google Drive video.
No AI claims of visual inspection; review cuts and replace placeholder cards manually.
"""
import json, subprocess, argparse
from pathlib import Path

def run(cmd):
    print(" ".join(str(x) for x in cmd))
    subprocess.run([str(x) for x in cmd], check=True)

def find_source(base, cfg):
    candidates = list(base.rglob(cfg["raw_file"]))
    if not candidates:
        candidates = [p for p in base.rglob("*.mp4") if "PREVIEW" not in str(p).upper() and "FINAL" not in str(p).upper()]
    if not candidates:
        raise FileNotFoundError("Source footage not found in " + str(base))
    return candidates[0]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.json")
    parser.add_argument("--render", action="store_true", help="Render preview; requires ffmpeg")
    args = parser.parse_args()
    cfg = json.loads(Path(args.config).read_text())
    base = Path(cfg["drive_project"])
    video = find_source(base, cfg)
    start, end = float(cfg["source_start"]), float(cfg["source_end"])
    if end <= start:
        raise ValueError("Invalid source time range")
    print("Source:", video, "selected:",start,end, "duration:",round(end-start,2))
    print("Evidence cards are placeholders until replaced with verified sources.")
    if not args.render:
        print("Dry-run complete. To render: python editor.py --render")
        return
    output = base / "Previews" / "script_selected_clean_preview.mp4"
    output.parent.mkdir(parents=True,exist_ok=True)
    duration = end-start
    # Work from precise segment, with a final 1.9s hold on last frame;
    # no altered spoken words, music, or evidence added automatically.
    command=["ffmpeg","-y","-ss",str(start),"-t",str(duration),"-i",str(video),
       "-filter_complex",
       f"[0:v]fps=30,scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,tpad=stop_mode=clone:stop_duration={max(0,30-duration):.3f},trim=duration=30,format=yuv420p[v];"
       f"[0:a]aresample=async=1:first_pts=0,apad,atrim=duration=30[a]",
       "-map","[v]","-map","[a]","-c:v","libx264","-preset","veryfast","-crf","22","-r","30",
       "-c:a","aac","-b:a","160k","-movflags","+faststart",str(output)]
    run(command)
    print("Review output:", output)
if __name__=="__main__":
    main()
