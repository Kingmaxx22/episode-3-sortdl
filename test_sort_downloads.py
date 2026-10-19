"""Prove sort_downloads.py actually works, on a sandbox it cannot damage.

Builds a fake Downloads folder with the messy mixture the video shows (loose
PDFs, ZIPs, images, installers, duplicates, and an installer backdated past the
30-day cutoff), runs the real script against it via a patched ``Path.home``, and
asserts every file landed where the video claims.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import textwrap
import time
from pathlib import Path

SANDBOX = Path(__file__).resolve().parent / "build" / "scratch" / "sortdl_sandbox"
SCRIPT = Path(__file__).resolve().parent / "sort_downloads.py"

MESSY = [
    ("invoice.pdf", 0), ("report.docx", 0), ("notes.txt", 0), ("sheet.xlsx", 0),
    ("screenshot.png", 0), ("photo.jpg", 0), ("meme.webp", 0),
    ("project.zip", 0), ("backup.7z", 0), ("archive.tar.gz", 0),
    ("setup.exe", 0), ("installer.msi", 0), ("weird.xyz", 0),
]
STALE_INSTALLER = ("old_setup.exe", 45 * 86400)   # older than the 30-day cutoff


def build() -> Path:
    if SANDBOX.exists():
        shutil.rmtree(SANDBOX)
    dl = SANDBOX / "Downloads"
    dl.mkdir(parents=True)
    for name, age in MESSY + [STALE_INSTALLER]:
        p = dl / name
        p.write_text("x")
        if age:
            old = time.time() - age
            import os
            os.utime(p, (old, old))
    # a subfolder must be left alone
    (dl / "already_a_folder").mkdir()
    return dl


def main() -> int:
    dl = build()
    before = sorted(p.name for p in dl.iterdir())

    # Run the script with Path.home() redirected to the sandbox.  The script is
    # executed verbatim — only the home directory is faked, so what is tested is
    # the real code, not a copy.
    runner = SANDBOX / "_run.py"
    runner.write_text(textwrap.dedent(f"""
        import pathlib, runpy, sys
        _real = pathlib.Path.home
        pathlib.Path.home = classmethod(lambda cls: pathlib.Path(r"{SANDBOX}"))
        runpy.run_path(r"{SCRIPT}", run_name="__main__")
        pathlib.Path.home = _real
    """), encoding="utf-8")

    proc = subprocess.run([sys.executable, str(runner)], capture_output=True, text=True)
    if proc.returncode != 0:
        print("SCRIPT FAILED")
        print(proc.stdout)
        print(proc.stderr)
        return 1

    print(f"ran sort_downloads.py ({len(SCRIPT.read_text().splitlines())} lines)\n")
    print(f"before: {len(before)} entries in Downloads/")
    print("  " + "  ".join(before) + "\n")

    problems: list[str] = []
    expected = {
        "Documents": {"invoice.pdf", "report.docx", "notes.txt", "sheet.xlsx"},
        "Images": {"screenshot.png", "photo.jpg", "meme.webp"},
        "Archives": {"project.zip", "backup.7z", "archive.tar.gz"},
        "Executables": {"setup.exe", "installer.msi"},
        "Other": {"weird.xyz"},
    }
    for folder, want in expected.items():
        d = dl / folder
        got = {p.name for p in d.iterdir()} if d.is_dir() else set()
        status = "OK " if got == want else "!! "
        if got != want:
            problems.append(f"{folder}: want {sorted(want)}, got {sorted(got)}")
        print(f"{status}{folder:11} {sorted(got)}")

    # the stale installer must be gone entirely
    gone = not (dl / "old_setup.exe").exists() and not any(
        (dl / f / "old_setup.exe").exists() for f in expected
    )
    print(f"{'OK ' if gone else '!! '}stale installer purged (>30 days): {gone}")
    if not gone:
        problems.append("old_setup.exe survived the 30-day purge")

    # loose files must be gone from the root, and the existing folder untouched
    loose = [p.name for p in dl.iterdir() if p.is_file()]
    print(f"{'OK ' if not loose else '!! '}loose files left in Downloads/: {loose}")
    if loose:
        problems.append(f"loose files remain: {loose}")

    sub = (dl / "already_a_folder").is_dir()
    print(f"{'OK ' if sub else '!! '}pre-existing subfolder untouched: {sub}")
    if not sub:
        problems.append("a subfolder was moved or deleted")

    # idempotence: a second run must be harmless
    subprocess.run([sys.executable, str(runner)], capture_output=True, text=True)
    still = {f: sorted(p.name for p in (dl / f).iterdir()) for f in expected if (dl / f).is_dir()}
    print(f"\nsecond run (idempotence): {still}")
    if any(sorted(still.get(f, [])) != sorted(v) for f, v in expected.items()):
        problems.append("second run changed the result")

    print()
    if problems:
        print("FAILURES:")
        for p in problems:
            print("  -", p)
        return 1
    print("ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
