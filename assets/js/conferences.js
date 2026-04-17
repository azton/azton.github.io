(function () {
  "use strict";

  const STATE = {
    data: null,
    filters: new Set(),        // active tag filters; empty = show all
    showPast: false,
  };

  const URGENT_DAYS = 7;
  const SOON_DAYS = 30;

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, c => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#39;"
    }[c]));
  }

  function daysBetween(iso) {
    if (!iso) return null;
    // Accept YYYY-MM-DD or full ISO
    const t = new Date(iso.length === 10 ? iso + "T23:59:59Z" : iso).getTime();
    const now = Date.now();
    return Math.round((t - now) / 86400000);
  }

  function fmtDate(iso) {
    if (!iso) return "";
    const d = new Date(iso.length === 10 ? iso + "T00:00:00Z" : iso);
    return d.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
  }

  function fmtRange(start, end) {
    if (!start && !end) return "";
    if (!end || end === start) return fmtDate(start);
    return fmtDate(start) + " – " + fmtDate(end);
  }

  function classifyByDeadline(d) {
    if (d == null) return "is-event";
    if (d < 0) return "is-past";
    if (d <= URGENT_DAYS) return "is-urgent";
    if (d <= SOON_DAYS) return "is-soon";
    return "is-ok";
  }

  function passesFilter(entry) {
    if (STATE.filters.size === 0) return true;
    const tags = entry.tags || [];
    for (const f of STATE.filters) {
      if (tags.indexOf(f) === -1) return false;
    }
    return true;
  }

  function isPast(entry) {
    const d = daysBetween(entry.submission_deadline);
    const s = daysBetween(entry.end || entry.start);
    if (d !== null) return d < 0 && (s == null || s < 0);
    if (s !== null) return s < 0;
    return false;
  }

  function renderCountdown(entry, kind /* "deadline" | "event" */) {
    let iso = null, label = "";
    if (kind === "deadline") { iso = entry.submission_deadline; label = "until CFP"; }
    else                     { iso = entry.start; label = "until start"; }
    const d = daysBetween(iso);
    if (d === null) return `<div class="conf-countdown"><span class="num">—</span><span class="lbl">${esc(label)}</span></div>`;
    if (d < 0)     return `<div class="conf-countdown"><span class="num">${Math.abs(d)}d</span><span class="lbl">ago</span></div>`;
    if (d === 0)   return `<div class="conf-countdown"><span class="num">today</span><span class="lbl">${esc(label)}</span></div>`;
    return `<div class="conf-countdown"><span class="num">${d}d</span><span class="lbl">${esc(label)}</span></div>`;
  }

  function renderCard(entry, kind) {
    const iso = kind === "deadline" ? entry.submission_deadline : entry.start;
    const d = daysBetween(iso);
    let cls = classifyByDeadline(d);
    if (kind === "event" && d !== null && d >= 0) cls = "is-event";
    if (d !== null && d < 0) cls = "is-past";

    const approx = entry.approximate ? '<span class="approx">~ approximate</span>' : "";
    const metaParts = [];
    if (entry.parent)   metaParts.push(`<span><span class="k">parent</span>${esc(entry.parent)}</span>`);
    if (entry.location) metaParts.push(`<span><span class="k">where</span>${esc(entry.location)}</span>`);
    const eventWhen = fmtRange(entry.start, entry.end);
    if (eventWhen) metaParts.push(`<span><span class="k">event</span>${esc(eventWhen)}</span>`);
    if (kind === "deadline" && entry.submission_deadline) {
      metaParts.push(`<span><span class="k">deadline</span>${esc(fmtDate(entry.submission_deadline))}${entry.deadline_note ? " — " + esc(entry.deadline_note) : ""}</span>`);
    }
    if (approx) metaParts.push(approx);

    const tagsHtml = (entry.tags || []).map(t => `<span class="conf-tag">${esc(t)}</span>`).join("")
      + `<span class="conf-tag source-${esc(entry.source || "misc")}">${esc(entry.source || "misc")}</span>`;

    const nameHtml = entry.url
      ? `<a href="${esc(entry.url)}" target="_blank" rel="noopener">${esc(entry.name)}</a>`
      : esc(entry.name);

    const actions = entry.url
      ? `<div class="conf-actions"><a href="${esc(entry.url)}" target="_blank" rel="noopener">open ↗</a></div>`
      : `<div class="conf-actions"></div>`;

    return `
      <article class="conf-card ${cls}" data-id="${esc(entry.id)}">
        ${renderCountdown(entry, kind)}
        <div class="conf-body">
          <h4 class="conf-name">${nameHtml}</h4>
          ${entry.full_name ? `<div class="conf-sub">${esc(entry.full_name)}</div>` : ""}
          <div class="conf-meta-row">${metaParts.join("")}</div>
          ${entry.notes ? `<div class="conf-sub" style="margin-top:4px">${esc(entry.notes)}</div>` : ""}
          <div class="conf-tags">${tagsHtml}</div>
        </div>
        ${actions}
      </article>`;
  }

  function collectTags(entries) {
    const counts = new Map();
    for (const e of entries) {
      for (const t of e.tags || []) counts.set(t, (counts.get(t) || 0) + 1);
    }
    return [...counts.entries()].sort((a, b) => b[1] - a[1]);
  }

  function renderFilters() {
    const host = document.getElementById("conf-filters");
    const tags = collectTags(STATE.data.entries);
    host.innerHTML = tags.map(([t, n]) => {
      const on = STATE.filters.has(t) ? " on" : "";
      return `<span class="conf-chip${on}" data-tag="${esc(t)}">${esc(t)} <span style="opacity:.6">${n}</span></span>`;
    }).join("");
    host.querySelectorAll(".conf-chip").forEach(el => {
      el.addEventListener("click", () => {
        const t = el.dataset.tag;
        if (STATE.filters.has(t)) STATE.filters.delete(t); else STATE.filters.add(t);
        renderFilters();
        renderLists();
      });
    });
  }

  function renderLists() {
    const pool = STATE.data.entries.filter(e => {
      if (!passesFilter(e)) return false;
      if (!STATE.showPast && isPast(e)) return false;
      return true;
    });

    const deadlines = pool
      .filter(e => e.submission_deadline)
      .sort((a, b) => a.submission_deadline.localeCompare(b.submission_deadline));

    const events = pool
      .filter(e => !e.submission_deadline && (e.start || e.end))
      .sort((a, b) => (a.start || a.end || "").localeCompare(b.start || b.end || ""));

    const dl = document.getElementById("conf-list-deadlines");
    const ev = document.getElementById("conf-list-events");

    dl.innerHTML = deadlines.length
      ? deadlines.map(e => renderCard(e, "deadline")).join("")
      : `<div class="conf-empty">No curated deadlines in view. Toggle filters or add entries to <code>tools/conferences/curated.yml</code>.</div>`;

    ev.innerHTML = events.length
      ? events.map(e => renderCard(e, "event")).join("")
      : `<div class="conf-empty">No upcoming events in view.</div>`;
  }

  function renderMeta() {
    const m = document.getElementById("conf-meta");
    const d = STATE.data;
    const when = d.generated_at ? new Date(d.generated_at).toLocaleString() : "?";
    m.textContent = `Last refreshed ${when} — ${d.entries.length} entries (curated + INSPIRE-HEP).`;
  }

  async function boot() {
    const url = window.CONFERENCES_JSON_URL || "/assets/data/conferences.json";
    try {
      const res = await fetch(url, { cache: "no-cache" });
      if (!res.ok) throw new Error("HTTP " + res.status);
      STATE.data = await res.json();
    } catch (e) {
      document.getElementById("conf-list-deadlines").innerHTML =
        `<div class="conf-empty">Could not load <code>${esc(url)}</code>: ${esc(e.message)}. Run <code>python tools/conferences/update.py</code> to generate it.</div>`;
      return;
    }
    document.getElementById("conf-show-past").addEventListener("change", (e) => {
      STATE.showPast = e.target.checked;
      renderLists();
    });
    renderFilters();
    renderLists();
    renderMeta();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
