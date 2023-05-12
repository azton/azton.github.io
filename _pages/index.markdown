---
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://jekyllrb.com/docs/themes/#overriding-theme-defaults

layout: default
title: Home
permalink: /
sidebar_sort_order: 1
---
![Early Cosmological Simulations](/assets/img/galgif.gif)
## Research Interests
Deep learning is opening up avenues of computation that were unimaginable 10 years ago.  My research attempts to bring the power of deep learning methods to astrophysical simulations to accomplish tasks that a) couldn't be done without it, or b) couldn't be done in a hubble time without it. In the reckless pursuit of applying deep learning to simulations, I also develop methods of error checking and validation to ensure that, although we cannot enumerate what all 40 million parameters of a model represent, we can estimate the models' correctness and trustworthiness in real time.  

I've also developed an interest in the analysis of deep learning architectures.  For example, given several architectures trained on the same task, how can we compare them, beyond tradition metrics like accuracy or area-under-the-curve metrics?  Which architectures generalize most effectively, and can we quantify how/when they will break?  How can we build interpretability into model predictions?  

## Reading
Here, I'll put a few recent papers or articles that caught my eye.  Some focus on ML/DL methods or new architectures.  Some focus on stellar feedback or evolution.

* [Linear attention in transformers: ALiBi](https://arxiv.org/abs/2108.12409)
* [Extending context windows: Mega](https://arxiv.org/abs/2209.10655)
* [Dead simple memory in transformers: RMT](https://arxiv.org/abs/2207.06881)
* [SWIN](https://arxiv.org/pdf/2111.09883.pdf)
* [Convolutions and trasformers, together at last](https://arxiv.org/pdf/2103.15808.pdf)
* [VAN](https://arxiv.org/pdf/2202.09741.pdf)
* [Transformer performing U-Nets job](https://arxiv.org/pdf/2112.01527.pdf)
* [Neighborhood Attention](https://arxiv.org/pdf/2204.07143.pdf)
* [Getting language models to be more factual; Retrieval Augmented Generation](https://arxiv.org/pdf/2005.11401.pdf)
* A Method of augmentation in generative adversarial networks, [ADA](https://nvlabs-fi-cdn.nvidia.com/stylegan2-ada/ada-paper.pdf)
* A Convolutional Tensor-train LSTM for time-series predictions, [CTTLSTM](https://sites.google.com/nvidia.com/conv-tt-lstm)
* Imagine accelerating your computation up to a [billion times](https://developer.nvidia.com/blog/using-ai-based-emulators-to-speed-up-simulations-by-billions-of-times/)


## Research Activities
* Long-context Transformers for genomic applications (https://github.com/azton/GenomeLM)
* Physically motivated stellar feedback models
* External Enrichment of Minihalos by the First Supernovae
* Predicting Primordial Star Formation with Deep Convolutional Neural Networks
* Predicting the Feedback Influence of Primordial Stars with Generative Adversarial Networks
* The Phoenix Dataset: Primordial Star Formation in Cosmological Simulations

## Tools
The tools of my trade.  There's a lot of ways to accomplish astrophysics simulations and deep learning, these are just the ones I use.
* Simulations: 
    * [Enzo](https://github.com/enzo-project/)
    * [Grackle](https://grackle.readthedocs.io/en/latest)
    * HACC (Hybrid/Hardware Accelerated Cosmology Code)
* Numerics, data generation and analysis: Python, NumPy, Pandas, HDF5, and the usual data science suspects.
* Defining models, one-off testing: [Pytorch](https://pytorch.org)
* Training: sometimes [Pytorch Lightning](https://www.pytorchlightning.ai) and sometimes just Pytorch
* Computers: 
  * [Polaris](https://www.alcf.anl.gov/polaris)
  * [SambaNova and Cerebras AI accelerator systems](https://www.alcf.anl.gov/alcf-ai-testbed) 
  * [Expanse](https://www.sdsc.edu/support/user_guides/expanse.html)
  * [Comet (RIP)](https://www.sdsc.edu/support/user_guides/comet.html) 
  * [Frontera](https://frontera-portal.tacc.utexas.edu/user-guide/intro) 