# Episode 3 — "The 10-Line Script That Organizes Your Downloads"

**Series:** Power-User & Developer Shortcuts
**Format:** vertical 9:16, 1080×1920 @ 30 fps, ~38 s, narrated, soft subtitles
**Engine:** voxcpm-gguf (quantized VoxCPM2)
**CTA:** "Follow for Episode 4"

---

## Voiceover script

| # | In | Out | Narration |
| --- | --- | --- | --- |
| 01 | 0.0 s | 5.4 s | If your Downloads folder looks like an absolute landfill right now, stop sorting it by hand. |
| 02 | 5.4 s | 16.4 s | We let files pile up until finding one P D F means five minutes of scrolling. My folder held twelve thousand nine hundred thirty one files. |
| 03 | 16.4 s | 25.8 s | Instead, write a ten line Python script. It reads each file extension and moves the file into a labelled subfolder. |
| 04 | 25.8 s | 32.5 s | Run it once and the folder sorts itself in seconds. It can even bin installers older than thirty days. |
| 05 | 32.5 s | 38.1 s | Schedule it to run every night and your storage stays clean on autopilot. Follow for Episode four. |

Timings are the **rendered** scene durations, not the planned ones.

Two spellings in that table are deliberate and were measured, not guessed — the
narration was synthesised and transcribed back until the transcript matched:

- `12,931` as digits was read *"12,000, 931"*, so the count is spelled out:
  **twelve thousand nine hundred thirty one**.
- `PDF` was read as a word, so it is written **P D F** to make the voice say the
  letters.

## On-screen text

**01 — The landfill**

- header: `The landfill` · index `01`
- window title: `Downloads — 12,931 files`
- loose file chips: `invoice (3).pdf`, `screenshot 42.png`, `setup.exe`,
  `backup.zip`, `photo.jpg`, `notes.txt`, `installer.msi`, `meme.webp`,
  `report.docx`, `archive (1).zip`, `IMG_2043.jpg`, `sheet.xlsx`
- headline: **STOP SORTING** / by hand

**02 — Why it hurts**

- header: `Why it hurts` · index `02`
- counter, running up to the measured count: `12,931` / `files in Downloads`
- search field: `search: invoice.pdf` (with a cursor that crawls and never returns)
- label: `five minutes of scrolling`

**03 — The script**

- header: `The script` · index `03`
- badge: `10 LINES OF PYTHON`
- a code panel showing an **excerpt** of the real file, marked with `…`
- the folder map: `Images .png .jpg .webp` · `Documents .pdf .docx .txt` ·
  `Archives .zip .rar .7z` · `Executables .exe .msi` · `Other everything else`

**04 — Run it once**

- header: `Run it once` · index `04`
- terminal: `$ python sort_downloads.py`, then the five destination folders
- label: `installers older than 30 days are binned`

**05 — On autopilot**

- header: `On autopilot` · index `05`
- badge: `EVERY NIGHT AT 23:00`
- the real command:
  `schtasks /create` `/tn SortDownloads` `/tr "python sort_downloads.py"`
  `/sc DAILY /st 23:00`
- CTA: **Follow for Episode 4**

## The script itself

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

> **Do not point this at a real Downloads folder to "try it".**
> `unlink()` bypasses the Recycle Bin, so the 30-day purge is irreversible.
> Run `test_sort_downloads.py` instead — it builds a sandbox and runs the real
> script against that.

## What the video claims, and how it was checked

| Claim on screen | How it was verified |
| --- | --- |
| "10 lines" | `wc -l sort_downloads.py` = 10; the panel shows an excerpt, marked with `…` |
| "12,931 files" | **measured** from the real `~/Downloads` — the draft's "4,129 items" was invented |
| Files sort by extension | asserted by `test_sort_downloads.py` against a sandbox |
| Installers >30 days are binned | asserted by the same test |
| Runs nightly | a real `schtasks` command, checked by creating, running and deleting a probe task |

**Nightly schedule** — Windows Task Scheduler (cron is not available in the WSL
distro on this machine):

```powershell
schtasks /create /tn "SortDownloads" `
         /tr "python C:\path\to\sort_downloads.py" `
         /sc DAILY /st 23:00
```

## Files

| File | What it is |
| --- | --- |
| `sort_downloads.py` | the 10-line script the episode is about |
| `test_sort_downloads.py` | sandbox test — builds a messy fake Downloads, runs the real script against it, asserts the result |
| `project.yaml` | the episode brief: per-scene narration, accents, durations, visuals |
| `scenes.py` | the Manim CE scene source. Needs the `manimations` framework, which is **not** included here — it is reference for how the visuals are built |
| `subtitles.srt` | the rendered soft subtitles |
| `EPISODE-NOTES.md` | the original episode notes (build commands, engine caveats) |
