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

1. [EVO: Long-context DNA transformer](https://www.biorxiv.org/content/10.1101/2024.02.27.582234v1)
2. [A Review: Transformer-based deep learning for predicting protein properties in the life sciences](https://elifesciences.org/articles/82819)
3. [ESM-1/2 is the SOTA for protein applications; learned on amino-acid representations](https://github.com/facebookresearch/esm/tree/main/esm)
4. [GenSLMs trained on gene sequences as 3-mer represenations as applied to COVID](https://github.com/ramanathanlab/genslm/tree/main/genslm)
5. [Single-nucleotide genomic model with >500K context window](https://github.com/HazyResearch/hyena-dna)

## Long sequence modeling in transformers
1. [Position interpolation with RoPE](https://arxiv.org/pdf/2306.15595.pdf)
2. [Feedback loops for infinite working memory](https://arxiv.org/abs/2404.09173)
3. [YaRN: Yet another RoPE extensioN method](https://arxiv.org/pdf/2309.00071.pdf)

## Fine-tuning: making the transformer work for you
1. [ORPO: preference optimization without a reference model](https://arxiv.org/abs/2403.07691)
2. [Adversarial preference optimization](https://arxiv.org/abs/2311.08045)
3. [Direct preference optimization](https://arxiv.org/pdf/2310.03708.pdf)
4. [Limitations of instruction tuning for LLMs](https://arxiv.org/pdf/2402.05119.pdf)

## Modifications to RLHF approaches
1. [Leveraging reward models for more robust modeling](https://browse.arxiv.org/pdf/2402.00782)
2. [Thinking before speaking](https://arxiv.org/pdf/2403.09629.pdf)

## Unlearning and controlled forgetting
1. [LLM Unlearning](https://openreview.net/pdf?id=wKe6jE065x)
2. [Who's Harry Potter?](https://arxiv.org/pdf/2310.02238.pdf)
3. 

## Chemistry/Molecular applications

1. [The molecular transformer](https://pubs.acs.org/doi/pdf/10.1021/acscentsci.9b00576)

## Physics and physical systems

1. [Transformers for modeling physical systems: a review](https://openreview.net/pdf/c45d1ade1683075a8a4e5bfe568cf3915805af44.pdf)
2. [Astronomical foundation models for Stars](https://arxiv.org/pdf/2308.10944.pdf)
   

## Materials/Condensed Matter Physics

1. [Generative materials design with transformers](https://ui.adsabs.harvard.edu/abs/2022arXiv220613578F/abstract)
2. [Crystal Transformer](https://ui.adsabs.harvard.edu/abs/2022arXiv220411953W/abstract)
3. [Predicting polymer properties](https://www.nature.com/articles/s41524-023-01016-5)
4. [Predict multiscale physics fields and nonlinear material properties](https://www.sciencedirect.com/science/article/abs/pii/S1369702122001316)


## Astrophysics/Cosmology

1. [Time-series transformer for Photometric Classification](https://arxiv.org/abs/2105.06178)
2. [Representing light curves with transformer embeddings](https://arxiv.org/abs/2105.06178)


## Mathematics
1. [Foundation models for PDEs](https://arxiv.org/pdf/2306.00258.pdf)