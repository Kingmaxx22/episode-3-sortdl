# The 10-Line Script That Organizes Your Downloads (sortdl)

Episode 3 of the *Power-User & Developer Shortcuts* series — a vertical 9:16
Short for YouTube Shorts / TikTok / Instagram Reels.

A 10-line Python script that sorts loose files in `~/Downloads` into labelled
subfolders, purges installers older than 30 days, and runs nightly on a
schedule.

## The script

`sort_downloads.py` — **exactly 10 lines**:

```python
import shutil, time
from pathlib import Path
D = Path.home() / "Downloads"
K = {"Images": ".png .jpg .jpeg .webp", "Documents": ".pdf .docx .txt .xlsx", "Archives": ".zip .rar .7z .tar .gz", "Executables": ".exe .msi .dmg .deb"}
for f in D.iterdir():
    if not f.is_file(): continue
    if f.suffix.lower() in K["Executables"] and time.time() - f.stat().st_mtime > 30 * 86400:
        f.unlink(); continue
    d = D / next((k for k, v in K.items() if f.suffix.lower() in v.split()), "Other")
    d.mkdir(exist_ok=True); shutil.move(str(f), d / f.name)
```

`test_sort_downloads.py` proves it works **against a sandbox**, never a real
Downloads folder: it builds a messy fixture (loose PDFs, ZIPs, images,
installers, an unknown extension, a pre-existing subfolder, and an installer
backdated 45 days), runs the script verbatim with `Path.home()` redirected, and
asserts every file landed correctly, the stale installer is gone, subfolders are
untouched, and a second run is a no-op.

```bash
uv run python projects/episode-3-sortdl/test_sort_downloads.py     # ALL CHECKS PASSED
```

> **Do not point the script at a real Downloads folder to "try it".** `unlink()`
> bypasses the Recycle Bin, so the 30-day purge is irreversible. Run the test.

## What the video claims, and how it was checked

| Claim on screen | How it was verified |
| --- | --- |
| "10 lines" | `wc -l sort_downloads.py` = 10, and the excerpt shown is marked with an ellipsis |
| "12,931 files" | **measured** from the real `~/Downloads` with `find … \| wc -l` |
| Files sort by extension | asserted by the sandbox test |
| Installers >30 days are binned | asserted by the sandbox test |
| Runs nightly | a real `schtasks` command, verified by creating, running and deleting a probe task |

**The source script's "4,129 items" was invented.** The real folder held 12,931
files, so the on-screen counter and the narration use the measured number.

**Nightly schedule** — Windows Task Scheduler (cron is not available in the WSL
distro on this machine):

```powershell
schtasks /create /tn "SortDownloads" `
         /tr "python C:\path\to\sort_downloads.py" `
         /sc DAILY /st 23:00
```

## Narration

Engine: **voxcpm-gguf**. Number and word choices were measured, not guessed —
synthesised, transcribed with faster-whisper, and rewritten until the transcript
matched:

- `12,931` written as digits was read **"12,000, 931"**. The count is now spelled
  `twelve thousand nine hundred thirty one`, and in the second half of the
  sentence as `My folder held …` (a bare `Mine reached …` broke the join).
- `PDF` → `P D F` so the voice says the letters.

## Build

```bash
uv run manimations validate sortdl
uv run manimations preview  sortdl
uv run manimations final    sortdl --voiceover --engine voxcpm-gguf \
                                    --fit-narration --subtitles
uv run python projects/episode-3-sortdl/mix_sfx.py
ffmpeg -y -i projects/episode-3-sortdl/build/sortdl_final.mp4 \
          -i projects/episode-3-sortdl/build/sortdl_with_sfx.m4a \
       -map 0:v -map 1:a -map 0:s? -c:v copy -c:a copy -c:s mov_text \
       -movflags +faststart projects/episode-3-sortdl/build/sortdl_reel.mp4
```

`build/sortdl_reel.mp4` is the deliverable: video + narration + SFX + soft subs.
