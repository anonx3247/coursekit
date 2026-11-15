"""Generate lesson notes by piping the transcript through headless Claude Code (`claude -p`).

No API key needed: it uses your Claude Code login. Course "profiles" (src/coursekit/profiles/*.md,
or <library>/profiles/*.md to override) add domain-specific instructions and allowed tools.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

from . import library as lib

PROFILE_DIRS = [lib.LIBRARY / "profiles", Path(__file__).parent / "profiles"]

BASE_PROMPT = """You are writing study notes for one video lesson of a course, from its timestamped transcript.
The notes are stored as markdown and used by (1) a video player that parses the Outline to let the
viewer jump around and auto-skip sections, and (2) AI agents that answer questions about the course.

Write the notes in {notes_language}. Quote the speaker in the original language where wording matters.

Output ONLY the markdown document, starting with the H1 line. Use exactly this structure:

# {title}

> Course: {course_title} · Lesson {index} · [Watch]({url}) · Duration {duration}

## TL;DR
2–4 sentences: what this lesson covers and the main takeaways.

## Outline
One line per section, chronological, 5–25 sections, STRICT format (the player parses it):
- [hh:mm:ss] Section title
Append ` {{skip: reason}}` to sections a focused learner can safely skip: logistics, housekeeping,
long digressions unrelated to the topic, Q&A that repeats content, breaks, dead air, sound checks,
recap of the previous lesson. Be conservative; never mark core content as skip.

## Notes
Detailed notes per section, with `### [hh:mm:ss] Section title` headings matching the outline.
Capture definitions, arguments, examples, formulas, lists, and anything the speaker emphasises.

## Key terms
- **term** — short definition

{profile_sections}

## Review questions
3–8 questions to test understanding, with short answers in a collapsed <details> block.

Timestamps must come from the transcript. Do not invent content that is not in the lesson; when you
add outside knowledge, label it clearly (e.g. "(context)").
"""


def load_profile(name: str) -> tuple[dict, str]:
    for d in PROFILE_DIRS:
        f = d / f"{name}.md"
        if f.exists():
            text = f.read_text()
            meta: dict = {}
            m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
            if m:
                for line in m.group(1).splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        meta[k.strip()] = v.strip()
                text = text[m.end():]
            return meta, text.strip()
    raise KeyError(f"Unknown profile '{name}'. Available: {', '.join(available_profiles())}")


def available_profiles() -> list[str]:
    names = set()
    for d in PROFILE_DIRS:
        if d.exists():
            names |= {f.stem for f in d.glob("*.md")}
    return sorted(names)


def build_prompt(course: dict, lesson: dict, transcript: str) -> tuple[str, dict]:
    meta, body = load_profile(course.get("profile", "default"))
    prompt = BASE_PROMPT.format(
        notes_language=course.get("notes_language") or meta.get("notes_language") or "the language of the lesson",
        title=lesson["title"], course_title=course["title"], index=lesson["index"],
        url=lib.yt_url(lesson["video_id"]), duration=lib.fmt_ts(lesson.get("duration") or 0),
        profile_sections=body,
    )
    if course.get("notes_instructions"):
        prompt += "\nAdditional instructions for this course:\n" + course["notes_instructions"] + "\n"
    prompt += "\n<transcript>\n" + transcript + "\n</transcript>\n"
    return prompt, meta


def generate_notes(course: dict, lesson: dict, overwrite: bool = False, model: str | None = None,
                   research: bool | None = None) -> str:
    d = lib.lesson_dir(course, lesson)
    out = d / "notes.md"
    if out.exists() and not overwrite:
        return "exists"
    tr = d / "transcript.md"
    if not tr.exists():
        raise FileNotFoundError(f"No transcript yet for lesson {lesson['index']}")
    claude = shutil.which("claude") or os.path.expanduser("~/.local/bin/claude")
    prompt, meta = build_prompt(course, lesson, tr.read_text())
    cmd = [claude, "-p", "--output-format", "text"]
    tools = meta.get("tools", "")
    if research is False:
        tools = ""
    elif research and not tools:
        tools = "WebSearch,WebFetch"
    if tools:
        cmd += ["--allowedTools", tools]
    model = model or os.environ.get("COURSEKIT_NOTES_MODEL") or meta.get("model")
    if model:
        cmd += ["--model", model]
    res = subprocess.run(cmd, input=prompt, capture_output=True, text=True, cwd=str(lib.state_dir()),
                         timeout=60 * 30)
    if res.returncode != 0:
        raise RuntimeError(f"claude failed: {res.stderr.strip()[:500] or res.stdout.strip()[:500]}")
    text = res.stdout
    i = text.find("\n# ") if not text.startswith("# ") else 0
    text = text[i:].lstrip() if i >= 0 else text
    if "## Outline" not in text:
        raise RuntimeError("claude output did not contain an Outline; not saving.\n" + text[:500])
    out.write_text(text.rstrip() + "\n")
    return "ok"
