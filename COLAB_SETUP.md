# Run from your tablet with Google Colab

1. Visit https://colab.research.google.com and create a new notebook.
2. Run the following cells **one at a time**. Your previous transcript and reports will remain in Drive.

```python
from google.colab import drive
drive.mount('/content/drive')
```

```python
!apt-get -qq install -y ffmpeg
!git clone https://github.com/SymplyFlorence/badenoch-vhs-video-editor.git
%cd badenoch-vhs-video-editor
!python editor.py
```

```python
!python editor.py --render
```

The output is in **MyDrive/Badenoch_VHS_Project/Previews/script_selected_clean_preview.mp4**.

Because this is a private repository, `git clone` may ask for GitHub authorization or fail. An easier alternative is Colab **File > Open notebook > GitHub** after authorizing GitHub, or upload `editor.py` and `config.json` from the repository to Colab.

The script currently exports only a clean review clip. It intentionally does not claim to have removed bad takes or generated authentic evidence. Review it before building the final documentary edit. Do not upload original client footage to GitHub.
