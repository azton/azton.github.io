# CLAUDE.md — azton.github.io

Jekyll site (theme: `not-pure-poole`). Pages live in `_pages/`, nav in
`_data/navigation.yml`, posts in `_posts/`. Local preview:

```bash
bundle exec jekyll serve
```

This file documents the two Claude-driven workflows on this site: **updating
My Work** (papers list + bio), and **updating Conferences** (deadline tracker).
Both write a JSON file under `assets/data/` that the page reads client-side.

When asked to refresh a page, do these things without asking — they are safe,
local, and expected.

**"Update the pages" (no specific page named) means do both workflows.**
Run My Work first, then Conferences. Commit each in its own commit so the
diff reads cleanly. Push once at the end.

---

## 1. My Work (`/my-work/`)

Source files:

- `tools/works/update.py` — fetches arXiv for the author.
- `tools/works/overrides.yml` — manual include/exclude of arXiv IDs.
- `tools/works/requirements.txt` — `PyYAML`.
- `_pages/my-work.markdown` — the page shell. Contains the bio between the
  `<!-- BIO-START -->` / `<!-- BIO-END -->` markers.
- `assets/js/works.js`, `assets/css/works.css` — renderer + styles.
- `assets/data/works.json` — generated output. **Commit this.**

### Update procedure

1. Make sure deps are installed once per machine:
   ```bash
   pip install -r tools/works/requirements.txt
   ```

2. Run the fetcher:
   ```bash
   python tools/works/update.py
   ```
   The script prints `included`, `excluded`, and `needs_review` counts. It
   also lists each `needs_review` arXiv ID with its title and lead author.

3. **Resolve `needs_review`.** arXiv's name match of `au:"Azton Wells"`
   catches most things unambiguously, but anything where no author string
   matched an exact form (`Azton Wells`, `Azton I. Wells`) lands here. For
   each:
   - Open `https://arxiv.org/abs/<id>` and read the author list + abstract.
   - If it's clearly Azton, add the bare id to `include:` in
     `tools/works/overrides.yml`.
   - If it's clearly someone else, add it to `exclude:` so future runs stop
     warning about it.
   - If you can't tell, leave it out (it stays in `needs_review`, invisible
     on the page).

4. Re-run the script until `needs_review` is empty or contains only entries
   you've consciously left unresolved.

5. **Rewrite the bio.** Read every `included` entry's title + abstract in
   `assets/data/works.json`. Then edit `_pages/my-work.markdown`, replacing
   everything between `<!-- BIO-START -->` and `<!-- BIO-END -->` with a
   ~150–250 word bio that:
   - Summarizes research themes (not a list of papers — thematic synthesis).
   - Notes current directions.
   - **Matches the syntactic style and tone of the abstracts themselves**
     (dense, declarative, technical; no first-person; no marketing words).
   - Avoids paper-level citations in prose. Don't say "in 2.5.4 we showed X".
     State the theme; the cards below carry the specifics.
   - Stays honest about the distribution. If most recent work is LLMs/agents
     and older work is cosmological hydrodynamics, say both.

6. Preview locally if you want (`bundle exec jekyll serve`) then commit:
   ```bash
   git add assets/data/works.json tools/works/overrides.yml _pages/my-work.markdown
   git commit -m "works: refresh papers and bio"
   git push
   ```

### Disambiguation rules (what the script decides on its own)

- `author name == "Azton Wells"` (any middle-initial variant, case-insensitive,
  punctuation-tolerant) → **included**. The middle initial makes this safe.
- Appears in `overrides.yml` `exclude` → **excluded**.
- Appears in `overrides.yml` `include` → **included** even if the name is
  ambiguous.
- Otherwise → **needs_review**.

Do not relax the default — false positives on big collaboration papers are the
main risk.

### Future source: bioRxiv

When Azton publishes on bioRxiv, extend `tools/works/update.py` with a
`fetch_biorxiv()` that returns records matching the same shape as `fetch_arxiv`.
The rest of the pipeline (classify/write/render) is source-agnostic.

---

## 2. Conferences (`/conferences/`)

Source files:

- `tools/conferences/update.py` — pulls INSPIRE-HEP + merges curated YAML.
- `tools/conferences/curated.yml` — hand-maintained venues (deadlines live
  here; INSPIRE-HEP doesn't expose CFPs).
- `tools/conferences/requirements.txt` — `requests`, `PyYAML`.
- `_pages/conferences.markdown` — page shell.
- `assets/js/conferences.js`, `assets/css/conferences.css`.
- `assets/data/conferences.json` — generated output. **Commit this.**

### Update procedure

1. Install deps once per machine:
   ```bash
   pip install -r tools/conferences/requirements.txt
   ```

2. **Curate `curated.yml` before running the script.** INSPIRE-HEP gives you
   conference event dates but NOT submission deadlines, so the curated file
   is where the action items live. During an update pass, do all of the
   following:

   - **Resolve placeholder entries.** Every entry with `approximate: true`
     or any `null` date needs attention. For each, open its `url` and look
     for the current year's CFP / abstract-submission date. If you find it,
     fill in `submission_deadline`, `start`, `end`, `location`, drop
     `approximate: true`, and tighten the `deadline_note` to something
     concrete ("abstract subs due X", "papers only, AoE"). If the URL still
     points to last year's meeting and no new CFP is posted, leave the
     entry as-is and note `deadline_note: "next CFP not yet announced"`.

   - **Archive past entries.** If `end` is in the past *and* the venue has
     an announced successor (e.g. ML4PS 2026 → ML4PS 2027), bump the entry
     in place: change `id` suffix to the new year, clear the dates, set
     `approximate: true`, update the note. Don't accumulate stale entries.

   - **Add venues the user mentions.** Follow the schema comments at the top
     of `curated.yml`. Always include `tags`; the page's filter chips are
     built from them.

   - **Verify URLs.** If an `open ↗` link now 404s or redirects to a parked
     domain, either update the URL to the current official page or delete
     the entry.

3. Run the fetcher:
   ```bash
   python tools/conferences/update.py
   ```
   INSPIRE-HEP is queried for Astrophysics + Gravitation and Cosmology
   categories, future events only. The script merges curated + INSPIRE
   (curated wins on id collisions) and sorts by deadline, then event start.

4. **Spot-check the output.** Open `assets/data/conferences.json` and
   confirm:
   - Counts are sane (curated entries roughly preserved; INSPIRE count
     non-zero unless network blocked).
   - No curated entry has `null` dates that you intended to resolve.
   - No obvious subdiscipline mismatches from INSPIRE (see guardrails
     below); if one slips in, the right fix is usually not to add it to an
     exclude list — just ignore it. The page is driven by filter chips, and
     anything outside astro/cosmo tags stays off the default view.

5. Commit and push:
   ```bash
   git add tools/conferences/curated.yml assets/data/conferences.json
   git commit -m "conferences: refresh"
   git push
   ```

### Scope guardrails

The Conferences page is deliberately narrow. When curating, apply these
rules strictly:

- **Astrophysics / cosmology** venues — always in scope.
- **General physics / science** venues (SC, PASC, ISC, IPDPS, SMC) — in
  scope **only if** they host an astro/cosmo-relevant workshop (MLHPC,
  AI4S, SciML, etc.). In that case the *workshop* is the entry, not the
  parent conference. Set `parent:` to the host conference.
- **General ML** venues (NeurIPS, ICML, ICLR, AAAI) — main tracks are **out
  of scope**. Their astro/science-focused workshops (ML4PS, AI4Science,
  AI4DifferentialEquations, ML4Materials if astro-relevant) are in scope.
  Again, list each workshop as its own entry.
- **Subdiscipline-focused non-astro** venues — materials, quantum
  computing, HEP collider physics, condensed matter, pure biology, etc.
  **Out of scope.** Do not add them even if they have ML content.
- **HPC + astro** overlap (PASC, SC workshops on cosmological simulation,
  Indico workshops at observatories) — in scope.

If an entry straddles the scope boundary and you're unsure, leave it out
and note it in the commit message so the user can weigh in.

### Standard venues to keep fresh

These should almost always be represented in `curated.yml` with whatever
information is currently knowable:

- **ML4PS** @ NeurIPS (annual)
- **AI4Science** @ NeurIPS, @ ICML (annual each)
- **AI4DifferentialEquations** / **SciML / MLIS** @ ICLR (annual)
- **ADASS** (annual)
- **AAS Winter** + **AAS Summer** (biannual)
- **MLHPC** / **AI4S** workshops @ SC (annual)
- **PASC** (annual)
- Mission-specific collaboration meetings the user cares about (Rubin/LSST,
  DESI, Euclid, SKA) if they're accepting outside contributions — add on
  request rather than preemptively.

---

## Editing rules that apply to both

- Generated JSON (`assets/data/*.json`) is committed — GitHub Pages serves it
  directly; there is no CI build step for it.
- Keep `_data/navigation.yml` as one YAML list item per link (one `title` +
  one `url` per item). Duplicated keys in a single item cause Jekyll to keep
  only the last, which has bitten this site before.
- Don't introduce a JS framework, bundler, or npm. These pages are deliberately
  plain: one HTML page + one JS file + one CSS file + one JSON file.
- Don't bind scripts to network services other than the ones listed here
  without flagging the new dependency to the user first.
