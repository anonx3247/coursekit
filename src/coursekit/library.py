"""On-disk course library: plain JSON + markdown, designed to be read by humans and agents.

Layout:
  <library>/
    CLAUDE.md                       how an agent should navigate the library
    <course>/
      course.json                   metadata + ordered lesson list
      README.md                     generated index (lessons, durations, status, TL;DRs)
      lessons/<NNN>-<slug>/
        transcript.md               timestamped paragraphs, each linking to YouTube at that time
        transcript.json             raw segments (used by the player for sync)
        notes.md                    AI notes: TL;DR, Outline (with skip markers), details, refs...
        annotations.md              Q&A / references / code added later by Claude via MCP
    .state/                         player state & progress (not content)
"""
from __future__ import annotations

import json
import os
import re
import unicodedata
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LIBRARY = Path(os.environ.get("COURSEKIT_LIBRARY", REPO / "library")).expanduser()
PORT = int(os.environ.get("COURSEKIT_PORT", "8765"))


def state_dir() -> Path:
    d = LIBRARY / ".state"
    d.mkdir(parents=True, exist_ok=True)
    return d


# ---------- helpers ----------

def slugify(text: str, maxlen: int = 60) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text[:maxlen].rstrip("-") or "untitled"


def fmt_ts(seconds: float) -> str:
    s = int(seconds or 0)
    return f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}"


def parse_ts(ts: str | float | int) -> float:
    if isinstance(ts, (int, float)):
        return float(ts)
    ts = ts.strip()
    if re.fullmatch(r"\d+(\.\d+)?", ts):
        return float(ts)
    parts = [float(p) for p in ts.split(":")]
    total = 0.0
    for p in parts:
        total = total * 60 + p
    return total


def yt_url(video_id: str, t: float | None = None) -> str:
    u = f"https://www.youtube.com/watch?v={video_id}"
    return f"{u}&t={int(t)}s" if t else u


# ---------- courses ----------

def course_dir(slug: str) -> Path:
    return LIBRARY / slug


def list_courses() -> list[dict]:
    if not LIBRARY.exists():
        return []
    out = []
    for p in sorted(LIBRARY.iterdir()):
        f = p / "course.json"
        if f.exists():
            out.append(json.loads(f.read_text()))
    return out


def load_course(slug: str) -> dict:
    f = course_dir(slug) / "course.json"
    if not f.exists():
        # allow fuzzy match on slug prefix / title
        matches = [c for c in list_courses() if slug.lower() in c["slug"] or slug.lower() in c["title"].lower()]
        if len(matches) == 1:
            return matches[0]
        known = ", ".join(c["slug"] for c in list_courses()) or "(none)"
        raise KeyError(f"Unknown course '{slug}'. Known courses: {known}")
    return json.loads(f.read_text())


def save_course(course: dict) -> None:
    d = course_dir(course["slug"])
    d.mkdir(parents=True, exist_ok=True)
    (d / "course.json").write_text(json.dumps(course, indent=2, ensure_ascii=False) + "\n")


def find_lesson(course: dict, ref: str | int) -> dict:
    """Find a lesson by playlist index (1-based), video id, or slug fragment."""
    ref_s = str(ref).strip()
    for l in course["lessons"]:
        if ref_s == str(l["index"]) or ref_s == l["video_id"] or ref_s == l["dir"]:
            return l
    hits = [l for l in course["lessons"] if ref_s.lower() in l["dir"] or ref_s.lower() in l["title"].lower()]
    if len(hits) == 1:
        return hits[0]
    raise KeyError(f"No unique lesson '{ref}' in course {course['slug']}")


def lesson_dir(course: dict, lesson: dict) -> Path:
    return course_dir(course["slug"]) / "lessons" / lesson["dir"]


def lesson_status(course: dict, lesson: dict) -> dict:
    d = lesson_dir(course, lesson)
    return {
        "transcript": (d / "transcript.md").exists(),
        "notes": (d / "notes.md").exists(),
        "annotations": (d / "annotations.md").exists(),
    }


def read_text(p: Path) -> str | None:
    return p.read_text() if p.exists() else None


# ---------- notes parsing ----------

OUTLINE_RE = re.compile(
    r"^\s*[-*]\s*\[?(\d{1,2}:\d{2}(?::\d{2})?)\]?(?:\([^)]*\))?\s*[-–—:]?\s*(.+?)\s*$"
)
SKIP_RE = re.compile(r"\{skip(?::\s*([^}]*))?\}", re.I)


def parse_outline(notes_md: str | None) -> list[dict]:
    """Extract the '## Outline' list: `- [hh:mm:ss] Title {skip: reason}`."""
    if not notes_md:
        return []
    m = re.search(r"^##\s+Outline\s*$(.*?)(?=^##\s|\Z)", notes_md, re.M | re.S)
    if not m:
        return []
    items = []
    for line in m.group(1).splitlines():
        om = OUTLINE_RE.match(line)
        if not om:
            continue
        title = om.group(2)
        sk = SKIP_RE.search(title)
        items.append({
            "t": parse_ts(om.group(1)),
            "title": SKIP_RE.sub("", title).strip(" -–—"),
            "skip": bool(sk),
            "skip_reason": (sk.group(1) or "").strip() if sk else "",
        })
    items.sort(key=lambda x: x["t"])
    return items


def tldr(notes_md: str | None) -> str:
    if not notes_md:
        return ""
    m = re.search(r"^##\s+TL;?DR\s*$(.*?)(?=^##\s|\Z)", notes_md, re.M | re.S | re.I)
    return " ".join(m.group(1).split()) if m else ""


# ---------- index / README ----------

def write_course_readme(course: dict) -> None:
    lines = [
        f"# {course['title']}",
        "",
        f"- Source: {course['url']}",
        f"- Channel: {course.get('channel') or '?'}",
        f"- Profile: `{course['profile']}` · Language: `{course['language']}`",
        f"- Lessons: {len(course['lessons'])} · Total: {fmt_ts(sum(l.get('duration') or 0 for l in course['lessons']))}",
        "",
    ]
    if course.get("description"):
        lines += [course["description"].strip(), ""]
    lines += ["| # | Lesson | Duration | Transcript | Notes |", "|---|---|---|---|---|"]
    for l in course["lessons"]:
        st = lesson_status(course, l)
        rel = f"lessons/{l['dir']}"
        notes = f"[notes]({rel}/notes.md)" if st["notes"] else "—"
        tr = f"[transcript]({rel}/transcript.md)" if st["transcript"] else "—"
        lines.append(f"| {l['index']} | [{l['title']}]({yt_url(l['video_id'])}) | {fmt_ts(l.get('duration') or 0)} | {tr} | {notes} |")
    summaries = []
    for l in course["lessons"]:
        s = tldr(read_text(lesson_dir(course, l) / "notes.md"))
        if s:
            summaries.append(f"- **{l['index']}. {l['title']}** — {s}")
    if summaries:
        lines += ["", "## Lesson summaries", "", *summaries]
    (course_dir(course["slug"]) / "README.md").write_text("\n".join(lines) + "\n")


LIBRARY_CLAUDE_MD = """# Course library (managed by coursekit)

This folder holds YouTube courses as plain markdown so agents can use them as context.

- `<course>/README.md` — index of lessons, durations, links and one-line summaries. Start here.
- `<course>/course.json` — metadata (profile, language, ordered lessons with video ids).
- `<course>/lessons/<NNN>-<slug>/transcript.md` — timestamped transcript. Every paragraph starts with
  `**[hh:mm:ss](youtube-link)**` so you can cite exact moments.
- `.../notes.md` — generated notes. The `## Outline` section uses the strict format
  `- [hh:mm:ss] Section title {skip: reason}`; `{skip}` marks sections the viewer may auto-skip.
- `.../annotations.md` — later additions (Q&A, verified references, code) appended by Claude.
- `.state/now_playing.json` — what the user is watching right now (course, lesson, position).

When answering about "what I'm watching", read `.state/now_playing.json`, then the transcript around
that position. When you add something worth keeping, append it to the lesson's `annotations.md`
using a `### [hh:mm:ss] <kind> — <title>` heading. Prefer the `coursekit` MCP tools when available.
"""


def ensure_library() -> None:
    LIBRARY.mkdir(parents=True, exist_ok=True)
    f = LIBRARY / "CLAUDE.md"
    if not f.exists():
        f.write_text(LIBRARY_CLAUDE_MD)
    state_dir()


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")
