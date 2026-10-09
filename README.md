# Badenoch VHS evidence explainer — private audition workspace

Source videos and generated previews stay in [Google Drive](https://drive.google.com/drive/folders/1Q7nX2TXYDQ0nNnH-naKctWI3vhg8Rfzo), not GitHub.

## Current stage

- Original ~2 GB video and timestamped transcription are in Google Drive.
- Script-based cut report and candidate timings already generated in Colab.
- Preferred **review candidate**: source time **387.96–416.06 seconds** (28.1 seconds of narration). Needs editorial review, not final client delivery.
- The repo provides an editable `config.json` and `editor.py` for creating a clean 30-second source review clip. The 1.9-second remainder is a still hold with no added speech; this is **not** a final edited evidence reel.
- Existing `evidence_01.png` through `evidence_03.png` are **placeholders**; do not represent them as authentic media.

## How to use

Follow [COLAB_SETUP.md](COLAB_SETUP.md). Python stdlib and FFmpeg only.

## Next production tasks for Codex

1. Compare the approved script against `script_cut_review.csv`; **verify actual source video** around cut points and identify complete, clean takes.
2. Produce a precise edit decision list (EDL) and a seamless 30-second opening with complete sentences; use authentic speech only.
3. Add documented, verified news screenshots/footage sourced to the precise statement. Never invent articles or headlines.
4. Create polished restrained evidence-card visuals with VHS/scanline texture **only on inserts**, clean presenter, 3–6 second dwell times and motion graphics.
5. Implement timeline composition and audio leveling using FFmpeg, output 1080p 30fps H264/AAC to Drive's `Final` folder.
6. Validate duration, audio, factual accuracy and visual continuity before client submission.

## Privacy

Repository is private. Do not commit footage, client scripts, transcript with private content, downloaded media, credentials, cookies or Google Drive tokens.
