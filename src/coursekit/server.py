"""Local web player + JSON API. The page reports what you're watching; Claude (via MCP) can read it and
send commands back (seek, open lesson, change speed, refresh annotations)."""
from __future__ import annotations

import json
import subprocess
import sys
import threading
import time
from pathlib import Path

import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from . import library as lib

WEB = Path(__file__).parent / "web"
_lock = threading.Lock()
_commands: list[dict] = []
_cmd_id = 0
_jobs: dict[str, subprocess.Popen] = {}


def _read_json(p: Path, default):
    try:
        return json.loads(p.read_text())
    except Exception:  # noqa: BLE001
        return default


def progress_file() -> Path:
    return lib.state_dir() / "progress.json"


def now_playing_file() -> Path:
    return lib.state_dir() / "now_playing.json"


# ---------- routes ----------

async def index(_: Request):
    return FileResponse(WEB / "index.html")


async def api_courses(_: Request):
    prog = _read_json(progress_file(), {})
    out = []
    for c in lib.list_courses():
        lessons = []
        for l in c["lessons"]:
            p = prog.get(f"{c['slug']}/{l['index']}", {})
            lessons.append({**l, **lib.lesson_status(c, l), "position": p.get("t", 0), "watched": p.get("watched", False)})
        out.append({k: c[k] for k in ("slug", "title", "profile", "language", "url")} | {"lessons": lessons})
    return JSONResponse(out)


async def api_lesson(request: Request):
    c = lib.load_course(request.path_params["course"])
    l = lib.find_lesson(c, request.path_params["lesson"])
    d = lib.lesson_dir(c, l)
    notes = lib.read_text(d / "notes.md")
    tr = _read_json(d / "transcript.json", {})
    prog = _read_json(progress_file(), {}).get(f"{c['slug']}/{l['index']}", {})
    key = f"{c['slug']}/{l['index']}"
    job = _jobs.get(key)
    return JSONResponse({
        "course": {k: c[k] for k in ("slug", "title", "profile", "language")},
        "lesson": l,
        "notes": notes,
        "outline": lib.parse_outline(notes),
        "paragraphs": tr.get("paragraphs", []),
        "transcript_source": tr.get("source"),
        "annotations": lib.read_text(d / "annotations.md"),
        "position": prog.get("t", 0),
        "job_running": bool(job and job.poll() is None),
        "dir": str(d),
    })


async def api_state_get(_: Request):
    return JSONResponse(_read_json(now_playing_file(), {}))


async def api_state_post(request: Request):
    s = await request.json()
    s["updated"] = time.time()
    now_playing_file().write_text(json.dumps(s))
    if s.get("course") and s.get("lesson") is not None:
        with _lock:
            prog = _read_json(progress_file(), {})
            key = f"{s['course']}/{s['lesson']}"
            p = prog.get(key, {})
            p["t"] = s.get("t", 0)
            dur = s.get("duration") or 0
            p["watched"] = p.get("watched", False) or (dur > 0 and s.get("t", 0) / dur > 0.92)
            prog[key] = p
            progress_file().write_text(json.dumps(prog))
    return JSONResponse({"ok": True})


async def api_command_post(request: Request):
    global _cmd_id
    cmd = await request.json()
    with _lock:
        _cmd_id += 1
        cmd["id"] = _cmd_id
        cmd["at"] = time.time()
        _commands.append(cmd)
        del _commands[:-50]
    return JSONResponse(cmd)


async def api_commands(request: Request):
    after = int(request.query_params.get("after", 0))
    with _lock:
        # new page loads only get commands from the last 10s
        cmds = [c for c in _commands if c["id"] > after and (after or time.time() - c["at"] < 10)]
        last = _cmd_id
    return JSONResponse({"commands": cmds, "last": last})


async def api_process(request: Request):
    c = lib.load_course(request.path_params["course"])
    l = lib.find_lesson(c, request.path_params["lesson"])
    key = f"{c['slug']}/{l['index']}"
    j = _jobs.get(key)
    if j and j.poll() is None:
        return JSONResponse({"status": "running"})
    log = lib.state_dir() / "jobs"
    log.mkdir(exist_ok=True)
    f = open(log / f"{c['slug']}-{l['index']}.log", "a")  # noqa: SIM115
    _jobs[key] = subprocess.Popen([sys.executable, "-m", "coursekit.cli", "process", c["slug"], str(l["index"])],
                                  stdout=f, stderr=subprocess.STDOUT)
    return JSONResponse({"status": "started"})


async def api_health(_: Request):
    return JSONResponse({"ok": True, "library": str(lib.LIBRARY)})


def app() -> Starlette:
    return Starlette(routes=[
        Route("/", index),
        Route("/api/health", api_health),
        Route("/api/courses", api_courses),
        Route("/api/lesson/{course}/{lesson}", api_lesson),
        Route("/api/state", api_state_get, methods=["GET"]),
        Route("/api/state", api_state_post, methods=["POST"]),
        Route("/api/command", api_command_post, methods=["POST"]),
        Route("/api/commands", api_commands),
        Route("/api/process/{course}/{lesson}", api_process, methods=["POST"]),
        Mount("/static", StaticFiles(directory=WEB)),
    ])


def serve(port: int = lib.PORT) -> None:
    lib.ensure_library()
    uvicorn.run(app(), host="127.0.0.1", port=port, log_level="warning")
