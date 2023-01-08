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
Deep learning is opening up avenues of computation that were unimaginable 10 years ago.  My research attempts to bring the power of deep learning methods to astrophysical simulations to accomplish tasks that a) couldn't be done without it, or b) couldn't be done in a hubble time without it. In the reckless pursuit of applying deep learning to simulations, I also develop methods of error checking and validation to ensure that, although we cannot enumerate what all 40 million parameters of a model represent, we can estimate the models' correctness and trustworthiness in real time.  This work can be applied in consort with the next-generation of exascale simulation codes ([Enzo-E](https://github.com/enzo-project)) to enable the most massive hydrodynamic + star formation simulations that have ever been accomplished.

## Reading
Here, I'll put a few recent papers or articles that caught my eye.  Some focus on ML/DL methods or new architectures.  Some focus on stellar feedback or evolution.
* A Method of augmentation in generative adversarial networks, [ADA](https://nvlabs-fi-cdn.nvidia.com/stylegan2-ada/ada-paper.pdf)
* A Convolutional Tensor-train LSTM for time-series predictions, [CTTLSTM](https://sites.google.com/nvidia.com/conv-tt-lstm)
* Imagine accelerating your computation up to a [billion times](https://developer.nvidia.com/blog/using-ai-based-emulators-to-speed-up-simulations-by-billions-of-times/)


## Research Activities
* Physically motivated stellar feedback models
* External Enrichment of Minihalos by the First Supernovae
* Predicting Primordial Star Formation with Deep Convolutional Neural Networks
* Predicting the Feedback Influence of Primordial Stars with Generative Adversarial Networks
* The Phoenix Dataset: Primordial Star Formation in Cosmological Simulations

## Tools
The tools of my trade.  There's a lot of ways to accomplish astrophysics simulations and deep learning, these are just the ones I use.
* Simulations: 
    * [Enzo](https://github.com/enzo-project/
    * [Grackle](https://grackle.readthedocs.io/en/latest)
    * HACC (Hybrid-hardware Accelerated Cosmology Code)
* Numerics, data generation and analysis: Python, NumPy, Pandas and the usual data science suspects.
* Defining models, one-off testing: [Pytorch](https://pytorch.org)
* Training: [Pytorch Lightning](https://www.pytorchlightning.ai)
* Computers: [Expanse](https://www.sdsc.edu/support/user_guides/expanse.html), [Comet (RIP)](https://www.sdsc.edu/support/user_guides/comet.html), [Frontera](https://frontera-portal.tacc.utexas.edu/user-guide/intro)
