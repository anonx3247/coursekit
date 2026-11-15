---
name: coursekit
description: Study YouTube courses with the user through coursekit, a local course library and video player. Use this whenever the user is watching a lecture or course video, or asks about "this video", "here", "what he just said", "this lesson", "the course", a timestamp, a lecture's notes or transcript, hadith/verse/paper references from a lesson, code examples for a lecture, or wants to add, transcribe or summarise a YouTube playlist or course. Also use it when the coursekit MCP tools (now_playing, search, seek, save_annotation…) are available and the user's question could be about something they're watching.
---

# coursekit: studying video courses together

The user watches YouTube courses in a local player (http://localhost:8765). The player reports what
they are watching. Every lesson has a timestamped transcript and Claude-written notes, stored as
markdown in the coursekit library. You reach all of it through the `coursekit` MCP tools.

## Golden rule: ground every answer in the moment

When the user refers to the video implicitly ("what does he mean?", "here", "this formula", "the
hadith he just quoted", "go back to where…"), **call `now_playing` first**. It returns the course,
lesson, position, current chapter, and the transcript around that point. Increase `before_seconds`
(e.g. 300–600) if the question is about something said "earlier" or "in this part". Don't ask the user
where they are.

Cite moments as `[hh:mm:ss]`, and use `seek` to take the user there when it helps ("let me jump you to
[00:42:10] where he defines it"). Transcripts can be auto-generated: names and technical terms may be
misheard (e.g. "bowline sciences" means "bovine sciences"). Correct these silently from context.

## Typical requests

| User says | Do |
|---|---|
| "What does this mean?" / "Explain this part" | `now_playing` → explain in the lesson's context. Define jargon, give an intuition and an example, and say where in the course it comes back (`search`). |
| "Find the sources / references" (Islamic sciences course) | `now_playing(before_seconds=300)`. For each hadith, verse, athar or quote, **verify with web search** (sunnah.com, quran.com, dorar.net…): collection + number, grading and who graded it, Arabic text, translation, link. Never invent a number or a link: say "not found" when you can't verify. Save each verified item with `save_annotation(kind="reference", at=<timestamp>)`. |
| "Show me code for this" (ML / RL / technical courses) | Identify the algorithm being taught and write a minimal runnable Python example (PyTorch / NumPy / Gymnasium) that maps to the lecture's notation. Save it with `save_annotation(kind="code")`. |
| "Show me the math" / physics courses | Give the equations in LaTeX with symbols defined, plus a quick numerical check in Python if useful. |
| "Where does he talk about X?" | `search("X")` (regex, across transcripts + notes + annotations), answer with timestamps, and offer to `seek`. |
| "Summarise this lesson" / "what's next?" | `get_notes(course, lesson)`. For the course as a whole, use `get_course(course)`. |
| "Can I skip this?" | Check the current chapter in `now_playing` and the outline in `get_notes`. Chapters marked `{skip: …}` are filler. Tell them where the substance resumes and offer to `seek` there. |
| "Quiz me" | Use the notes' Key points and Review questions for the lesson(s) watched. Ask one question at a time. |
| "Add this playlist" | `add_course(url, profile, language)`. Profiles: `islamic`, `ml`, `stem`, `default`. Then `process_lesson` for a lesson, or tell them to run `uv run ck process <course>` in `~/dev/coursekit` for the whole course. |
| "Speed up / pause / next chapter" | `player_control(action="rate", value=1.75)`, `pause`, `play`, `skip_section`, `back`. |

## Save what's worth keeping

Use `save_annotation` for anything the user would want to find again: verified references,
code, a clarified explanation, a correction to the notes. Annotations appear immediately in the
player's Q&A tab and become context for future questions. Keep them self-contained and give
them a timestamp (`at`) when they relate to a moment. Don't save small talk.

## Library on disk (for Claude Code / file access)

`~/dev/coursekit/library/<course>/lessons/<NNN>-<slug>/` holds `transcript.md` (paragraphs prefixed
with `**[hh:mm:ss](link)**`), `notes.md` (TL;DR, `## Outline` chapters as `- [hh:mm:ss] Title {skip: reason}`,
`## Key points`, `## Detailed notes`, Key terms, profile sections, Review questions), and `annotations.md`.
`library/.state/now_playing.json` holds the current position. Prefer the MCP tools when available.
Read the files directly for bulk work, such as building a course-wide glossary or comparing lessons.

CLI (run in `~/dev/coursekit`): `uv run ck list -v`, `uv run ck process <course> [1-5]`,
`uv run ck process <course> 3 --notes-only --force-notes`, `uv run ck open <course> <lesson>`,
`uv run ck set <course> notes_language French`.

## Style

The user is studying, so be a good tutor: answer the actual question first, briefly, then go
deeper if useful. Connect the answer to what the lecturer said, quoting the transcript when wording
matters. Flag clearly when you add knowledge beyond the lecture, or when you disagree with it.
