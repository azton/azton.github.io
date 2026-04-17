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

- `tools/works/update.py` — fetches arXiv + Semantic Scholar and merges.
- `tools/works/overrides.yml` — manual include/exclude + pinned S2
  `author_ids`. include/exclude accept bare arXiv id (`2511.10687`),
  `arxiv:<id>`, `doi:<doi>`, or `s2:<paperId>`.
- `tools/works/requirements.txt` — `PyYAML`.
- `_pages/my-work.markdown` — the page shell (renders the papers grid).
- `_pages/index.markdown` — home page. The bio lives here, between the
  `<!-- BIO-START -->` / `<!-- BIO-END -->` markers, directly under the gif.
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
   Two sources are queried: arXiv (`au:"Azton Wells"`) and Semantic Scholar
   (every pinned `author_ids` in overrides.yml). Results are merged by
   arXiv id → DOI → normalized title. S2 is how we catch papers arXiv
   misses (journal-only publications, old conference papers, etc.). The
   script prints `included`, `excluded`, and `needs_review` counts.

3. **Resolve `needs_review`.** For arXiv-only records this triggers when
   no author string exactly matches `Azton Wells` / `Azton I. Wells`
   (case-insensitive, punctuation-tolerant). S2 records auto-include when
   tied to a pinned `author_ids` profile, so they don't usually land here.
   For each needs_review entry:
   - Open the paper and read the author list + abstract.
   - If it's clearly Azton, add the identifier to `include:` in
     `tools/works/overrides.yml` — any of bare arxiv id, `arxiv:<id>`,
     `doi:<doi>`, or `s2:<paperId>` works.
   - If it's clearly someone else, add it to `exclude:`.
   - If you can't tell, leave it out (it stays in `needs_review`).

   **Also spot-check included S2-only entries.** S2 sometimes attaches
   name-collision papers or orphan duplicate records to the pinned author
   profile. Anything co-authored with recognizable colleagues is almost
   certainly correct; anything with a list of strangers in an unfamiliar
   subfield should be audited. Exclude false positives by `s2:<paperId>`.

4. Re-run the script until `needs_review` is empty or contains only entries
   you've consciously left unresolved.

5. **Rewrite the bio.** Read every `included` entry's title + abstract in
   `assets/data/works.json`. Then edit `_pages/index.markdown`, replacing
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
   git add assets/data/works.json tools/works/overrides.yml _pages/index.markdown
   git commit -m "works: refresh papers and bio"
   git push
   ```

### Disambiguation rules (what the script decides on its own)

Checked in this order; first match wins:

1. Identifier in `overrides.yml` `exclude` → **excluded**.
2. Identifier in `overrides.yml` `include` → **included**.
3. S2 attributes the paper to a pinned `semantic_scholar.author_ids`
   profile → **included** (the user vetted the profile).
4. Any author string exactly matches `Azton Wells` / `Azton I. Wells`
   (case-insensitive, punctuation-tolerant) → **included**.
5. Otherwise → **needs_review**.

Do not relax rule 4 — false positives on big collaboration papers are the
main risk. S2 profile pinning (rule 3) is the trust boundary for non-arXiv
sources; keep `author_ids` audited when new profiles appear on S2.

### Future source: bioRxiv

When Azton publishes on bioRxiv, extend `tools/works/update.py` with a
`fetch_biorxiv()` that returns records matching the same shape as `fetch_arxiv`.
Plumb it through `main()` and pass the list into `merge_records(...)`
alongside arXiv and S2 — the rest of the pipeline (classify/dedup/render)
is source-agnostic.

---

## 2. Conferences (`/conferences/`)

Source files:

- `tools/conferences/update.py` — three sources: INSPIRE-HEP (astro/cosmo
  conferences), `huggingface/ai-deadlines` (major ML/AI/NLP venues, per-
  venue YAML pulled from raw.githubusercontent.com), and `curated.yml`.
  Flags: `--no-inspire`, `--no-ai-deadlines` for debugging a single source.
- `tools/conferences/curated.yml` — hand-maintained venues. Used for (a)
  workshop-level entries the other feeds don't carry (ML4PS, AI4Science,
  ADASS, MLHPC @ SC, AAS), and (b) ML venues missing from ai-deadlines
  (e.g. MLSys). INSPIRE-HEP doesn't expose CFPs and ai-deadlines is often
  a cycle behind for brand-new years, so curated remains the source of
  truth for submission deadlines on anything that matters.
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
   categories, future events only. Each INSPIRE hit then runs through a
   keyword relevance filter (see below) before merging with curated. The
   script merges curated + filtered INSPIRE (curated wins on id
   collisions), dedupes by (title, opening_date) since INSPIRE can carry
   the same physical conference under multiple records, and sorts by
   deadline then event start.

4. **Spot-check the output.** Open `assets/data/conferences.json` and
   confirm:
   - Counts are sane (curated entries preserved; INSPIRE count non-zero
     unless network blocked; "dropped by relevance filter" line in the
     script output is non-trivial — typically 60–70% of raw INSPIRE hits
     get cut).
   - No curated entry has `null` dates that you intended to resolve.
   - Skim the kept INSPIRE titles. If formal-theory venues are slipping
     through ("Strings 20XX", "<X> in Fundamental Physics", "Holography
     and <Y>", etc.), tune the keyword lists in `update.py` (see "Keyword
     filter" below).

### Venue (host-city) filter

INSPIRE entries also pass through a host-city allowlist
(`US_VENUE_CITIES` and `INTL_VENUE_CITIES` in `update.py`). The site owner
doesn't travel to small university workshops; this filter keeps:

- **US**: cities containing a top-~50 research university or major astro
  national lab. National labs are listed by host town
  (`argonne`, `greenbelt`, `batavia`, `los alamos`, `upton`, `aspen`, ...).
- **International**: a short list of major astro/physics-adjacent cities
  where the trip is plausible — Oxford, London, Edinburgh, Zurich,
  Lausanne, Geneva, Munich, Garching, Heidelberg, Paris/Saclay, Leiden,
  Tokyo, Kyoto, Beijing, Shanghai, Seoul, Toronto, Vancouver, Canberra,
  Sydney, Melbourne, etc.
- Entries with **no location string** (typically virtual/online) pass
  through — they cost nothing to attend.

Add cities only if you'd actually travel there for a workshop. Removing
a city is a one-line change. Both lists live at the top of `update.py`
right under `MIN_RELEVANCE_SCORE`.

### Keyword filter

`tools/conferences/update.py` defines `POS_KEYWORDS` and `NEG_KEYWORDS`.
INSPIRE entries are scored by keyword hits in their title (+ subtitle):

- A positive hit is required — entries with **zero positive hits are
  dropped immediately** regardless of negatives.
- Negative hits subtract 2 each from the score.
- Entries with final score ≥ 1 are kept.

This is tuned to the site owner's actual research: cosmological hydro
simulations of the first galaxies, ML/HPC for astro, foundation models for
cosmology data. Workshop topics like de Sitter holography, lattice QCD,
collider phenomenology, AdS/CFT, scattering-amplitudes formalism, and
strings & cosmology are filtered out; observational cosmology, galaxy
formation, gravitational-wave astronomy (data-side), simulation venues,
ML-for-science, and HPC stay in.

If a venue you do want is being filtered, add a missing positive keyword
to `POS_KEYWORDS`. If a venue you don't want is slipping through, look at
its title and add the most distinctive theoretical-formalism keyword to
`NEG_KEYWORDS` — and then re-run the script and re-skim the kept list to
make sure you didn't over-filter. Be careful: "string" alone catches
"cosmic string" (astro), so the negatives use compound forms like
"string theor", "strings &", "strings 20".

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
- **General ML / AI / NLP** venues — **parent conferences ARE tracked**
  because knowing their CFP cycle predicts when the attached
  astro/science workshops will open. These are auto-pulled from
  `huggingface/ai-deadlines`. The whitelist in `update.py`
  (`AI_DEADLINES_WHITELIST`) covers the big 17: NeurIPS, ICML, ICLR, AAAI,
  IJCAI, UAI, AISTATS, ACL, EMNLP, NAACL, COLM, CoNLL, KDD, CIKM, SIGIR,
  ECIR, WSDM. Add/remove venues there, not here in curated.yml, unless
  the feed is missing the venue entirely (e.g. MLSys). List each
  science-relevant *workshop* (ML4PS, AI4Science,
  AI4DifferentialEquations, ML4Materials if astro, SciML/MLIS) as its own
  curated entry with `parent:` set to the host conference, so the
  deadline countdown shows on the workshop directly.
- **Subdiscipline-focused non-astro** venues — materials, quantum
  computing, HEP collider physics, condensed matter, pure biology, etc.
  **Out of scope.** Do not add them even if they have ML content.
- **HPC + astro** overlap (PASC, SC workshops on cosmological simulation,
  Indico workshops at observatories) — in scope.

If an entry straddles the scope boundary and you're unsure, leave it out
and note it in the commit message so the user can weigh in.

### Deadline estimation

When a conference has no known `submission_deadline` but does have a
future `start` date, `apply_deadline_estimate()` fills in an
`estimated_deadline` of `start - typical_lead`. Lead-time buckets
(`ESTIMATED_LEAD_DAYS` in `update.py`): ml-main 150d, ml-workshop 60d,
hpc-main 150d, hpc-workshop 90d, astro-workshop 60d, astro-conf 45d,
default 60d. Bucket is chosen by tags + name keywords (NeurIPS/ICML,
"workshop", "hpc", etc.).

Rules:

- Skipped for `source: ai-deadlines` entries — those have authoritative
  deadlines, so a null value means "CFP already passed," not "unknown."
  Estimating them would mislead.
- Skipped when the event is more than ~10 months out (`ESTIMATE_HORIZON_DAYS`)
  or when the estimate would land in the past (the user should look up
  the real CFP rather than trust a stale guess).
- Renderer (`conferences.js`) shows estimates as `est. CFP ~YYYY-MM-DD
  (Nd)` in italicized orange on the event card — visually distinct from
  real deadlines, which stay in the deadline list.

When tuning lead days, check the script's "estimated deadlines for N
entries" print line and spot-check the categories; an entry landing in
an obviously wrong bucket usually means the name/tags heuristic in
`_estimate_lead_category()` needs a new keyword.

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
