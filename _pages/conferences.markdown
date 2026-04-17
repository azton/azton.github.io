---
layout: default
title: "Conferences"
permalink: /conferences/
---

<link rel="stylesheet" href="{{ '/assets/css/conferences.css' | relative_url }}">

<h2>Conferences &amp; workshops</h2>
<p class="conf-intro">
  Upcoming astrophysics/cosmology venues and ML/HPC workshops with astro-relevant content.
  Curated entries carry submission deadlines; INSPIRE-HEP provides the conference event dates.
  Data refreshed by <code>tools/conferences/update.py</code>.
</p>

<div class="conf-controls">
  <div class="conf-filters" id="conf-filters"></div>
  <label class="conf-toggle">
    <input type="checkbox" id="conf-show-past"> show past
  </label>
</div>

<section id="conf-deadlines">
  <h3>Submission deadlines</h3>
  <div class="conf-list" id="conf-list-deadlines"></div>
</section>

<section id="conf-events">
  <h3>Upcoming events (no curated deadline)</h3>
  <div class="conf-list" id="conf-list-events"></div>
</section>

<p class="conf-meta" id="conf-meta"></p>

<script>
  window.CONFERENCES_JSON_URL = "{{ '/assets/data/conferences.json' | relative_url }}";
</script>
<script src="{{ '/assets/js/conferences.js' | relative_url }}"></script>
