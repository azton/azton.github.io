---
layout: default
title: "My Work"
permalink: /my-work/
---

<link rel="stylesheet" href="{{ '/assets/css/works.css' | relative_url }}">

<h2>My work</h2>

<div class="works-meta" id="works-meta"></div>
<div class="works-list" id="works-list"></div>

<script>
  window.WORKS_JSON_URL = "{{ '/assets/data/works.json' | relative_url }}";
</script>
<script src="{{ '/assets/js/works.js' | relative_url }}"></script>
