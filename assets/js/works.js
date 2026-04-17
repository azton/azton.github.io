(function () {
  "use strict";

  const ME_PATTERNS = [/^azton\s+(i\.?\s+)?wells$/i];

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, c => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#39;"
    }[c]));
  }

  function fmtDate(iso) {
    if (!iso) return "";
    const d = new Date(iso);
    return d.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
  }

  function isMe(name) {
    const n = (name || "").replace(/\./g, ".").trim();
    return ME_PATTERNS.some(rx => rx.test(n));
  }

  function renderAuthors(authors) {
    return authors.map(a => {
      const name = esc(a.name);
      return isMe(a.name) ? `<span class="me">${name}</span>` : name;
    }).join(", ");
  }

  function renderCard(w) {
    const cats = (w.categories || []).map((c, i) =>
      `<span class="work-tag${c === w.primary_category ? " primary" : ""}">${esc(c)}</span>`
    ).join("");
    const links = [];
    if (w.arxiv_id) links.push(`<a class="work-link" href="https://arxiv.org/abs/${esc(w.arxiv_id)}" target="_blank" rel="noopener">arXiv ↗</a>`);
    if (w.pdf_url)  links.push(`<a class="work-link" href="${esc(w.pdf_url)}" target="_blank" rel="noopener">PDF</a>`);
    if (w.doi)      links.push(`<a class="work-link" href="https://doi.org/${esc(w.doi)}" target="_blank" rel="noopener">DOI</a>`);
    const venue = w.venue && !w.arxiv_id ? `<span class="work-venue">${esc(w.venue)}</span>` : "";

    return `
      <article class="work-card" data-id="${esc(w.id)}">
        <h3 class="work-title"><a href="${esc(w.url)}" target="_blank" rel="noopener">${esc(w.title)}</a></h3>
        <div class="work-authors">${renderAuthors(w.authors || [])}</div>
        <div class="work-date">${esc(fmtDate(w.published))}${w.updated && w.updated !== w.published ? " · updated " + esc(fmtDate(w.updated)) : ""}</div>
        ${w.abstract ? `<p class="work-abstract">${esc(w.abstract)}</p>` : ""}
        ${w.comment ? `<div class="work-comment">${esc(w.comment)}</div>` : ""}
        <div class="work-footer">${cats}${venue}${links.join("")}</div>
      </article>`;
  }

  async function boot() {
    const url = window.WORKS_JSON_URL || "/assets/data/works.json";
    let data;
    try {
      const res = await fetch(url, { cache: "no-cache" });
      if (!res.ok) throw new Error("HTTP " + res.status);
      data = await res.json();
    } catch (e) {
      document.getElementById("works-list").innerHTML =
        `<div class="works-empty">Could not load <code>${esc(url)}</code>: ${esc(e.message)}. Run <code>python tools/works/update.py</code> to generate it.</div>`;
      return;
    }

    const included = (data.entries || []).filter(e => e.status === "included");
    included.sort((a, b) => (b.published || "").localeCompare(a.published || ""));

    const meta = document.getElementById("works-meta");
    const when = data.generated_at ? new Date(data.generated_at).toLocaleString() : "?";
    const years = included.length ? `${included[included.length - 1].published.slice(0, 4)}–${included[0].published.slice(0, 4)}` : "";
    meta.textContent = `${included.length} papers${years ? " · " + years : ""} · refreshed ${when}`;

    const list = document.getElementById("works-list");
    list.innerHTML = included.length
      ? included.map(renderCard).join("")
      : `<div class="works-empty">No papers included yet. See <code>tools/works/overrides.yml</code>.</div>`;
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
