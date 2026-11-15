"""Fetch playlist / video metadata with yt-dlp and register it as a course."""
from __future__ import annotations

import os

from yt_dlp import YoutubeDL

from . import library as lib


def ydl_opts(**extra) -> dict:
    opts: dict = {"quiet": True, "no_warnings": True, "noprogress": True}
    # Unlisted videos work with the plain URL. For private / members-only content,
    # set COURSEKIT_COOKIES_FROM_BROWSER=chrome (or firefox, safari, ...).
    browser = os.environ.get("COURSEKIT_COOKIES_FROM_BROWSER")
    if browser:
        opts["cookiesfrombrowser"] = (browser,)
    opts.update(extra)
    return opts


def _lesson_from_entry(index: int, e: dict) -> dict:
    title = e.get("title") or e["id"]
    return {
        "index": index,
        "video_id": e["id"],
        "title": title,
        "duration": e.get("duration"),
        "dir": f"{index:03d}-{lib.slugify(title, 50)}",
    }


def add(url: str, slug: str | None = None, profile: str = "default", language: str = "en",
        title: str | None = None, course: str | None = None, whisper_prompt: str | None = None) -> dict:
    """Add a playlist (new course) or a single video (new course, or appended to `course`)."""
    lib.ensure_library()
    with YoutubeDL(ydl_opts(extract_flat="in_playlist")) as ydl:
        info = ydl.extract_info(url, download=False)

    entries = [e for e in (info.get("entries") or [info]) if e and e.get("id")]
    entries = [e for e in entries if e.get("title") not in ("[Private video]", "[Deleted video]")]

    if course:  # append to an existing course
        c = lib.load_course(course)
    else:
        name = title or info.get("title") or entries[0].get("title")
        s = slug or lib.slugify(name, 40)
        try:
            c = lib.load_course(s) if (lib.course_dir(s) / "course.json").exists() else None
        except KeyError:
            c = None
        c = c or {
            "slug": s, "title": name, "url": url,
            "channel": info.get("channel") or info.get("uploader"),
            "description": (info.get("description") or "").strip()[:1000],
            "profile": profile, "language": language, "added": lib.now_iso(), "lessons": [],
        }
        if whisper_prompt:
            c["whisper_prompt"] = whisper_prompt

    known = {l["video_id"] for l in c["lessons"]}
    nxt = max((l["index"] for l in c["lessons"]), default=0) + 1
    added = 0
    for e in entries:
        if e["id"] in known:
            continue
        c["lessons"].append(_lesson_from_entry(nxt, e))
        nxt += 1
        added += 1
    lib.save_course(c)
    lib.write_course_readme(c)
    c["_added"] = added
    return c
