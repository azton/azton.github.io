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
I am deeply involved in three major areas of work spanning genomics, cosmology, and language modeling.  My work on genome-scale language models is a continuation of the Gordon Bell prize-winning GenSLM models.  There, I work to extend the context window of the models to be able to analyze whole bacterial and viral genomes in a single context--which would enable modeling evolutionary or mutational trajectories.  Second, I work in domain specific foundation models for cosmology, where we aim to create multi-modal models capable of relating different representations of the same objects, such as learning the relationship between a galaxy image and star formation history from the same object. From these models, you can robustly predict various quantities as they are requested, instead of being constrained by the pretraining of the model.  Finally, I work in the area of large language models on the AuroraGPT project.  There, I lead a team to incorporate scientific knowledge into the post-pretraining protocols in meaningful ways.  We have created instruct tuning and preference optimization pipelines that outperform thier state-of-the-art counterparts in many evaluations, including MMLU and Decoding Trust.  Our current focus is on generating instruct and preference datasets that enhance scientific interactions and reinforce the scientific training corpora that will be  used on Aurora GPT.  

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
* Long-context Transformers for genomic applications
* AuroraGPT: Post-pretraining model tuning and instruction generation
* Generative models for cosmology and astrophysics
* Physically motivated stellar feedback models
* External Enrichment of Minihalos by the First Supernovae
* Predicting Primordial Star Formation with Deep Convolutional Neural Networks
* Predicting the Feedback Influence of Primordial Stars with Generative Adversarial Networks
* The Phoenix Dataset: Primordial Star Formation in Cosmological Simulations

## Tools
The tools of my trade.  There's a lot of ways to accomplish my multi-disciplinary work, but these are the ones I've used and worked with most.
* Simulations: 
    * [Enzo](https://github.com/enzo-project/)
    * [Grackle](https://grackle.readthedocs.io/en/latest)
    * HACC (Hybrid/Hardware Accelerated Cosmology Code)
* Numerics, data generation and analysis: Python, NumPy, Pandas, HDF5, and the usual data science suspects.
* Defining models, one-off testing: [Pytorch](https://pytorch.org)
* Training: sometimes [Pytorch Lightning](https://www.pytorchlightning.ai) and sometimes just Pytorch
* Huggingface Transformers: [Transformers](https://huggingface.co/transformers)
* Huggingface Accelerate: [Accelerate](https://huggingface.co/accelerate)
* [TRL](https://docs.vllm.ai/en/stable/)
* [Megatron-LM](https://github.com/NVIDIA/Megatron-LM)
* [Deepspeed](https://www.deepspeed.ai)
* [vLLM](https://docs.vllm.ai/en/stable/)
* Computers: 
  * [Polaris](https://www.alcf.anl.gov/polaris)
  * [Frontier](https://www.olcf.ornl.gov/frontier/)
  * [Aurora](https://www.alcf.anl.gov/aurora)
  * [SambaNova and Cerebras AI accelerator systems](https://www.alcf.anl.gov/alcf-ai-testbed) 
  * [Expanse](https://www.sdsc.edu/support/user_guides/expanse.html)
  * [Comet (RIP)](https://www.sdsc.edu/support/user_guides/comet.html) 
  * [Frontera](https://frontera-portal.tacc.utexas.edu/user-guide/intro) 