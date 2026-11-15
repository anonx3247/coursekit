"""Transcripts: YouTube subtitles when available, local Whisper otherwise."""
from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path

from yt_dlp import YoutubeDL

from . import library as lib
from .ingest import ydl_opts

WHISPER_MODEL = os.environ.get("COURSEKIT_WHISPER_MODEL", "mlx-community/whisper-large-v3-turbo")


def log(msg: str) -> None:
    print(msg, flush=True)


# ---------- subtitles ----------

def _pick_sub_key(info: dict, lang: str) -> tuple[str, bool] | None:
    """Return (key, is_auto). Prefer human subtitles, then the original-language auto captions."""
    manual = info.get("subtitles") or {}
    auto = info.get("automatic_captions") or {}
    manual = {k: v for k, v in manual.items() if k != "live_chat"}
    if lang == "auto":
        if manual:
            return next(iter(manual)), False
        orig = [k for k in auto if k.endswith("-orig")]
        return (orig[0], True) if len(orig) == 1 else None
    for k in manual:
        if k == lang or k.split("-")[0] == lang:
            return k, False
    for cand in (f"{lang}-orig", lang):
        if cand in auto:
            return cand, True
    for k in auto:
        if k.split("-")[0] == lang and k.endswith("-orig"):
            return k, True
    return None


def _parse_json3(path: Path) -> list[dict]:
    data = json.loads(path.read_text())
    segs = []
    for ev in data.get("events", []):
        if "segs" not in ev:
            continue
        text = "".join(s.get("utf8", "") for s in ev["segs"]).replace("\n", " ").strip()
        if not text:
            continue
        start = ev.get("tStartMs", 0) / 1000
        segs.append({"start": start, "end": start + ev.get("dDurationMs", 0) / 1000, "text": text})
    return segs


def fetch_subtitles(video_id: str, lang: str, workdir: Path) -> tuple[list[dict], str] | None:
    url = lib.yt_url(video_id)
    with YoutubeDL(ydl_opts(skip_download=True)) as ydl:
        info = ydl.extract_info(url, download=False)
    picked = _pick_sub_key(info, lang)
    if not picked:
        return None
    key, is_auto = picked
    opts = ydl_opts(
        skip_download=True,
        writesubtitles=not is_auto,
        writeautomaticsub=is_auto,
        subtitleslangs=[key],
        subtitlesformat="json3",
        outtmpl=str(workdir / "%(id)s.%(ext)s"),
    )
    with YoutubeDL(opts) as ydl:
        ydl.download([url])
    files = list(workdir.glob(f"{video_id}*.json3"))
    if not files:
        return None
    segs = _parse_json3(files[0])
    return (segs, f"youtube-{'auto' if is_auto else 'manual'}-subs:{key}") if segs else None


# ---------- whisper ----------

def download_audio(video_id: str, workdir: Path) -> Path:
    opts = ydl_opts(format="bestaudio/best", outtmpl=str(workdir / "%(id)s.%(ext)s"))
    with YoutubeDL(opts) as ydl:
        ydl.download([lib.yt_url(video_id)])
    files = [f for f in workdir.glob(f"{video_id}.*") if f.suffix not in (".json3", ".part")]
    if not files:
        raise RuntimeError(f"audio download failed for {video_id}")
    return files[0]


def whisper(audio: Path, lang: str, prompt: str | None) -> list[dict]:
    language = None if lang == "auto" else lang
    try:
        import mlx_whisper  # Apple Silicon
        res = mlx_whisper.transcribe(
            str(audio), path_or_hf_repo=WHISPER_MODEL, language=language,
            initial_prompt=prompt, condition_on_previous_text=False, verbose=None,
        )
        return [{"start": s["start"], "end": s["end"], "text": s["text"].strip()} for s in res["segments"]]
    except ImportError:
        from faster_whisper import WhisperModel
        model = WhisperModel(os.environ.get("COURSEKIT_FW_MODEL", "large-v3-turbo"), compute_type="auto")
        segs, _ = model.transcribe(str(audio), language=language, initial_prompt=prompt, vad_filter=True)
        return [{"start": s.start, "end": s.end, "text": s.text.strip()} for s in segs]


# ---------- output ----------

def paragraphs(segs: list[dict], min_len: float = 20, max_len: float = 45) -> list[dict]:
    out, cur = [], None
    for s in segs:
        if cur is None:
            cur = {"start": s["start"], "end": s["end"], "text": s["text"]}
        else:
            cur["text"] += " " + s["text"]
            cur["end"] = s["end"]
        dur = cur["end"] - cur["start"]
        if dur >= max_len or (dur >= min_len and re.search(r"[.?!…»\"]$", cur["text"])):
            out.append(cur)
            cur = None
    if cur:
        out.append(cur)
    for p in out:
        p["text"] = re.sub(r"\s+", " ", p["text"]).strip()
    return out


def write_transcript(course: dict, lesson: dict, segs: list[dict], source: str) -> Path:
    d = lib.lesson_dir(course, lesson)
    d.mkdir(parents=True, exist_ok=True)
    paras = paragraphs(segs)
    (d / "transcript.json").write_text(json.dumps(
        {"video_id": lesson["video_id"], "source": source, "language": course["language"],
         "segments": segs, "paragraphs": paras}, ensure_ascii=False))
    vid = lesson["video_id"]
    lines = [
        "---",
        f"course: {course['slug']}",
        f"lesson: {lesson['index']}",
        f"title: {json.dumps(lesson['title'], ensure_ascii=False)}",
        f"video: {lib.yt_url(vid)}",
        f"duration: {lib.fmt_ts(lesson.get('duration') or (segs[-1]['end'] if segs else 0))}",
        f"source: {source}",
        "---",
        "",
        f"# Transcript — {lesson['title']}",
        "",
    ]
    for p in paras:
        lines.append(f"**[{lib.fmt_ts(p['start'])}]({lib.yt_url(vid, p['start'])})** {p['text']}")
        lines.append("")
    path = d / "transcript.md"
    path.write_text("\n".join(lines))
    return path


def transcribe_lesson(course: dict, lesson: dict, force_whisper: bool = False, overwrite: bool = False) -> str:
    d = lib.lesson_dir(course, lesson)
    if (d / "transcript.md").exists() and not overwrite:
        return "exists"
    lang = course.get("language", "en")
    with tempfile.TemporaryDirectory(prefix="coursekit-") as tmp:
        tmpd = Path(tmp)
        got = None
        if not force_whisper and not course.get("force_whisper"):
            try:
                got = fetch_subtitles(lesson["video_id"], lang, tmpd)
            except Exception as e:  # noqa: BLE001
                log(f"  subtitles failed ({e}); falling back to whisper")
        if got:
            segs, source = got
        else:
            log(f"  [{lesson['index']}] downloading audio…")
            audio = download_audio(lesson["video_id"], tmpd)
            log(f"  [{lesson['index']}] whisper ({WHISPER_MODEL})…")
            segs = whisper(audio, lang, course.get("whisper_prompt"))
            source = f"whisper:{WHISPER_MODEL.split('/')[-1]}"
    write_transcript(course, lesson, segs, source)
    return source
