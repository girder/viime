---
title: 'Viime: Visualization and Integration of Metabolomics Experiments'
tags:
  - metabolomics
  - visualization
  - web application
authors:
  - name: Thomas O'Connell
    affiliation: 1
  - name: Lilian Golzarri Arroyo
    affiliation: 1
  - name: Jun Wan
    affiliation: 1
  - name: Daniel Raftery
    affiliation: 2
  - name: Jon Beezley
    affiliation: 3
  - name: Brandon Davis
    affiliation: 3
  - name: Roni Choudhury
    affiliation: 3
  - name: Samuel Gratzl
    affiliation: 3
  - name: Jeff Baumes
    affiliation: 3
  - name: Jared Tomeck
    affiliation: 3
affiliations:
  - name: Indiana University
    index: 1
  - name: University of Washington
    index: 2
  - name: Kitware Inc.
    index: 3
date: 11 March 2020
bibliography: paper.bib

---

# Summary

Metabolomics involves the comprehensive measurement of metabolites from a
biological system. The resulting metabolite profiles are influenced by genetics,
lifestyle, diet and environment and therefore provides a more holistic
biological readout of the pathological condition of the organism [@beger:2016;
@wishart:2016]. The challenge for metabolomics is that no single analytical
platform can provide a truly comprehensive coverage of the metabolome. The most
commonly used platforms are based on mass-spectrometry (MS) and nuclear magnetic
resonance (NMR) methods. Investigators are increasingly using both methods to
increase the metabolite coverage. The challenge for this type of multi-platform
approach is that the data structure may be very different in these two
platforms. For example, NMR data may be reported as a list of spectral features
e.g. bins or peaks with arbitrary intensity units or more directly with named
metabolites reported in concentration units ranging from micromolar to
millimolar. Some MS approaches can also provide data in the form of identified
metabolite concentrations, but given the superior sensitivity of MS, the
concentrations can be several orders of magnitude lower than for NMR. Other MS
approaches yield data in the form of arbitrary response units where the dynamic
range can be more than 6 orders of magnitude. Given the diversity of data
structures (i.e. magnitude and dynamic range) integrating the data from multiple
platforms can be challenging.  This often leads investigators to analyze the
datasets separately which prevents the observation of potentially interesting
correlations between metabolites detected on different platforms.  Viime is an
open-source, web-based application designed to integrate metabolomics data from
multiple platforms. The workflow of Viime for data ingestion, pretreatment, data
fusion and visualization is shown in Figure 1.

TODO: create and insert Figure 1 (showing cleanup steps)

# User Interface

# Backend Processing

# Future Work
