# Exact final-edit recovery

Open [Badenoch_FINAL_4K_Render.ipynb in Colab](https://colab.research.google.com/github/SymplyFlorence/badenoch-vhs-video-editor/blob/badenoch-final-recovery-v1/Badenoch_FINAL_4K_Render.ipynb) and choose **Runtime → Run all**. Mount the Google account holding `MyDrive/Badenoch_VHS_Project`.

The default `copy_exact` mode copies the preserved completed MP4 from GitHub to `Badenoch_VHS_Project/Final/Badenoch_documentary_FINAL_4K.mp4`, checks the copied checksum, and writes the storyboard, evidence manifest and recovery quality report there. No rendering is needed. The exact completed MP4 is also stored in `completed/` in this repository (40,283,921 bytes).

Set `MODE = 'render_original'` to run the original final editing pipeline against the Drive master. This uses precisely the same final renderer, 900-frame timeline, source cuts, screenshot pixels, highlight coordinates, graphic code, portrait crops, font binaries and normalized recorded audio. No original project file is changed. Local Colab scratch storage holds encoded shots; the validated completed output is copied to mounted Drive. Existing different final MP4s cause an explicit stop; move them aside yourself if needed.

## Original master: the only required asset too large for Git

- Original URL: https://drive.google.com/file/d/1yRy30VswuWiytEBTy6hm781Gd69FXe4D/view
- Existing Drive location: `Badenoch_VHS_Project/Raw video/Copy of Badenoch RUTHLESSLY DESTROYED In Commons As Jenri.mp4`
- Size: 2,009,538,306 bytes
- SHA-256: `813f122827087e16802664fecbe82c3e61a6eeacb6335df7e2e9908d04cfad90`

The master is already in the project's Raw video folder. If using another Google account, open the original URL and save a copy into that exact folder in My Drive. Alternatively set `SOURCE_OVERRIDE` to its mounted Drive path. The notebook searches the project for a matching-size media file if the expected name is absent, then verifies the full checksum. It never downloads or accepts the compressed preview as a replacement. `copy_exact` does not require the master because it transfers the already finished MP4.

All other required assets are committed as normal Git files, not Git LFS pointers: two licensed portraits (18.1 and 21.0 MB), actual Sky screenshots, geometry, fonts and the exact normalized narration WAV (8.6 MB). No manual evidence download or recapture is required. Source URLs, attribution, publication dates and rights are retained in `historical_qc/Badenoch_evidence_manifest.csv` and `evidence/portrait_rights.json`. `preserved_assets.json` records every preserved file's size and SHA-256.

## Preservation and reproducibility

- `original_scripts/render_documentary.py`: byte-for-byte original final renderer; includes motion-graphic generation, colors, coordinates, shot timeline and encoder configuration.
- `original_scripts/render_narration_review.py`: byte-for-byte original audio assembly/normalization and review-render provenance. Archived only; the notebook uses its exact resulting WAV, avoiding an unnecessary intermediate review render.
- `original_scripts/capture_sky.py`, `fetch_evidence.py`: original acquisition code, archived only; never automatically recapture evidence.
- `timeline/shots.json`, `work/narration_edl.json`: final picture timeline and frame-accurate source/audio EDL.
- `config.json`: original master identity and original FFmpeg build information. Pillow is pinned to 12.3.0; exact fonts are bundled with their license.
- `recover.py`: relocation wrapper. It verifies assets, changes only workspace/font paths when loading the preserved renderer, and confirms its timeline matches the frozen JSON. Render mode uses a fresh scratch directory, so stale shot caches cannot be substituted.
- `historical_qc/`: original metadata, contact sheet, manifests and report, preserved without rewriting historical findings.

A newly encoded result can differ in bytes with Colab's FFmpeg/libx264 and platform versions. The editorial recipe is preserved, but only `copy_exact` guarantees the original checksum `faed72ed5740d78ff4568581ef035600e0bcc0bf0668898163173b9766341392`. No footage, stills or graphics were regenerated during recovery.

The historical report records outstanding listening review and Sky excerpt republication-rights concerns; recovering files does not resolve them. Its old Drive authentication failure is historical: this notebook instead uses your mounted Drive. Rebuild mode performs measured format checks; it does not claim a new full visual/listening review.

## Validation without rendering

Run `python final_recovery/recover.py --project /path/to/project --mode render_original --source /path/to/master.mp4 --check-only` to verify source, all hashes, images, fonts and the timeline without generating a frame. `copy_exact --check-only` checks the preserved package without requiring the source.
