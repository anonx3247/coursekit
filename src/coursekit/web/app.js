// coursekit player
const $ = (s) => document.querySelector(s);
const RATES = [1, 1.25, 1.5, 1.75, 2];
const S = { courses: [], cur: null, player: null, ready: false, lastCmd: 0, autoskip: localStorage.autoskip === "1",
  rate: parseFloat(localStorage.rate || "1"), pendingSeek: null, lastSkipFrom: -1 };

const fmt = (s) => { s = Math.max(0, Math.floor(s || 0)); const h = Math.floor(s / 3600), m = Math.floor(s % 3600 / 60), x = s % 60;
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(x).padStart(2, "0")}`; };
const parseTs = (t) => t.split(":").reduce((a, b) => a * 60 + parseFloat(b), 0);
const esc = (s) => (s || "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const api = (p, opts) => fetch(p, opts).then((r) => r.json());
function toast(msg) { const t = $("#toast"); t.textContent = msg; t.hidden = false; clearTimeout(t._h); t._h = setTimeout(() => (t.hidden = true), 2200); }

// ---------- markdown (with math + clickable timestamps) ----------
function renderMd(md) {
  if (!md) return "";
  const math = [];
  md = md.replace(/\$\$([\s\S]+?)\$\$/g, (_, m) => `@@MATH${math.push([m, true]) - 1}@@`)
         .replace(/(^|[^\\$\w])\$([^\s$](?:[^$\n]*?[^\s$])?)\$(?!\w)/g, (_, pre, m) => `${pre}@@MATH${math.push([m, false]) - 1}@@`);
  md = md.replace(/\{skip(?::\s*([^}]*))?\}/gi, (_, r) => `<span class="skiptag">skip${r ? ": " + esc(r) : ""}</span>`);
  // bare [hh:mm:ss] → seek link (leave markdown links alone; YouTube links are intercepted below)
  md = md.replace(/\[(\d{1,2}:\d{2}(?::\d{2})?)\](?!\()/g, (_, ts) => `<a class="ts" data-t="${parseTs(ts)}">${ts}</a>`);
  let html = marked.parse(md);
  html = html.replace(/@@MATH(\d+)@@/g, (_, i) => {
    const [m, block] = math[+i];
    try { return katex.renderToString(m, { displayMode: block, throwOnError: false }); } catch { return esc(m); }
  });
  return html;
}

function wireLinks(root) {
  root.querySelectorAll("a").forEach((a) => {
    if (a.classList.contains("ts")) return;
    const href = a.getAttribute("href") || "";
    const m = href.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([\w-]{11}).*?[?&]t=(\d+)/);
    if (m && S.cur && m[1] === S.cur.lesson.video_id) { a.classList.add("ts"); a.dataset.t = m[2]; a.removeAttribute("href"); }
    else a.target = "_blank";
  });
}
document.addEventListener("click", (e) => {
  const a = e.target.closest("a.ts");
  if (a) { e.preventDefault(); seekTo(parseFloat(a.dataset.t)); }
});

// ---------- sidebar ----------
async function loadCourses() {
  S.courses = await api("/api/courses");
  renderSidebar();
}
function renderSidebar() {
  const q = $("#filter").value.toLowerCase();
  const open = new Set([...document.querySelectorAll("details.course[open]")].map((d) => d.dataset.slug));
  $("#courses").innerHTML = S.courses.map((c) => {
    const ls = c.lessons.filter((l) => !q || l.title.toLowerCase().includes(q));
    const isOpen = open.has(c.slug) || (S.cur && S.cur.course.slug === c.slug) || q;
    const nNotes = c.lessons.filter((l) => l.notes).length;
    return `<details class="course" data-slug="${c.slug}" ${isOpen ? "open" : ""}>
      <summary>${esc(c.title)} <span class="muted stats">${nNotes}/${c.lessons.length}</span></summary>
      ${ls.map((l) => {
        const pct = l.duration ? Math.min(100, (l.position / l.duration) * 100) : 0;
        const cur = S.cur && S.cur.course.slug === c.slug && S.cur.lesson.index === l.index;
        return `<a class="lesson ${cur ? "current" : ""} ${l.watched ? "watched" : ""}" href="#/${c.slug}/${l.index}">
          <span class="idx">${l.index}</span><span class="t">${esc(l.title)}</span>
          <span class="dots" title="transcript · notes · Q&A">${l.transcript ? "T" : "·"}${l.notes ? "N" : "·"}${l.annotations ? "Q" : ""}</span></a>
          ${pct > 1 ? `<div class="bar"><i style="width:${pct}%"></i></div>` : ""}`;
      }).join("")}</details>`;
  }).join("") || `<p class="muted">No courses yet.</p>`;
}
$("#filter").addEventListener("input", renderSidebar);

// ---------- lesson ----------
async function openLesson(slug, idx, t) {
  const data = await api(`/api/lesson/${slug}/${idx}`);
  const sameVideo = S.cur && S.cur.lesson.video_id === data.lesson.video_id;
  S.cur = data;
  S.lastSkipFrom = -1;
  $("#empty").hidden = true; $("#stage").hidden = false;
  $("#course-title").textContent = data.course.title;
  $("#lesson-title").textContent = `${data.lesson.index}. ${data.lesson.title}`;
  document.title = `${data.lesson.title} — coursekit`;
  renderPanel();
  renderTimeline();
  renderProcessBar();
  renderSidebar();
  const dur = data.lesson.duration || 0;
  const start = t ?? (data.position > 10 && (!dur || data.position < dur - 30) ? data.position : 0);
  if (sameVideo && S.ready) { if (t != null) seekTo(t); return; }
  loadVideo(data.lesson.video_id, start);
}

// Split notes.md: the Outline goes to the chapter bar, "Detailed notes" to its own tab, the rest is the short notes.
function splitNotes(md) {
  const parts = md.split(/^(?=## )/m);
  const short = [], detailed = [];
  for (const p of parts) {
    const h = (p.match(/^## (.*)/) || [])[1]?.trim().toLowerCase();
    if (h === "outline") continue;
    (h === "detailed notes" || h === "notes" ? detailed : short).push(p);
  }
  return { short: short.join(""), detailed: detailed.join("").replace(/^## .*\n/, "") };
}

function renderPanel() {
  const d = S.cur;
  const notes = $("#tab-notes"), det = $("#tab-detailed");
  const none = `<p class="muted">No notes yet${d.paragraphs.length ? " (transcript available)" : ""}.</p>`;
  const sp = d.notes ? splitNotes(d.notes) : null;
  notes.innerHTML = sp ? renderMd(sp.short) : none;
  det.innerHTML = sp && sp.detailed.trim() ? renderMd(sp.detailed) : none;
  wireLinks(notes); wireLinks(det);
  $("#transcript").innerHTML = d.paragraphs.length
    ? `<p class="muted">Source: ${esc(d.transcript_source)}</p>` + d.paragraphs.map((p, i) =>
      `<div class="para" data-i="${i}" data-t="${p.start}"><a class="ts" data-t="${p.start}">${fmt(p.start)}</a>${esc(p.text)}</div>`).join("")
    : `<p class="muted">No transcript yet.</p>`;
  const qa = $("#tab-qa");
  qa.innerHTML = d.annotations ? renderMd(d.annotations)
    : `<p class="muted">Nothing yet. Ask Claude about the video (it can see where you are through the coursekit MCP server);
       useful answers, verified references and code it saves with <code>save_annotation</code> appear here.</p>`;
  wireLinks(qa);
  const n = (d.annotations || "").match(/^### /gm);
  $("#qa-count").textContent = n ? `(${n.length})` : "";
}
$("#transcript").addEventListener("click", (e) => {
  const p = e.target.closest(".para"); if (p && !e.target.closest("a")) seekTo(parseFloat(p.dataset.t));
});

function renderTimeline() {
  const tl = $("#timeline");
  tl.querySelectorAll(".seg").forEach((s) => s.remove());
  const dur = S.cur.lesson.duration || 0;
  const o = S.cur.outline;
  if (!dur) return;
  o.forEach((it, i) => {
    const end = i + 1 < o.length ? o[i + 1].t : dur;
    const seg = document.createElement("div");
    seg.className = "seg" + (it.skip ? " skip" : "");
    seg.style.left = `${(it.t / dur) * 100}%`;
    seg.style.width = `${((end - it.t) / dur) * 100}%`;
    seg.onclick = (e) => { e.stopPropagation(); seekTo(it.t); };
    tl.appendChild(seg);
  });
  renderChapters();
}

function renderChapters() {
  const o = S.cur.outline, dur = S.cur.lesson.duration || 0;
  $("#chapters").innerHTML = o.length ? `<div class="ch-head muted">Chapters</div>` + o.map((it, i) => {
    const end = i + 1 < o.length ? o[i + 1].t : dur;
    return `<button class="chapter ${it.skip ? "skip" : ""}" data-i="${i}" data-t="${it.t}">
      <span class="ch-t">${fmt(it.t)}</span><span class="ch-title">${esc(it.title)}</span>
      ${it.skip ? `<span class="skiptag" title="${esc(it.skip_reason)}">skip</span>` : ""}
      <span class="ch-len muted">${Math.max(1, Math.round((end - it.t) / 60))} min</span></button>`;
  }).join("") : "";
}
$("#chapters").addEventListener("click", (e) => { const b = e.target.closest(".chapter"); if (b) seekTo(parseFloat(b.dataset.t)); });

// instant, large hover tooltip on the timeline
$("#timeline").addEventListener("mousemove", (e) => {
  if (!S.cur) return;
  const r = e.currentTarget.getBoundingClientRect(), x = e.clientX - r.left;
  const t = (x / r.width) * (S.cur.lesson.duration || 0), i = sectionIndex(t), o = S.cur.outline;
  const tip = $("#tip");
  tip.innerHTML = `<b>${fmt(t)}</b>${i >= 0 ? ` · ${esc(o[i].title)}${o[i].skip ? ` <span class="skiptag">skip${o[i].skip_reason ? ": " + esc(o[i].skip_reason) : ""}</span>` : ""}` : ""}`;
  tip.hidden = false;
  const w = tip.offsetWidth, tlr = $("#timeline").offsetLeft;
  tip.style.left = `${Math.min(Math.max(tlr + x - w / 2, tlr), tlr + r.width - w)}px`;
  $("#hover-line").style.left = `${x}px`; $("#hover-line").style.display = "block";
});
$("#timeline").addEventListener("mouseleave", () => { $("#tip").hidden = true; $("#hover-line").style.display = "none"; });
$("#timeline").addEventListener("click", (e) => {
  const r = e.currentTarget.getBoundingClientRect();
  seekTo(((e.clientX - r.left) / r.width) * (S.cur.lesson.duration || 0));
});

function renderProcessBar() {
  const d = S.cur;
  const missing = !d.paragraphs.length ? "No transcript or notes yet." : !d.notes ? "Transcript ready, no notes yet." : "";
  $("#process-bar").hidden = !missing && !d.job_running;
  $("#process-msg").textContent = d.job_running ? "Processing… (this page refreshes when done)" : missing;
  $("#process-btn").hidden = d.job_running;
}
$("#process-btn").onclick = async () => {
  await api(`/api/process/${S.cur.course.slug}/${S.cur.lesson.index}`, { method: "POST" });
  S.cur.job_running = true; renderProcessBar(); watchJob();
};
function watchJob() {
  const key = `${S.cur.course.slug}/${S.cur.lesson.index}`;
  const h = setInterval(async () => {
    if (!S.cur || `${S.cur.course.slug}/${S.cur.lesson.index}` !== key) return clearInterval(h);
    const d = await api(`/api/lesson/${S.cur.course.slug}/${S.cur.lesson.index}`);
    if (!d.job_running) { clearInterval(h); refreshLesson(); loadCourses(); toast("Processing finished"); }
  }, 5000);
}
async function refreshLesson() {
  if (!S.cur) return;
  const d = await api(`/api/lesson/${S.cur.course.slug}/${S.cur.lesson.index}`);
  Object.assign(S.cur, d); renderPanel(); renderTimeline(); renderProcessBar();
}

// ---------- YouTube player ----------
function loadVideo(id, start) {
  if (S.player && S.ready) { S.player.loadVideoById({ videoId: id, startSeconds: start }); return; }
  S.pendingVideo = { id, start };
  if (window.YT && YT.Player && !S.player) createPlayer();
}
function createPlayer() {
  const { id, start } = S.pendingVideo;
  S.player = new YT.Player("player", {
    videoId: id,
    playerVars: { start: Math.floor(start), rel: 0, modestbranding: 1, playsinline: 1 },
    events: {
      onReady: () => { S.ready = true; S.player.setPlaybackRate(S.rate); },
      onStateChange: (e) => {
        $("#play-btn").textContent = e.data === YT.PlayerState.PLAYING ? "❚❚" : "▶";
        if (e.data === YT.PlayerState.PLAYING && S.player.getPlaybackRate() !== S.rate) S.player.setPlaybackRate(S.rate);
        if (e.data === YT.PlayerState.ENDED) reportState();
      },
      onPlaybackRateChange: (e) => { S.rate = e.data; localStorage.rate = S.rate; renderRates(); },
    },
  });
}
window.onYouTubeIframeAPIReady = () => { if (S.pendingVideo && !S.player) createPlayer(); };

const now = () => (S.ready ? S.player.getCurrentTime() : 0);
function seekTo(t) {
  if (!S.ready) return;
  S.player.seekTo(Math.max(0, t), true);
  S.lastSkipFrom = -1;
  tick(true);
}
function setRate(r) { S.rate = r; localStorage.rate = r; if (S.ready) S.player.setPlaybackRate(r); renderRates(); }
function renderRates() {
  $("#rates").innerHTML = RATES.map((r) => `<button class="${Math.abs(r - S.rate) < 0.01 ? "active" : ""}" data-rate="${r}">${r}×</button>`).join("");
}
$("#rates").addEventListener("click", (e) => { const b = e.target.closest("button"); if (b) setRate(parseFloat(b.dataset.rate)); });

function sectionIndex(t) {
  const o = S.cur?.outline || []; let idx = -1;
  o.forEach((it, i) => { if (it.t <= t + 0.5) idx = i; });
  return idx;
}
function nextSection() { const o = S.cur.outline, i = sectionIndex(now()); if (i + 1 < o.length) seekTo(o[i + 1].t); else toast("Last section"); }
function prevSection() {
  const o = S.cur.outline, t = now(), i = sectionIndex(t);
  if (i < 0) return seekTo(0);
  seekTo(t - o[i].t > 5 || i === 0 ? o[i].t : o[i - 1].t);
}
function nextLesson() {
  const c = S.courses.find((c) => c.slug === S.cur.course.slug);
  const i = c.lessons.findIndex((l) => l.index === S.cur.lesson.index);
  if (c.lessons[i + 1]) location.hash = `#/${c.slug}/${c.lessons[i + 1].index}`;
}

let lastPara = -1;
function tick(force) {
  if (!S.cur || !S.ready) return;
  const t = now(), dur = S.cur.lesson.duration || S.player.getDuration() || 0;
  if (dur) $("#cursor").style.left = `${(t / dur) * 100}%`;
  const o = S.cur.outline, i = sectionIndex(t);
  $("#section-now").innerHTML = i >= 0 ? `<b>${fmt(o[i].t)}</b> ${esc(o[i].title)}${o[i].skip ? ` <span class="skiptag">skip: ${esc(o[i].skip_reason)}</span>` : ""}` : "";
  document.querySelectorAll(".chapter").forEach((b) => b.classList.toggle("now", +b.dataset.i === i));
  // auto-skip
  const playing = S.player.getPlayerState() === YT.PlayerState.PLAYING;
  if (S.autoskip && playing && i >= 0 && o[i].skip && S.lastSkipFrom !== i) {
    S.lastSkipFrom = i;
    let j = i; while (j < o.length && o[j].skip) j++;
    const target = j < o.length ? o[j].t : dur;
    toast(`Skipped: ${o[i].title}`);
    S.player.seekTo(target, true);
  }
  // transcript follow
  const ps = S.cur.paragraphs; let pi = -1;
  for (let k = 0; k < ps.length; k++) { if (ps[k].start <= t + 0.3) pi = k; else break; }
  if (pi !== lastPara || force) {
    document.querySelectorAll(".para.now").forEach((e) => e.classList.remove("now"));
    const el = document.querySelector(`.para[data-i="${pi}"]`);
    if (el) { el.classList.add("now"); if ($("#follow").checked && !$("#tab-transcript").hidden) el.scrollIntoView({ block: "center", behavior: "smooth" }); }
    lastPara = pi;
  }
}
setInterval(tick, 500);

// ---------- state reporting & commands from Claude ----------
function reportState() {
  if (!S.cur || !S.ready) return;
  const st = S.player.getPlayerState();
  fetch("/api/state", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({
    course: S.cur.course.slug, lesson: S.cur.lesson.index, title: S.cur.lesson.title, video_id: S.cur.lesson.video_id,
    t: now(), duration: S.cur.lesson.duration || S.player.getDuration(), rate: S.rate, playing: st === YT.PlayerState.PLAYING,
  }) }).catch(() => {});
}
setInterval(reportState, 2000);
setInterval(() => { if (S.cur) loadCourses(); }, 60000);

async function pollCommands() {
  try {
    const r = await api(`/api/commands?after=${S.lastCmd}`);
    for (const c of r.commands) runCommand(c);
    S.lastCmd = r.last;
  } catch {}
}
function runCommand(c) {
  if (c.action === "open") {
    const h = `#/${c.course}/${c.lesson}/${Math.floor(c.t || 0)}`;
    if (location.hash === h) openLesson(c.course, c.lesson, c.t); else location.hash = h;
    toast(`Claude opened lesson ${c.lesson}`);
  }
  else if (c.action === "seek") { seekTo(c.t); toast(`Claude → ${fmt(c.t)}`); }
  else if (c.action === "play") S.player?.playVideo();
  else if (c.action === "pause") S.player?.pauseVideo();
  else if (c.action === "rate") setRate(c.value);
  else if (c.action === "skip_section") nextSection();
  else if (c.action === "back") seekTo(now() - (c.value || 10));
  else if (c.action === "refresh") { refreshLesson(); loadCourses(); toast("New annotation from Claude"); }
}
setInterval(pollCommands, 1000);

// ---------- controls & keys ----------
function act(a) {
  if (!S.ready && a !== "copy") return;
  const t = now();
  switch (a) {
    case "back": seekTo(t - 10); break;
    case "fwd": seekTo(t + 10); break;
    case "play": S.player.getPlayerState() === YT.PlayerState.PLAYING ? S.player.pauseVideo() : S.player.playVideo(); break;
    case "next-sec": nextSection(); break;
    case "prev-sec": prevSection(); break;
    case "next-lesson": nextLesson(); break;
    case "copy": {
      const i = sectionIndex(t), sec = i >= 0 ? ` (section “${S.cur.outline[i].title}”)` : "";
      const txt = `[coursekit] I'm watching “${S.cur.lesson.title}” (course ${S.cur.course.slug}, lesson ${S.cur.lesson.index}) at ${fmt(t)}${sec}. `;
      navigator.clipboard.writeText(txt).then(() => toast("Context copied — paste it into Claude with your question"));
    }
  }
}
document.querySelector(".controls").addEventListener("click", (e) => { const b = e.target.closest("button[data-act]"); if (b) act(b.dataset.act); });
$("#autoskip").checked = S.autoskip;
$("#autoskip").onchange = (e) => { S.autoskip = e.target.checked; localStorage.autoskip = S.autoskip ? "1" : "0"; S.lastSkipFrom = -1; };

function toggleSidebar() {
  document.body.classList.toggle("no-sidebar");
  $("#show-sidebar").hidden = !document.body.classList.contains("no-sidebar");
}
$("#toggle-sidebar").onclick = toggleSidebar; $("#show-sidebar").onclick = toggleSidebar;

document.querySelectorAll(".tabs button").forEach((b) => b.onclick = () => {
  document.querySelectorAll(".tabs button").forEach((x) => x.classList.toggle("active", x === b));
  ["notes", "detailed", "transcript", "qa"].forEach((t) => ($(`#tab-${t}`).hidden = t !== b.dataset.tab));
  if (b.dataset.tab === "transcript") tick(true);
});

document.addEventListener("keydown", (e) => {
  if (e.target.matches("input, textarea") || e.metaKey || e.ctrlKey || e.altKey) return;
  const k = e.key;
  const map = { " ": "play", k: "play", ArrowLeft: "back", j: "back", ArrowRight: "fwd", l: "fwd", s: "next-sec", p: "prev-sec", n: "next-lesson", c: "copy" };
  if (map[k]) { e.preventDefault(); act(map[k]); }
  else if (k === ">" || k === ".") { const i = RATES.findIndex((r) => r >= S.rate - 0.01); setRate(RATES[Math.min(RATES.length - 1, i + 1)]); }
  else if (k === "<" || k === ",") { const i = RATES.findIndex((r) => r >= S.rate - 0.01); setRate(RATES[Math.max(0, i - 1)]); }
  else if (k === "a") { $("#autoskip").click(); toast(`Auto-skip ${S.autoskip ? "on" : "off"}`); }
  else if (k === "b") toggleSidebar();
  else if (k === "t") document.querySelector('.tabs button[data-tab="transcript"]').click();
});

// ---------- routing ----------
function route() {
  const m = location.hash.match(/^#\/([^/]+)\/(\d+)(?:\/(\d+))?/);
  if (m) openLesson(m[1], m[2], m[3] ? parseFloat(m[3]) : undefined);
}
window.addEventListener("hashchange", route);
renderRates();
loadCourses().then(route);
