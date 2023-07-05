---
layout: default
title:  "LLMs in Science"
permalink: /llm-science/
---

Large language models (GPT-N from OpenAI, Claude from Anthropic, LLaMAs from Meta, the list goes on) have emerged as the de-facto standard of language modeling.  Transformer models trained on language show incredible capacity and generalizability that was unheard of in deep learning before 2017.  However, the applications of LLMs are not limited to language.  In fact, LLMs are a generalizable tool that can be applied to any data that can be represented as a sequence of tokens.  This includes some well-researched applications (images, audio, video), but that is not the end of where transformers can be applied.  This page hosts some works that focus on applying transformers to various domains of scientific data.  By no means is this list complete, but it has some interesting efforts in it.

I am currently working to apply transformer architectures to three separate problems:
* Genomic data, in particular, long context-windows for identifying long-range dependencies in genomic data
* Cosmological data: using transformers to model the merger history of massive galaxies and clusters
* A foundational model of astrophysical observation: Using transformers to learn to reconstruct astrophysical images from sparse data that is as close to the observing instrument as possible.

[A primer on transformers for the uninitiated](https://www.sciencedirect.com/science/article/pii/S2666651022000146)

## Biology/Life Sciences
There has been a lot of work applying transformers to genomic or protein sequence problems.  It makes a lot of sense, as genomic data is readily representable as a sequence of letters, so the transition to LLM modeling is simple (in theory)--in reality, the rules of language do not directly translate to genomics, so the problem is quite different.

A review: [Transformer-based deep learning for predicting protein properties in the life sciences](https://elifesciences.org/articles/82819)

ESM-1/2 is a standard SOTA for protein applications; learned on amino-acid representations: [ESM Github](https://github.com/facebookresearch/esm/tree/main/esm)

GenSLMs trained on nucleotide 3-mer represenations as applied to COVID: [GenSLM Github](https://github.com/ramanathanlab/genslm/tree/main/genslm)


## Chemistry/Molecular applications

[The molecular transformer](https://pubs.acs.org/doi/pdf/10.1021/acscentsci.9b00576)

## Physics and physical systems

[Transformers for modeling physical systems: a review](https://openreview.net/pdf/c45d1ade1683075a8a4e5bfe568cf3915805af44.pdf)

## Materials/Condensed Matter Physics

[Generative materials design with transformers](https://ui.adsabs.harvard.edu/abs/2022arXiv220613578F/abstract)
[Crystal Transformer](https://ui.adsabs.harvard.edu/abs/2022arXiv220411953W/abstract)

[Predicting polymer properties](https://www.nature.com/articles/s41524-023-01016-5)

[Predict multiscale physics fields and nonlinear material properties](https://www.sciencedirect.com/science/article/abs/pii/S1369702122001316)


## Astrophysics/Cosmology

[Time-series transformer for Photometric Classification](https://arxiv.org/abs/2105.06178)

[Representing light curves with transformer embeddings](https://arxiv.org/abs/2105.06178)


## Mathematics
[Foundation models for PDEs](https://arxiv.org/pdf/2306.00258.pdf)