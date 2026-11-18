"""`ck` command line."""
from __future__ import annotations

import argparse
import json
import sys
import traceback
import webbrowser
from concurrent.futures import ThreadPoolExecutor

from . import library as lib


def _select(course: dict, refs: list[str]) -> list[dict]:
    if not refs:
        return course["lessons"]
    out = []
    for r in refs:
        for part in r.split(","):
            if "-" in part and all(x.isdigit() for x in part.split("-", 1)):
                a, b = map(int, part.split("-", 1))
                out += [l for l in course["lessons"] if a <= l["index"] <= b]
            else:
                out.append(lib.find_lesson(course, part))
    return out


def cmd_add(a):
    from .ingest import add
    c = add(a.url, slug=a.slug, profile=a.profile, language=a.language, title=a.title, course=a.course,
            whisper_prompt=a.whisper_prompt)
    print(f"{c['slug']}: {c['title']} — {len(c['lessons'])} lessons ({c['_added']} new)")
    print(f"  {lib.course_dir(c['slug'])}")


def cmd_list(a):
    for c in lib.list_courses():
        st = [lib.lesson_status(c, l) for l in c["lessons"]]
        print(f"{c['slug']:<40} {len(st):>3} lessons  {sum(s['transcript'] for s in st):>3} transcribed  "
              f"{sum(s['notes'] for s in st):>3} notes  [{c['profile']}/{c['language']}]")
        if a.verbose:
            for l, s in zip(c["lessons"], st):
                flags = ("T" if s["transcript"] else "-") + ("N" if s["notes"] else "-")
                print(f"   {flags} {l['index']:>3}. {l['title']}  ({lib.fmt_ts(l.get('duration') or 0)})")


def cmd_process(a):
    from .notes import generate_notes
    from .transcribe import transcribe_lesson
    courses = [lib.load_course(a.course)] if a.course else lib.list_courses()
    for c in courses:
        lessons = _select(c, a.lessons)
        print(f"== {c['title']} ({len(lessons)} lessons)", flush=True)
        pool = ThreadPoolExecutor(max_workers=a.jobs)
        futs = []

        def notes_job(c=c, l=None):
            try:
                r = generate_notes(c, l, overwrite=a.force_notes, model=a.model,
                                   research=False if a.no_research else None)
                print(f"  [{l['index']}] notes: {r}", flush=True)
            except Exception as e:  # noqa: BLE001
                print(f"  [{l['index']}] notes FAILED: {e}", flush=True)

        for l in lessons:
            if not a.notes_only:
                try:
                    r = transcribe_lesson(c, l, force_whisper=a.whisper, overwrite=a.force_transcript)
                    print(f"  [{l['index']}] transcript: {r}  — {l['title']}", flush=True)
                except Exception as e:  # noqa: BLE001
                    print(f"  [{l['index']}] transcript FAILED: {e}", flush=True)
                    if a.debug:
                        traceback.print_exc()
                    continue
            if not a.transcripts_only and (lib.lesson_dir(c, l) / "transcript.md").exists():
                futs.append(pool.submit(notes_job, c, l))
        for f in futs:
            f.result()
        pool.shutdown()
        lib.write_course_readme(c)


def cmd_set(a):
    c = lib.load_course(a.course)
    try:
        val = json.loads(a.value)
    except json.JSONDecodeError:
        val = a.value
    c[a.key] = val
    lib.save_course(c)
    lib.write_course_readme(c)
    print(f"{c['slug']}.{a.key} = {val!r}")


def cmd_serve(a):
    from .server import serve
    print(f"coursekit player on http://localhost:{a.port}  (library: {lib.LIBRARY})")
    serve(a.port)


def cmd_open(a):
    from .mcp_server import ensure_server
    url = ensure_server()
    if a.course:
        c = lib.load_course(a.course)
        l = lib.find_lesson(c, a.lesson or "1")
        url += f"/#/{c['slug']}/{l['index']}"
    print(url)
    webbrowser.open(url)


def cmd_anki(a):
    from pathlib import Path
    from .anki import build
    out, n = build(a.course, Path(a.out) if a.out else None, a.deck)
    print(f"{n} cards → {out}")


def cmd_mcp(_):
    from .mcp_server import run
    run()


def cmd_profiles(_):
    from .notes import available_profiles, load_profile
    for p in available_profiles():
        print(f"{p:<12} {load_profile(p)[0].get('description', '')}")


def main(argv: list[str] | None = None):
    p = argparse.ArgumentParser(prog="ck", description="YouTube course companion")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("add", help="add a playlist or video as a course")
    s.add_argument("url")
    s.add_argument("--profile", default="default", help="notes profile: default | islamic | ml | stem | custom")
    s.add_argument("--language", default="en", help="spoken language code (en, fr, ar...) or 'auto'")
    s.add_argument("--slug")
    s.add_argument("--title")
    s.add_argument("--course", help="append the video(s) to this existing course")
    s.add_argument("--whisper-prompt", help="vocabulary hint for Whisper (names, jargon)")
    s.set_defaults(fn=cmd_add)

    s = sub.add_parser("list", help="list courses")
    s.add_argument("-v", "--verbose", action="store_true")
    s.set_defaults(fn=cmd_list)

    s = sub.add_parser("process", help="transcribe + write notes (skips what already exists)")
    s.add_argument("course", nargs="?")
    s.add_argument("lessons", nargs="*", help="lesson numbers / ranges (1-5,8) / ids; default all")
    s.add_argument("--transcripts-only", action="store_true")
    s.add_argument("--notes-only", action="store_true")
    s.add_argument("--whisper", action="store_true", help="ignore YouTube subtitles, always use Whisper")
    s.add_argument("--force-transcript", action="store_true")
    s.add_argument("--force-notes", action="store_true")
    s.add_argument("--no-research", action="store_true", help="don't let Claude use web search for notes")
    s.add_argument("--model", help="Claude model for notes (default: your Claude Code default)")
    s.add_argument("-j", "--jobs", type=int, default=3, help="parallel note generations")
    s.add_argument("--debug", action="store_true")
    s.set_defaults(fn=cmd_process)

    s = sub.add_parser("set", help="set a course field (profile, language, notes_language, notes_instructions, whisper_prompt, force_whisper)")
    s.add_argument("course")
    s.add_argument("key")
    s.add_argument("value")
    s.set_defaults(fn=cmd_set)

    s = sub.add_parser("serve", help="run the web player")
    s.add_argument("--port", type=int, default=lib.PORT)
    s.set_defaults(fn=cmd_serve)

    s = sub.add_parser("open", help="open the player in the browser (starting it if needed)")
    s.add_argument("course", nargs="?")
    s.add_argument("lesson", nargs="?")
    s.set_defaults(fn=cmd_open)

    s = sub.add_parser("anki", help="build an Anki .apkg from <course>/anki/cards.json")
    s.add_argument("course")
    s.add_argument("--out")
    s.add_argument("--deck", help="root deck name (default: course title)")
    s.set_defaults(fn=cmd_anki)

    sub.add_parser("mcp", help="run the MCP server (stdio)").set_defaults(fn=cmd_mcp)
    sub.add_parser("profiles", help="list note profiles").set_defaults(fn=cmd_profiles)

    a = p.parse_args(argv)
    try:
        a.fn(a)
    except KeyError as e:
        sys.exit(str(e).strip("'\""))


if __name__ == "__main__":
    main()
