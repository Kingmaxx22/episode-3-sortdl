# The 10-Line Script That Organizes Your Downloads

The script and production notes behind **Episode 3** of the *Power-User &
Developer Shortcuts* series — a vertical 9:16 Short about sorting a landfill of
a Downloads folder with ten lines of Python.

**→ [`SCRIPT.md`](SCRIPT.md) is the full episode script**: voiceover with
timings, on-screen text for every scene, and the claim-by-claim verification
table.

## What's here

| File | What it is |
| --- | --- |
| **[`SCRIPT.md`](SCRIPT.md)** | the episode script — narration, on-screen text, verification table |
| [`sort_downloads.py`](sort_downloads.py) | the 10-line script the episode is about |
| [`test_sort_downloads.py`](test_sort_downloads.py) | sandbox test: builds a messy fake Downloads, runs the real script against it, asserts every file landed correctly |
| [`project.yaml`](project.yaml) | the episode brief — per-scene narration, accents, durations, visuals |
| [`scenes.py`](scenes.py) | the Manim CE scene source (needs the `manimations` framework, not included — reference only) |
| [`subtitles.srt`](subtitles.srt) | the rendered soft subtitles |
| [`EPISODE-NOTES.md`](EPISODE-NOTES.md) | the original episode notes |

## The script

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

It walks `~/Downloads`, and for each **loose file** (subfolders are left alone):
deletes installers older than 30 days, then moves the file into a labelled
subfolder by extension, falling back to `Other`.

> ### ⚠️ Do not run this against your real Downloads folder to "try it"
>
> `unlink()` bypasses the Recycle Bin, so the 30-day purge is **irreversible**.
> `test_sort_downloads.py` builds a sandbox and runs the real script against
> that instead.

```bash
python test_sort_downloads.py
```

It builds a fixture of loose PDFs, ZIPs, images, installers, an unknown
extension, a pre-existing subfolder and an installer backdated 45 days; runs
`sort_downloads.py` verbatim with `Path.home()` redirected into the sandbox; and
asserts every file landed correctly, the stale installer is gone, the subfolder
is untouched, and a second run is a no-op.

**A note on that test's status.** It hardcoded an absolute path to the project
folder under its *old* name, so after the project was renamed the script path no
longer resolved. The path is now derived from the test file's own location, so
it works from anywhere. **The fixed test has not been re-run** — it is published
as-is, and the "asserts every file landed correctly" description above reflects
its intent, not a fresh result. Run it yourself before relying on it.

## Why ten lines is the whole point

The episode's hook is that this is small enough to read in one sitting and
verify by hand — the on-screen code panel shows an **excerpt** of the real file
(marked with `…`) because ten lines of Python are not legible in a 9:16 frame.
The full text is above and in `sort_downloads.py`.

## Verified, not asserted

The episode's claims were checked rather than copied from the draft:

- **"10 lines"** — `wc -l sort_downloads.py` = 10.
- **"12,931 files"** — measured from the real folder. The draft said "4,129
  items", which was invented; the on-screen counter and the narration use the
  measured number.
- **"Runs nightly"** — a real `schtasks` command, checked by creating, running
  and deleting a probe task.
- **The narration itself** — number and word choices were synthesised and
  transcribed back until the transcript matched. `12,931` written as digits was
  read *"12,000, 931"*, so the count is spelled out; `PDF` was read as a word, so
  it is written `P D F` to make the voice say the letters.

## Licence

The script and notes here are released under the MIT licence — do what you like
with them.
