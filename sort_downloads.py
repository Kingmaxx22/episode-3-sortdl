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
