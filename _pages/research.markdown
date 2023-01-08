---
layout: default
title:  "Research"
permalink: /research/
---

## Current Research Interests

My current research spans simulation analysis and deep learning.  Incorporating HACC into the YT analysis framework enables simple Pythonic simulation analysis by non-experts, and allows quick iteration and validation by experts.  Now we can visualize stars and the galaxies identified in-situ:
![HACC galaxy](/assets/img/190203-core-mapped_Particle_z_particle_mass.png)

If we really want to showboat, we could also do a 3D projection using [napari](https://napari.org/stable) that includes gas density (blue), temperature (red-fuscia), and stars (white):
![HACC 3D](/assets/img/multichannel-stars_napari.png)

Within the realm of deep learning, I am using deep convolutional neural networks to create data-driven models of the ionizing ultraviolet background of the universe at intermediate redshifts.  Since current models assume a uniform background radiation, improving the model to have varying ionization and heating rates dependent on local variables would be a vast improvement.  

Prior work applying generative models to cosmology required the network model to generate the entire volume in one prediction.  This is somewhat useful, but the volumes created are extremely limited by having to create the whole thing in one forward pass through the network.  I am evaluating methods to incrementally create these volumes, enabling much larger volumes to be created by generative networks.

For my past research, check out the [Resume](/resume/)