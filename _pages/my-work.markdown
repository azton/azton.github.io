---
layout: default
title: "My Work"
permalink: /my-work/
---

<link rel="stylesheet" href="{{ '/assets/css/works.css' | relative_url }}">

<h2>My work</h2>

<!-- BIO-START -->
Azton Wells's research spans machine learning and astrophysics across two
overlapping strands. The first develops high-resolution cosmological
hydrodynamic simulations of the first galaxies. The Phoenix suite, built in
Enzo, samples tens of thousands of primordial star-forming regions and
resolves the heterogeneous chemical enrichment driven by Population III
supernovae. StarNet, a 3D convolutional surrogate, accelerates Pop III star
formation and feedback enough to be integrated directly into adaptive-mesh
cosmological runs, enabling statistically significant galaxy samples at
z ≳ 10 that remain physically consistent with higher-resolution reference
simulations.

The second strand applies large language models to scientific practice. The
AstroMLab series introduces astronomy-specific LLM benchmarks and releases
AstroSage, a family of domain-specialized models (8B and 70B parameters)
that match frontier general-purpose systems on astronomy Q&A at a fraction
of the inference cost. Related work extends transformer architectures
beyond text: LoRA adaptation of LLaMA-3.1-8B to predict galaxy redshifts
from spectra, and encoder-only foundation models that map between
simulation- and observation-derived galactic features with dynamic masking
across modalities.

Adjacent work targets the infrastructure needed to deploy such models at
scientific scale — HPC-resident retrieval-augmented generation over millions
of papers, evaluation methodologies for AI research assistants, and credit
assignment in multi-LLM agents — alongside empirical findings that context
length alone degrades LLM performance independent of retrieval quality.
Current directions push multi-modal astrophysical foundation models toward
images, merger trees, and 3D fields, and toward unified agents that handle
both quantitative modalities and natural-language reasoning.
<!-- BIO-END -->

<div class="works-meta" id="works-meta"></div>
<div class="works-list" id="works-list"></div>

<script>
  window.WORKS_JSON_URL = "{{ '/assets/data/works.json' | relative_url }}";
</script>
<script src="{{ '/assets/js/works.js' | relative_url }}"></script>
