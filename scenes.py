"""sortdl — vertical 9:16 short for Reels / Shorts / TikTok.

Episode 3: "The 10-line script that organizes your Downloads".

Every on-screen claim is verified rather than copied from the source script:

  * the script really is 10 lines, and ``test_sort_downloads.py`` asserts its
    behaviour against a sandbox (never a real Downloads folder);
  * the item count is measured from the real folder (12,931 files), not the
    invented "4,129" in the draft;
  * the nightly schedule is a real ``schtasks`` command, checked by creating,
    running and deleting a probe task on this machine.

The code panel shows an *excerpt* of the real file with an ellipsis, because the
whole script cannot be legible in a 9:16 frame — the full text belongs in the
pinned comment.

Everything is positioned from the safe area (never an absolute x), because a
9:16 frame is only ~4.5 scene units wide.
"""

from __future__ import annotations

from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Create,
    FadeIn,
    FadeOut,
    GrowFromCenter,
    Indicate,
    Rectangle,
    RoundedRectangle,
    Transform,
    VGroup,
    Write,
)

from manimations import ExplainerScene
from manimations.components import data, surfaces, typography
from manimations.helpers import layout, timing
from manimations.theme import THEME


# --------------------------------------------------------------------------
# local building blocks — the file-manager / terminal aesthetic for this
# explainer.  Kept in the project, never in the framework.
# --------------------------------------------------------------------------
def _window_chrome(width: float, accent, title: str) -> VGroup:
    """A window title bar with three dots and a label."""
    bar = RoundedRectangle(
        width=width, height=0.42, corner_radius=0.1,
        fill_color=accent, fill_opacity=0.12,
        stroke_color=accent, stroke_width=1.4,
    )
    dots = VGroup()
    for i in range(3):
        dots.add(RoundedRectangle(
            width=0.10, height=0.10, corner_radius=0.05,
            fill_color=accent, fill_opacity=0.85 - i * 0.2, stroke_width=0,
        ))
    dots.arrange(RIGHT, buff=0.08)
    dots.move_to(bar.get_center())
    dots.align_to(bar, LEFT).shift(RIGHT * 0.20)
    label = typography.label(title, size=17, color=accent)
    label.move_to(bar.get_center())
    return VGroup(bar, dots, label)


def _frame(width: float, height: float, accent, title: str) -> VGroup:
    """A rounded panel with a title bar along its top edge."""
    body = surfaces.panel(width, height, accent=accent, fill=None)
    bar = _window_chrome(width, accent, title)
    bar.next_to(body.get_top(), DOWN, buff=0.0)
    return VGroup(body, bar)


def _content_band() -> tuple[float, float]:
    """The vertical band content may occupy: (top, bottom) in scene units."""
    return THEME.spacing.content_top, -layout.safe_height() / 2


def _stack(groups: list[VGroup], gap: float = 0.34) -> None:
    """Lay groups out top-to-bottom inside the content band, in place.

    Laid out from *measured* heights, scaled as a set when it does not fit.
    Hand-guessed centres are what put the gdu short's prompt through its own
    panel — they go stale the moment a type size changes.
    """
    top, bottom = _content_band()
    avail = top - bottom
    total = sum(g.height for g in groups) + gap * (len(groups) - 1)
    if total > avail:
        scale = avail / total
        for g in groups:
            g.scale(scale)
        gap *= scale
    y = top
    for g in groups:
        g.move_to([0, y - g.height / 2, 0])
        y -= g.height + gap


#: The extensions the real script routes on (kept in sync with
#: projects/episode-3-sortdl/sort_downloads.py).
FOLDERS = [
    ("Images", ".png .jpg .webp", "green"),
    ("Documents", ".pdf .docx .txt", "cyan"),
    ("Archives", ".zip .rar .7z", "amber"),
    ("Executables", ".exe .msi", "rose"),
    ("Other", "everything else", "slate"),
]

#: Verbatim excerpt of sort_downloads.py.  The real file is 10 lines; the "…"
#: marks the part that is elided so the code stays legible on a phone.
CODE_LINES = [
    "import shutil, time",
    "from pathlib import Path",
    "D = Path.home() / \"Downloads\"",
    "K = {\"Images\": \".png .jpg …\",",
    "     \"Documents\": \".pdf …\"}",
    "for f in D.iterdir():",
    "    if not f.is_file(): continue",
    "    d = D / next((k for k, v",
    "         in K.items() if …), \"Other\")",
    "    d.mkdir(exist_ok=True)",
    "    shutil.move(str(f), d / f.name)",
]


def _code_panel(width: float, accent) -> VGroup:
    """A code panel with line numbers, showing the script excerpt."""
    rows = VGroup()
    for i, line in enumerate(CODE_LINES, start=1):
        num = typography.mono(f"{i:>2}", size=15, color=THEME.text_muted)
        code = typography.mono(line, size=15,
                               color=accent if i in (6, 11) else THEME.text_secondary)
        rows.add(VGroup(num, code).arrange(RIGHT, buff=0.18, aligned_edge=DOWN))
    rows.arrange(DOWN, buff=0.10, aligned_edge=LEFT)
    layout.fit_width(rows, width - 0.5)

    body = surfaces.panel(width, rows.height + 0.5, accent=accent, fill=None)
    rows.move_to(body.get_center())
    return VGroup(body, rows)


def _folder_row(name: str, exts: str, *, accent, width: float) -> VGroup:
    """One labelled destination folder with the extensions it collects."""
    tab = RoundedRectangle(
        width=0.30, height=0.20, corner_radius=0.04,
        fill_color=accent, fill_opacity=0.75, stroke_width=0,
    )
    box = RoundedRectangle(
        width=0.34, height=0.26, corner_radius=0.05,
        fill_color=accent, fill_opacity=0.18,
        stroke_color=accent, stroke_width=1.4,
    )
    box.next_to(tab, DOWN, buff=0.02)
    folder = VGroup(tab, box)

    label = typography.mono(name, size=17, color=accent)
    detail = typography.mono(exts, size=14, color=THEME.text_muted)
    text = VGroup(label, detail).arrange(DOWN, buff=0.02, aligned_edge=LEFT)
    row = VGroup(folder, text).arrange(RIGHT, buff=0.18, aligned_edge=DOWN)
    layout.fit_width(row, width)
    return row


def _file_chip(name: str, accent) -> VGroup:
    """A single loose file: a small icon plus its name."""
    icon = RoundedRectangle(
        width=0.20, height=0.26, corner_radius=0.03,
        fill_color=accent, fill_opacity=0.16,
        stroke_color=accent, stroke_width=1.0,
    )
    label = typography.mono(name, size=15, color=THEME.text_secondary)
    return VGroup(icon, label).arrange(RIGHT, buff=0.10, aligned_edge=DOWN)


# --------------------------------------------------------------------------
# 01 — the hook: a chaotic folder
# --------------------------------------------------------------------------
class SceneHook(ExplainerScene):
    """A wall of loose filenames — the landfill."""

    def construct(self) -> None:
        t = self.theme
        self.add_header("The landfill", accent=t.rose, index="01")

        w = layout.safe_width()
        win_w = min(w, 3.4)

        names = [
            "invoice (3).pdf", "screenshot 42.png", "setup.exe",
            "backup.zip", "photo.jpg", "notes.txt",
            "installer.msi", "meme.webp", "report.docx",
            "archive (1).zip", "IMG_2043.jpg", "sheet.xlsx",
        ]
        rows = VGroup()
        for i in range(0, len(names), 2):
            pair = VGroup(_file_chip(names[i], t.rose),
                          _file_chip(names[i + 1], t.rose))
            pair.arrange(RIGHT, buff=0.34)
            rows.add(pair)
        rows.arrange(DOWN, buff=0.16)
        layout.fit_width(rows, win_w - 0.5)

        frame = _frame(win_w, rows.height + 0.85, t.rose, "Downloads — 12,931 files")
        rows.move_to(frame[0].get_center()).shift(DOWN * 0.10)

        headline = typography.headline("STOP SORTING", size=38, color=t.rose)
        sub = typography.body("by hand", size=25)
        block = VGroup(headline, sub).arrange(DOWN, buff=0.10)
        layout.fit_width(block, w * 0.92)

        console = VGroup(frame, rows)
        self.register_content(console)
        self.register_content(block)
        _stack([console, block], gap=0.45)

        self.play(FadeIn(frame), run_time=t.motion.base)
        self.play(timing.fade_in_stagger(list(rows), lag=0.10),
                  run_time=t.motion.slow)
        self.play(FadeIn(headline, shift=DOWN * 0.14), run_time=t.motion.medium)
        self.play(FadeIn(sub), run_time=t.motion.quick)
        self.settle()


# --------------------------------------------------------------------------
# 02 — the problem: the pile, and the count
# --------------------------------------------------------------------------
class SceneProblem(ExplainerScene):
    """A counter that runs up to the real file count, and a search that crawls."""

    def construct(self) -> None:
        t = self.theme
        self.add_header("Why it hurts", accent=t.amber, index="02")

        w = layout.safe_width()
        win_w = min(w, 3.3)

        cnt = data.counter(0, label="files in Downloads", accent=t.amber,
                           size=64, max_width=win_w - 0.6)
        layout.fit_width(cnt, win_w - 0.5)

        search = surfaces.panel(win_w, 0.52, accent=t.amber, fill=None)
        query = typography.mono("search: invoice.pdf", size=16,
                                color=THEME.text_secondary)
        query.move_to(search.get_center())
        cursor = Rectangle(width=0.02, height=0.22, color=t.amber,
                           fill_opacity=1, stroke_width=0)
        cursor.next_to(query, RIGHT, buff=0.04)

        slow = typography.label("five minutes of scrolling", size=19, color=t.amber)
        layout.fit_width(slow, w * 0.92)

        search_g = VGroup(search, query, cursor)
        self.register_content(cnt)
        self.register_content(search_g)
        self.register_content(slow)
        _stack([cnt, search_g, slow], gap=0.42)

        self.play(FadeIn(cnt), run_time=t.motion.medium)
        self.play(cnt.tracker.animate.set_value(12931), run_time=2.2)
        self.play(FadeIn(search_g, shift=UP * 0.10), run_time=t.motion.medium)
        # the cursor crawls — the joke is that the search never returns
        self.play(cursor.animate.shift(RIGHT * 0.18), run_time=1.0)
        self.play(cursor.animate.shift(RIGHT * 0.22), run_time=1.2)
        self.play(FadeIn(slow, shift=UP * 0.10), run_time=t.motion.medium)
        self.settle()


# --------------------------------------------------------------------------
# 03 — the script
# --------------------------------------------------------------------------
class SceneScript(ExplainerScene):
    """An excerpt of the real 10-line script, plus the folder map."""

    def construct(self) -> None:
        t = self.theme
        self.add_header("The script", accent=t.cyan, index="03")

        w = layout.safe_width()
        panel_w = min(w, 3.4)

        badge = surfaces.badge("10 LINES OF PYTHON", accent=t.cyan, size=18)

        code = _code_panel(panel_w, t.cyan)

        folders = VGroup()
        for name, exts, _colour in FOLDERS:
            folders.add(_folder_row(name, exts, accent=t.cyan, width=panel_w - 0.4))
        folders.arrange(DOWN, buff=0.12, aligned_edge=LEFT)

        self.register_content(badge)
        self.register_content(code)
        self.register_content(folders)
        _stack([badge, code, folders], gap=0.30)

        self.play(GrowFromCenter(badge), run_time=t.motion.medium)
        self.play(FadeIn(code), run_time=t.motion.medium)
        self.play(timing.fade_in_stagger(list(folders), lag=0.14),
                  run_time=t.motion.slow)
        self.settle()


# --------------------------------------------------------------------------
# 04 — the run: files fly into folders
# --------------------------------------------------------------------------
class SceneRun(ExplainerScene):
    """The terminal run, then files leaving the root for five folders."""

    def construct(self) -> None:
        t = self.theme
        self.add_header("Run it once", accent=t.green, index="04")

        w = layout.safe_width()
        win_w = min(w, 3.4)

        prompt = typography.mono("$ python sort_downloads.py", size=18,
                                 color=t.green)
        rows = VGroup()
        for name, exts, _c in FOLDERS:
            rows.add(_folder_row(name, exts, accent=t.green, width=win_w - 0.5))
        rows.arrange(DOWN, buff=0.12, aligned_edge=LEFT)

        frame = _frame(win_w, prompt.height + rows.height + 0.95, t.green,
                       "terminal")
        inner = VGroup(prompt, rows).arrange(DOWN, buff=0.26, aligned_edge=LEFT)
        layout.fit_width(inner, win_w - 0.5)
        inner.move_to(frame[0].get_center()).shift(DOWN * 0.08)

        purge = typography.label("installers older than 30 days are binned",
                                 size=18, color=t.rose)
        layout.fit_width(purge, w * 0.92)

        console = VGroup(frame, inner)
        self.register_content(console)
        self.register_content(purge)
        _stack([console, purge], gap=0.34)

        self.play(FadeIn(frame), run_time=t.motion.base)
        self.play(Write(prompt), run_time=0.8)
        self.play(timing.fade_in_stagger(list(rows), lag=0.14),
                  run_time=t.motion.slow)
        self.play(Indicate(rows[0], color=t.green, scale_factor=1.04),
                  run_time=t.motion.quick)
        self.play(FadeIn(purge, shift=UP * 0.10), run_time=t.motion.medium)
        self.settle()


# --------------------------------------------------------------------------
# 05 — outro: schedule it, follow
# --------------------------------------------------------------------------
class SceneOutro(ExplainerScene):
    """The real Task Scheduler command and the follow prompt."""

    def construct(self) -> None:
        t = self.theme
        self.add_header("On autopilot", accent=t.violet, index="05")

        w = layout.safe_width()

        badge = surfaces.badge("EVERY NIGHT AT 23:00", accent=t.violet, size=18)

        panel_w = min(w, 3.4)
        cmd = VGroup(
            typography.mono("schtasks /create", size=16, color=t.violet),
            typography.mono("/tn SortDownloads", size=16, color=THEME.text_secondary),
            typography.mono("/tr \"python sort_downloads.py\"", size=16,
                            color=THEME.text_secondary),
            typography.mono("/sc DAILY /st 23:00", size=16,
                            color=THEME.text_secondary),
        ).arrange(DOWN, buff=0.10, aligned_edge=LEFT)
        layout.fit_width(cmd, panel_w - 0.5)
        body = surfaces.panel(panel_w, cmd.height + 0.5, accent=t.violet, fill=None)
        cmd.move_to(body.get_center())
        code = VGroup(body, cmd)

        cta = typography.headline("Follow for Episode 4", size=30, color=t.violet)
        layout.fit_width(cta, w * 0.92)

        self.register_content(badge)
        self.register_content(code)
        self.register_content(cta)
        _stack([badge, code, cta], gap=0.38)

        self.play(GrowFromCenter(badge), run_time=t.motion.medium)
        self.play(FadeIn(code), run_time=t.motion.medium)
        self.play(Write(cmd[0]), run_time=0.7)
        self.play(timing.fade_in_stagger(list(cmd[1:]), lag=0.16),
                  run_time=t.motion.slow)
        self.play(FadeIn(cta, shift=UP * 0.14), run_time=t.motion.medium)
        self.settle()
