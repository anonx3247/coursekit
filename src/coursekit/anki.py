"""Build Anki decks (.apkg) from a course's cards file.

Cards live in <library>/<course>/anki/cards.json, a list of objects:
  {
    "id": "l01-written-in-lifetime",      # stable: re-importing updates the card instead of duplicating it
    "lesson": 1,                          # lesson index (sets the subdeck and the "Watch" link)
    "kind": "example",                    # example | principle | positions | case | history (becomes a tag)
    "front": "Give examples of …",
    "back": "1. …\n2. …",                 # light markdown: **bold**, *italic*, "- " and "1. " lists
    "refs": ["Ṣaḥīḥ al-Bukhārī 113 — https://sunnah.com/bukhari:113"],
    "isnad": "optional chain(s)",
    "t": "00:39:33",                      # moment in the lecture
    "tags": ["optional", "extra-tags"]
  }
Arabic-script runs are wrapped automatically for right-to-left display in a larger font.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
from pathlib import Path

import genanki

from . import library as lib

CSS = """
.card { font-family: -apple-system, "Segoe UI", Inter, sans-serif; font-size: 19px; line-height: 1.5;
  text-align: left; color: #1d1f24; background: #fbfaf7; max-width: 720px; margin: 0 auto; padding: 8px; }
.nightMode.card, .night_mode .card { color: #e6e8ee; background: #16181d; }
.front { font-size: 21px; font-weight: 600; }
.kind { font-size: 12px; text-transform: uppercase; letter-spacing: .08em; color: #8b91a3; margin-bottom: 6px; }
.ar { font-family: "Amiri", "Scheherazade New", "Noto Naskh Arabic", "Geeza Pro", serif; font-size: 1.35em;
  direction: rtl; unicode-bidi: isolate; }
ol, ul { padding-left: 1.3em; margin: 6px 0; } li { margin: 4px 0; }
.refs { margin-top: 14px; font-size: 14px; color: #555b6a; border-top: 1px solid #ddd; padding-top: 8px; }
.nightMode .refs { color: #a3a9b8; border-color: #333; }
.refs a, .watch a { color: #3d6cf0; text-decoration: none; }
.isnad { margin-top: 10px; font-size: 13px; color: #8b91a3; }
.isnad summary { cursor: pointer; }
.watch { margin-top: 10px; font-size: 14px; }
"""

FRONT = """<div class="kind">{{Kind}} · {{Lesson}}</div><div class="front">{{Front}}</div>"""
BACK = """{{FrontSide}}<hr id="answer"><div class="back">{{Back}}</div>
{{#References}}<div class="refs"><b>References</b><br>{{References}}</div>{{/References}}
{{#Isnad}}<details class="isnad"><summary>Isnād</summary>{{Isnad}}</details>{{/Isnad}}
{{#Watch}}<div class="watch">{{Watch}}</div>{{/Watch}}"""


def _id(s: str) -> int:
    return int(hashlib.sha1(s.encode()).hexdigest()[:8], 16)


MODEL = genanki.Model(
    _id("coursekit-model-v1"), "coursekit card",
    fields=[{"name": n} for n in ("Front", "Back", "References", "Isnad", "Watch", "Lesson", "Kind")],
    templates=[{"name": "Card 1", "qfmt": FRONT, "afmt": BACK}],
    css=CSS,
)

AR_RUN = re.compile(r"([؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿][؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿\s،؛؟«»\.\-…]*[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿»])|([؀-ۿﭐ-﷿ﹰ-﻿])")


def _inline(s: str) -> str:
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", s)
    s = re.sub(r"(https?://(?:www\.)?([^\s<)]+))", r'<a href="\1">\2</a>', s)
    s = AR_RUN.sub(lambda m: f'<span class="ar">{m.group(0)}</span>', s)
    return s


def md(text: str) -> str:
    """Tiny markdown: paragraphs, '- ' and '1. ' lists (one level), bold/italic, links, Arabic spans."""
    out, mode = [], None
    for raw in (text or "").splitlines():
        line = raw.rstrip()
        m_ul, m_ol = re.match(r"^\s*[-*]\s+(.*)", line), re.match(r"^\s*\d+[.)]\s+(.*)", line)
        want = "ul" if m_ul else "ol" if m_ol else None
        if want != mode:
            if mode:
                out.append(f"</{mode}>")
            if want:
                out.append(f"<{want}>")
            mode = want
        if want:
            out.append(f"<li>{_inline((m_ul or m_ol).group(1))}</li>")
        elif line.strip():
            out.append(f"<div>{_inline(line)}</div>")
    if mode:
        out.append(f"</{mode}>")
    return "".join(out)


def build(course_slug: str, out: Path | None = None, deck_name: str | None = None) -> tuple[Path, int]:
    c = lib.load_course(course_slug)
    d = lib.course_dir(c["slug"]) / "anki"
    cards = json.loads((d / "cards.json").read_text())
    root = deck_name or c.get("anki_deck") or c["title"]
    decks: dict[int, genanki.Deck] = {}
    seen = set()
    for card in cards:
        if card["id"] in seen:
            raise ValueError(f"duplicate card id {card['id']}")
        seen.add(card["id"])
        l = lib.find_lesson(c, card["lesson"])
        if l["index"] not in decks:
            name = f"{root}::{l['index']:02d} · {l['title']}"
            decks[l["index"]] = genanki.Deck(_id(f"{c['slug']}/deck/{l['index']}"), name)
        watch = ""
        if card.get("t"):
            t = lib.parse_ts(card["t"])
            watch = f'<a href="{lib.yt_url(l["video_id"], t)}">▶ Watch at {lib.fmt_ts(t)}</a>'
        refs = "<br>".join(_inline(r) for r in card.get("refs", []))
        note = genanki.Note(
            model=MODEL,
            fields=[_inline(card["front"]), md(card["back"]), refs, md(card.get("isnad", "")), watch,
                    f"Lesson {l['index']}", card.get("kind", "")],
            tags=[f"L{l['index']:02d}", card.get("kind", "card"), *card.get("tags", [])],
            guid=genanki.guid_for(c["slug"], card["id"]),
        )
        decks[l["index"]].add_note(note)
    out = out or d / f"{c['slug']}.apkg"
    genanki.Package([decks[k] for k in sorted(decks)]).write_to_file(str(out))
    return out, len(cards)
