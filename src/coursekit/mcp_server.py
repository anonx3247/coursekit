"""MCP server: lets Claude (desktop app or Claude Code) see what you're watching, read transcripts and
notes, search the library, control the player, and save Q&A / references / code next to the lesson."""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time

import logging

import httpx
from mcp.server.mcpserver import MCPServer

from . import library as lib

logging.getLogger("httpx").setLevel(logging.WARNING)

mcp = MCPServer(
    "coursekit",
    instructions=(
        "Course companion for YouTube lectures stored locally as markdown. When the user asks about "
        "'this', 'here', 'what he just said', etc., call now_playing first: it returns the lesson, the "
        "current position and the transcript around it. Cite moments as [hh:mm:ss]. Save useful answers, "
        "verified references (hadith numbers, verses, papers) and code with save_annotation so they show up "
        "in the player. Use seek to show the user a specific moment."
    ),
)

BASE = f"http://127.0.0.1:{lib.PORT}"


def _server_up() -> bool:
    try:
        return httpx.get(f"{BASE}/api/health", timeout=0.5).status_code == 200
    except httpx.HTTPError:
        return False


def ensure_server() -> str:
    """Start the web player in the background if it isn't running."""
    if not _server_up():
        log = open(lib.state_dir() / "server.log", "a")  # noqa: SIM115
        subprocess.Popen([sys.executable, "-m", "coursekit.cli", "serve"], stdout=log, stderr=log,
                         stdin=subprocess.DEVNULL, start_new_session=True)
        for _ in range(40):
            time.sleep(0.25)
            if _server_up():
                break
    return f"http://localhost:{lib.PORT}"


def _send(cmd: dict) -> str:
    url = ensure_server()
    httpx.post(f"{BASE}/api/command", json=cmd, timeout=3)
    return url


def _window(course: dict, lesson: dict, start: float, end: float) -> str:
    p = lib.lesson_dir(course, lesson) / "transcript.json"
    if not p.exists():
        return "(no transcript yet — run `ck process` or use process_lesson)"
    segs = [s for s in json.loads(p.read_text())["segments"] if s["end"] >= start and s["start"] <= end]
    lines, cur = [], None  # merge tiny caption fragments into ~10s lines
    for s in segs:
        if cur and s["start"] - cur[0] < 10:
            cur[1] += " " + s["text"]
        else:
            if cur:
                lines.append(cur)
            cur = [s["start"], s["text"]]
    if cur:
        lines.append(cur)
    return "\n".join(f"[{lib.fmt_ts(t)}] {txt}" for t, txt in lines) or "(no speech in this range)"


def _section_at(course: dict, lesson: dict, t: float) -> str:
    outline = lib.parse_outline(lib.read_text(lib.lesson_dir(course, lesson) / "notes.md"))
    cur = None
    for item in outline:
        if item["t"] <= t:
            cur = item
    return f"[{lib.fmt_ts(cur['t'])}] {cur['title']}" if cur else "(unknown)"


@mcp.tool()
def now_playing(before_seconds: int = 180, after_seconds: int = 30) -> str:
    """What the user is watching right now: course, lesson, position, current outline section, and the
    transcript from `before_seconds` before to `after_seconds` after the current position."""
    p = lib.state_dir() / "now_playing.json"
    if not p.exists():
        return "Nothing is playing. Open the player with open_player."
    s = json.loads(p.read_text())
    c = lib.load_course(s["course"])
    l = lib.find_lesson(c, s["lesson"])
    t = float(s.get("t", 0))
    age = time.time() - s.get("updated", 0)
    d = lib.lesson_dir(c, l)
    return "\n".join([
        f"Course: {c['title']} (slug: {c['slug']}, profile: {c['profile']})",
        f"Lesson {l['index']}: {l['title']}",
        f"Position: {lib.fmt_ts(t)} / {lib.fmt_ts(l.get('duration') or 0)} · "
        f"{'playing' if s.get('playing') else 'paused'} at {s.get('rate', 1)}x · state updated {int(age)}s ago",
        f"Current section: {_section_at(c, l, t)}",
        f"Video at this moment: {lib.yt_url(l['video_id'], t)}",
        f"Files: {d}/notes.md, {d}/transcript.md, {d}/annotations.md",
        "",
        f"Transcript {lib.fmt_ts(max(0, t - before_seconds))}–{lib.fmt_ts(t + after_seconds)}:",
        _window(c, l, max(0, t - before_seconds), t + after_seconds),
    ])


@mcp.tool()
def list_courses() -> str:
    """List courses in the library with lesson counts and processing status."""
    out = []
    for c in lib.list_courses():
        st = [lib.lesson_status(c, l) for l in c["lessons"]]
        out.append(f"- {c['slug']}: {c['title']} — {len(st)} lessons, {sum(s['transcript'] for s in st)} transcribed, "
                   f"{sum(s['notes'] for s in st)} with notes (profile {c['profile']}, lang {c['language']})")
    return "\n".join(out) or "Library is empty. Use add_course."


@mcp.tool()
def get_course(course: str) -> str:
    """Course index (README): lessons, durations, links, and one-line summaries."""
    c = lib.load_course(course)
    lib.write_course_readme(c)
    return (lib.course_dir(c["slug"]) / "README.md").read_text()


@mcp.tool()
def get_notes(course: str, lesson: str) -> str:
    """Generated notes for a lesson (lesson = number, video id, or title fragment), plus annotations."""
    c = lib.load_course(course)
    l = lib.find_lesson(c, lesson)
    d = lib.lesson_dir(c, l)
    notes = lib.read_text(d / "notes.md") or "(no notes yet)"
    ann = lib.read_text(d / "annotations.md")
    return notes + (f"\n\n---\n# Annotations\n\n{ann}" if ann else "")


@mcp.tool()
def get_transcript(course: str, lesson: str, start: str = "0", end: str = "") -> str:
    """Transcript of a lesson, optionally limited to [start, end] (seconds or hh:mm:ss)."""
    c = lib.load_course(course)
    l = lib.find_lesson(c, lesson)
    return _window(c, l, lib.parse_ts(start), lib.parse_ts(end) if end else 10**9)


@mcp.tool()
def search(query: str, course: str = "", max_results: int = 30) -> str:
    """Case-insensitive regex/keyword search across transcripts, notes and annotations.
    Returns matches with lesson, timestamp and a link."""
    rx = re.compile(query, re.I)
    courses = [lib.load_course(course)] if course else lib.list_courses()
    hits = []
    for c in courses:
        for l in c["lessons"]:
            d = lib.lesson_dir(c, l)
            for fname in ("notes.md", "annotations.md"):
                for line in (lib.read_text(d / fname) or "").splitlines():
                    if rx.search(line):
                        hits.append(f"{c['slug']} #{l['index']} {fname}: {line.strip()[:240]}")
            tj = d / "transcript.json"
            if tj.exists():
                for p in json.loads(tj.read_text())["paragraphs"]:
                    if rx.search(p["text"]):
                        m = rx.search(p["text"])
                        a = max(0, m.start() - 120)
                        hits.append(f"{c['slug']} #{l['index']} [{lib.fmt_ts(p['start'])}] …{p['text'][a:a + 260]}… "
                                    f"{lib.yt_url(l['video_id'], p['start'])}")
            if len(hits) >= max_results:
                return "\n".join(hits[:max_results]) + "\n(truncated)"
    return "\n".join(hits) or "No matches."


@mcp.tool()
def seek(t: str, course: str = "", lesson: str = "") -> str:
    """Move the player to a time (seconds or hh:mm:ss). If course+lesson are given, open that lesson first."""
    cmd: dict = {"action": "seek", "t": lib.parse_ts(t)}
    if course and lesson:
        c = lib.load_course(course)
        l = lib.find_lesson(c, lesson)
        cmd = {"action": "open", "course": c["slug"], "lesson": l["index"], "t": cmd["t"]}
    url = _send(cmd)
    return f"Sent {cmd} to the player at {url}"


@mcp.tool()
def player_control(action: str, value: float = 0) -> str:
    """Control the player: action = play | pause | rate (value = 0.25..2) | skip_section | back (value = seconds)."""
    url = _send({"action": action, "value": value})
    return f"Sent {action} to {url}"


@mcp.tool()
def open_player(course: str = "", lesson: str = "") -> str:
    """Start the local web player (if needed) and return its URL; optionally open a lesson."""
    url = ensure_server()
    if course and lesson:
        c = lib.load_course(course)
        l = lib.find_lesson(c, lesson)
        return f"{url}/#/{c['slug']}/{l['index']}"
    return url


@mcp.tool()
def save_annotation(course: str, lesson: str, kind: str, title: str, body: str, at: str = "") -> str:
    """Append to the lesson's annotations.md (shown in the player's Q&A tab and used as future context).
    kind: question | reference | code | note | correction. `at` = timestamp it relates to (optional).
    For references, include the exact source (e.g. 'Sahih Muslim 1907', 'Quran 2:255') and a link."""
    c = lib.load_course(course)
    l = lib.find_lesson(c, lesson)
    d = lib.lesson_dir(c, l)
    d.mkdir(parents=True, exist_ok=True)
    f = d / "annotations.md"
    head = f"### [{lib.fmt_ts(lib.parse_ts(at))}] " if at else "### "
    entry = f"{head}{kind} — {title}\n\n_{lib.now_iso()}_\n\n{body.strip()}\n\n"
    if not f.exists():
        entry = f"# Annotations — {l['title']}\n\n" + entry
    with f.open("a") as fh:
        fh.write(entry)
    if _server_up():
        httpx.post(f"{BASE}/api/command", json={"action": "refresh"}, timeout=3)
    return f"Saved to {f}"


@mcp.tool()
def add_course(url: str, profile: str = "default", language: str = "en", slug: str = "", title: str = "") -> str:
    """Register a YouTube playlist (or single video) as a course. Fetches metadata only.
    profile: default | islamic | ml | stem (or a custom one). language: spoken language code, or 'auto'."""
    from .ingest import add
    c = add(url, slug=slug or None, profile=profile, language=language, title=title or None)
    return f"Course '{c['slug']}' has {len(c['lessons'])} lessons ({c['_added']} new). " \
           f"Run `ck process {c['slug']}` in a terminal (or process_lesson) to transcribe and write notes."


@mcp.tool()
def process_lesson(course: str, lesson: str) -> str:
    """Transcribe + generate notes for one lesson in the background (takes a few minutes)."""
    ensure_server()
    c = lib.load_course(course)
    l = lib.find_lesson(c, lesson)
    r = httpx.post(f"{BASE}/api/process/{c['slug']}/{l['index']}", timeout=5).json()
    return f"Processing {c['slug']} #{l['index']}: {r['status']}. Log: {lib.state_dir()}/jobs/{c['slug']}-{l['index']}.log"


@mcp.prompt()
def explain_here() -> str:
    """Explain what is being said at the current moment of the video."""
    return ("Call now_playing, then explain what the lecturer is saying at this moment, in context of the "
            "lesson. Define jargon, give an example, and point to timestamps for related parts.")


@mcp.prompt()
def find_references() -> str:
    """Find and verify sources for texts cited around the current moment (hadith, verses, papers)."""
    return ("Call now_playing (before_seconds=300). Identify every hadith, verse, quote or paper cited in that "
            "window. Search the web to find and verify its exact source (collection + number + grading for "
            "hadith; surah:ayah for verses; authors/year for papers) with links. Save each verified one with "
            "save_annotation(kind='reference'). Say clearly when you could not verify something.")


@mcp.prompt()
def code_example() -> str:
    """Write a runnable code example for the concept being taught right now."""
    return ("Call now_playing, identify the algorithm/concept being taught, and write a minimal runnable Python "
            "example for it. Explain how it maps to the lecture, then save it with save_annotation(kind='code').")


def run() -> None:
    lib.ensure_library()
    mcp.run()
